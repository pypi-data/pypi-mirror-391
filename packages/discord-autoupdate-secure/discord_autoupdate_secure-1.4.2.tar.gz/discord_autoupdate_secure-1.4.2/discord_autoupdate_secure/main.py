#!/usr/bin/env python3
import base64
import binascii
import hashlib
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from tkinter import Tk, messagebox
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

import requests

# URL for the Discord Linux .deb package
DISCORD_API_URL = "https://discord.com/api/download?platform=linux&format=deb"
TRUSTED_DOMAINS = ("discord.com", "discordapp.com", "discordapp.net")
REQUEST_TIMEOUT = 15
DOWNLOAD_CHUNK_SIZE = 1024 * 1024
MANAGED_DESKTOP_COMMENT = "# Managed by discord-autoupdate-secure\n"
DESKTOP_FILE_NAME = "discord.desktop"
DEFAULT_DESKTOP_TEMPLATE = """[Desktop Entry]
Name=Discord
Comment=All-in-one voice and text chat
Exec={exec_path}
Icon=discord
Terminal=false
Type=Application
Categories=Network;InstantMessaging;
StartupWMClass=discord
"""


@dataclass
class DownloadMetadata:
    version: str
    url: str
    hash_algorithm: str
    hash_value: str


def get_installed_version():
    """
    Retrieves the currently installed version of Discord using dpkg.
    Returns the version string or None if Discord is not installed.
    """
    try:
        output = subprocess.check_output(
            ["dpkg", "-s", "discord"], text=True, stderr=subprocess.DEVNULL
        )
        for line in output.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return None

def _is_trusted_host(url: str) -> bool:
    hostname = urlparse(url).hostname or ""
    hostname = hostname.lower()
    return any(
        hostname == domain or hostname.endswith(f".{domain}") for domain in TRUSTED_DOMAINS
    )


def _extract_version_from_url(url: str) -> Optional[str]:
    match = re.search(r"/(\d+\.\d+\.\d+)/", url)
    if match:
        return match.group(1)
    return None


def _parse_expected_hash(resp: requests.Response) -> Optional[Tuple[str, str]]:
    header = resp.headers.get("x-goog-hash")
    if header:
        for part in header.split(","):
            part = part.strip()
            if part.startswith("md5="):
                try:
                    decoded = base64.b64decode(part.split("=", 1)[1])
                    return "md5", decoded.hex()
                except (binascii.Error, ValueError):
                    break
    etag = resp.headers.get("etag")
    if etag:
        etag = etag.strip('"')
        if re.fullmatch(r"[a-fA-F0-9]{32}", etag):
            return "md5", etag.lower()
    return None


