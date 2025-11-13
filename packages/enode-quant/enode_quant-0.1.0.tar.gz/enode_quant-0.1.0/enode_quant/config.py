import os
import json
from pathlib import Path

from enode_quant.errors import MissingCredentialsError

# Folder: ~/.enode_quant/
CONFIG_DIR = Path.home() / ".enode_quant"
CONFIG_FILE = CONFIG_DIR / "credentials.json"


def set_credentials(api_url: str, api_key: str) -> None:
    """
    Write API credentials to ~/.enode_quant/credentials.
    Creates the folder if it does not exist.
    Overwrites existing credentials safely.
    """

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "api_url": api_url.strip(),
        "api_key": api_key.strip(),
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

    # Restrict permissions (0600: user read/write only)
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except Exception:
        # Not critical if chmod fails (Windows, etc.)
        pass


def delete_credentials() -> None:
    """
    Remove the credentials file (used by `enode logout`).
    """
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


def _load_credentials() -> dict:
    """
    Lower-level helper to load credentials from disk.
    Raises MissingCredentialsError if file is missing or invalid.
    """
    if not CONFIG_FILE.exists():
        raise MissingCredentialsError("No credentials found. Run `enode login` first.")

    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise MissingCredentialsError(
            "Credentials file is corrupted. Run `enode login` again."
        ) from e
    if not isinstance(data.get("api_url"), str) or not isinstance(data.get("api_key"), str):
        raise MissingCredentialsError("Invalid credentials file. Run `enode login` again.")


    return data


def get_api_url() -> str:
    """
    Return the stored API URL.
    """
    return _load_credentials()["api_url"]


def get_api_key() -> str:
    """
    Return the stored API key.
    """
    return _load_credentials()["api_key"]


def ensure_credentials_exist() -> None:
    """
    Used by commands like `enode whoami` to ensure the user is logged in.
    Raises MissingCredentialsError if credentials are absent.
    """
    _ = _load_credentials()