def get_latest_metadata() -> Optional[DownloadMetadata]:
    """
    Retrieves trusted metadata about the latest Discord release.
    Ensures redirects resolve to Discord-controlled domains and collects a checksum.
    """
    try:
        resp = requests.head(DISCORD_API_URL, allow_redirects=True, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        if not _is_trusted_host(resp.url):
            print(f"{ANSI_RED}[X]{ANSI_RESET} Refusing untrusted download host: {resp.url}")
            return None
        version = _extract_version_from_url(resp.url)
        if not version:
            print(f"{ANSI_RED}[X]{ANSI_RESET} Could not parse version from Discord download URL.")
            return None
        hash_info = _parse_expected_hash(resp)
        if not hash_info:
            print(f"{ANSI_RED}[X]{ANSI_RESET} Discord download response lacked a checksum header.")
            return None
        algo, value = hash_info
        return DownloadMetadata(version=version, url=resp.url, hash_algorithm=algo, hash_value=value)
    except requests.exceptions.RequestException as exc:
        print(f"{ANSI_RED}[X]{ANSI_RESET} Failed to contact Discord for metadata: {exc}")
    return None

def _download_package(metadata: DownloadMetadata, destination: str) -> bool:
    hasher = hashlib.new(metadata.hash_algorithm)
    try:
        with requests.get(metadata.url, stream=True, timeout=REQUEST_TIMEOUT) as resp:
            resp.raise_for_status()
            if not _is_trusted_host(resp.url):
                print(f"{ANSI_RED}[X]{ANSI_RESET} Refusing to download from untrusted host: {resp.url}")
                return False
            with open(destination, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    if not chunk:
                        continue
                    fh.write(chunk)
                    hasher.update(chunk)
    except requests.exceptions.RequestException as exc:
        print(f"{ANSI_RED}[X]{ANSI_RESET} Failed to download Discord: {exc}")
        return False

    calculated = hasher.hexdigest()
    if calculated != metadata.hash_value:
        print(f"{ANSI_RED}[X]{ANSI_RESET} Download checksum mismatch. Aborting install.")
        return False
    return True


def _find_privilege_command() -> Optional[str]:
    for candidate in ("/usr/bin/pkexec", "/usr/bin/sudo"):
        if os.path.exists(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def _sanitized_env() -> Dict[str, str]:
    clean_path = "/usr/sbin:/usr/bin:/sbin:/bin"
    env = {"PATH": clean_path}
    for var in ("LANG", "LC_ALL", "LC_CTYPE"):
        if var in os.environ:
            env[var] = os.environ[var]
    return env

def _user_applications_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME")
    if base:
        base_path = Path(base)
    else:
        base_path = Path.home() / ".local" / "share"
    return base_path / "applications"

def _desktop_source_candidates(user_dir: Path) -> Tuple[Path, ...]:
    return (
        user_dir / "discord.desktop",
        user_dir / "com.discordapp.Discord.desktop",
        Path("/usr/share/applications/discord.desktop"),
        Path("/usr/share/applications/com.discordapp.Discord.desktop"),
        Path("/var/lib/snapd/desktop/applications/discord_discord.desktop"),
    )

def _is_shortcut_managed(target: Path) -> bool:
    try:
        return target.exists() and "discord-autoupdate-secure" in target.read_text()
    except OSError:
        return False

def _resolve_launcher_path() -> Optional[str]:
    entry_point = shutil.which("discord-autoupdate-secure")
    if entry_point:
        return entry_point
    candidate = Path(sys.argv[0])
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    if candidate.exists():
        return str(candidate.resolve())
    return None

def _compose_exec_value(existing_value: str, new_command: str) -> str:
    command = shlex.quote(new_command)
    existing_value = existing_value.strip()
    if not existing_value:
        return command
    try:
        tokens = shlex.split(existing_value, comments=False, posix=True)
    except ValueError:
        return command
    if len(tokens) == 0:
        return command
    suffix_tokens = tokens[1:]
    if not suffix_tokens:
        return command
    quoted_suffix = " ".join(shlex.quote(token) for token in suffix_tokens)
    return f"{command} {quoted_suffix}"

def _rewrite_desktop_entry(content: str, exec_command: str) -> Optional[str]:
    lines = content.splitlines()
    output = []
    in_main_section = False
    replaced = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_main_section = stripped == "[Desktop Entry]"
        if in_main_section and stripped.startswith("Exec="):
            existing_value = line.split("=", 1)[1]
            new_value = _compose_exec_value(existing_value, exec_command)
            output.append(f"Exec={new_value}")
            replaced = True
        else:
            output.append(line)
    if not any(line.strip() == "[Desktop Entry]" for line in output):
        return None
    if not replaced:
        for idx, line in enumerate(output):
            if line.strip() == "[Desktop Entry]":
                output.insert(idx + 1, f"Exec={shlex.quote(exec_command)}")
                replaced = True
                break
    rewritten = "\n".join(output).rstrip() + "\n"
    if not rewritten.startswith(MANAGED_DESKTOP_COMMENT):
        rewritten = MANAGED_DESKTOP_COMMENT + rewritten
    return rewritten

def _load_reference_desktop_entry(user_dir: Path) -> Optional[str]:
    for candidate in _desktop_source_candidates(user_dir):
        try:
            if candidate.exists():
                return candidate.read_text()
        except OSError:
            continue
    return None

def _backup_existing_file(target: Path) -> Optional[Path]:
    try:
        backup = target.with_suffix(target.suffix + ".bak")
        counter = 1
        while backup.exists():
            backup = target.with_suffix(target.suffix + f".bak{counter}")
            counter += 1
        target.rename(backup)
        return backup
    except OSError:
        return None

def _refresh_desktop_database(applications_dir: Path) -> None:
    updater = shutil.which("update-desktop-database")
    if not updater:
        return
    try:
        subprocess.run([updater, str(applications_dir)], check=False)
    except Exception:
        pass

class BootstrapError(RuntimeError):
    """Raised when the desktop bootstrap process cannot complete."""
    pass


def bootstrap_shortcut(*, force: bool = False, quiet: bool = False) -> bool:
    """
    Ensure the Discord desktop entry points to this tool.
    Returns True if the entry was created or updated.
    """
    applications_dir = _user_applications_dir()
    applications_dir.mkdir(parents=True, exist_ok=True)
    target_path = applications_dir / DESKTOP_FILE_NAME

    if not force and _is_shortcut_managed(target_path):
        if not quiet:
            print(f"{ANSI_GREEN}[OK]{ANSI_RESET} Discord desktop shortcut is already managed: {target_path}")
        return False

    launcher_path = _resolve_launcher_path()
    if not launcher_path:
        raise BootstrapError("Could not determine launcher path for discord-autoupdate-secure.")

    source_content = _load_reference_desktop_entry(applications_dir)
    if source_content:
        rewritten = _rewrite_desktop_entry(source_content, launcher_path)
    else:
        body = DEFAULT_DESKTOP_TEMPLATE.format(exec_path=shlex.quote(launcher_path)).strip()
        rewritten = f"{MANAGED_DESKTOP_COMMENT}{body}\n"
    if rewritten is None:
        body = DEFAULT_DESKTOP_TEMPLATE.format(exec_path=shlex.quote(launcher_path)).strip()
        rewritten = f"{MANAGED_DESKTOP_COMMENT}{body}\n"

    backup_note = None
    if target_path.exists() and not _is_shortcut_managed(target_path):
        backup_path = _backup_existing_file(target_path)
        if backup_path:
            backup_note = f"{ANSI_BLUE}[BK]{ANSI_RESET} Existing desktop entry backed up to {backup_path}"
        else:
            backup_note = f"{ANSI_YELLOW}[!]{ANSI_RESET} Unable to back up existing desktop entry; overwriting."

    try:
        target_path.write_text(rewritten)
        target_path.chmod(0o644)
    except OSError as exc:
        raise BootstrapError(f"Failed to write desktop entry: {exc}") from exc

    _refresh_desktop_database(applications_dir)

    if not quiet:
        if backup_note:
            print(backup_note)
        print(f"{ANSI_GREEN}[OK]{ANSI_RESET} Discord desktop shortcut now routes through discord-autoupdate-secure: {target_path}")
        print(f"{ANSI_CYAN}[i]{ANSI_RESET} Log out/in or re-open your application menu if the change is not immediately visible.")
    return True

def ensure_discord_installed_for_bootstrap() -> bool:
    installed = get_installed_version()
    if installed:
        return True
    print(f"{ANSI_CYAN}[i]{ANSI_RESET} Discord is not installed; installing latest release before bootstrapping.")
    metadata = get_latest_metadata()
    if metadata is None:
        print(f"{ANSI_RED}[X]{ANSI_RESET} Cannot bootstrap without trusted Discord metadata.")
        return False
    update_discord(metadata, is_interactive=False)
    return get_installed_version() is not None



def update_discord(metadata: Optional[DownloadMetadata], is_interactive=False):
    """
    Downloads and installs the latest Discord .deb package.
    Uses pkexec for privilege escalation if available, otherwise falls back to sudo.
    """
    if metadata is None:
        print(f"{ANSI_RED}[X]{ANSI_RESET} Cannot update Discord without trusted metadata.")
        return

    if is_interactive:
        Tk().wm_withdraw() # Hides the main Tkinter window
        message = "A new version of Discord is available. Do you want to update now?"
        if not messagebox.askyesno("Discord Updater", message):
            print(f"{ANSI_RED}[X]{ANSI_RESET} Update canceled by user.")
            return

    # Check for pkexec and build the command accordingly
    privilege_cmd = _find_privilege_command()
    if not privilege_cmd:
        print(f"{ANSI_RED}[X]{ANSI_RESET} Could not find 'pkexec' or 'sudo' for installation. Aborting.")
        sys.exit(1)

    with tempfile.NamedTemporaryFile(suffix=".deb", delete=False) as tmp_file:
        tmp_path = tmp_file.name

    print(f"{ANSI_BLUE}[↓]{ANSI_RESET} Downloading latest Discord...")
    if not _download_package(metadata, tmp_path):
        os.remove(tmp_path)
        return
    print(f"{ANSI_GREEN}[OK]{ANSI_RESET} Download complete and verified.")

    print(f"{ANSI_BLUE}[*]{ANSI_RESET} Installing...")
    try:
        subprocess.run(
            [privilege_cmd, "dpkg", "-i", tmp_path],
            check=True,
            env=_sanitized_env(),
        )
    except subprocess.CalledProcessError:
        print(f"{ANSI_RED}[X]{ANSI_RESET} dpkg installation failed. Attempting to fix dependencies...")
        subprocess.run(
            [privilege_cmd, "apt-get", "-f", "-y", "install"],
            check=True,
            env=_sanitized_env(),
        )

    os.remove(tmp_path)
    print(f"{ANSI_GREEN}[OK]{ANSI_RESET} Discord updated.")

def run_discord():
    """
    Starts Discord if it is not already running.
    """
    # Check if Discord is already running
    try:
        subprocess.check_output(["pgrep", "-x", "Discord"])
        print(f"{ANSI_BLUE}[>]{ANSI_RESET} Discord is already running.")
        return
    except subprocess.CalledProcessError:
        pass

    # Find the Discord executable in PATH
    discord_cmd = shutil.which("discord") or shutil.which("Discord")
    if not discord_cmd:
        print(f"{ANSI_RED}[X]{ANSI_RESET} Could not find Discord executable.")
        return

    print(f"{ANSI_BLUE}[>]{ANSI_RESET} Starting Discord...")
    subprocess.Popen([discord_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Automatically update and run Discord on Debian-based systems."
    )
    parser.add_argument("--update", action="store_true", help="Only update Discord, do not run.")
    parser.add_argument("--check", action="store_true", help="Show installed and latest Discord version without updating or running.")
    parser.add_argument(
        "--bootstrap",
        action="store_true",
        help="Replace the Discord desktop shortcut so it launches discord-autoupdate-secure first.",
    )
    args = parser.parse_args()

    if args.bootstrap:
        try:
            if not ensure_discord_installed_for_bootstrap():
                print(f"{ANSI_RED}[X]{ANSI_RESET} Bootstrap requires Discord to be installed. Aborting.")
                sys.exit(1)
            bootstrap_shortcut(force=True)
        except BootstrapError as exc:
            print(f"{ANSI_RED}[X]{ANSI_RESET} {exc}")
            sys.exit(1)
        return

    installed = get_installed_version()
    metadata = get_latest_metadata()
    latest = metadata.version if metadata else None

    print(f"Installed version: {installed or 'not installed'}")
    print(f"Latest version:    {latest or 'unknown'}")

    if args.check:
        return

    if metadata is None:
        print(f"{ANSI_YELLOW}[!]{ANSI_RESET} Unable to determine the latest Discord release; skipping update.")
    else:
        is_update_needed = installed != latest
        if is_update_needed:
            update_discord(metadata, is_interactive=True)
        else:
            print(f"{ANSI_GREEN}[OK]{ANSI_RESET} Discord is up to date.")

    if not args.update:
        run_discord()

if __name__ == "__main__":
    main()
ANSI_RESET = "\033[0m"
ANSI_GREEN = "\033[32m"
ANSI_RED = "\033[31m"
ANSI_YELLOW = "\033[33m"
ANSI_BLUE = "\033[34m"
ANSI_CYAN = "\033[36m"
