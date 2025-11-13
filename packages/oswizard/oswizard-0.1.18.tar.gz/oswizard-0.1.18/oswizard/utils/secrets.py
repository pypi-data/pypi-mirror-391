from __future__ import annotations
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
import os
import yaml

ENC_PREFIX = "ENC::"
KEY_FILENAME = ".key"  # stored in your workspace root (e.g., osw-work/.key)


def key_path_for(machines_file: Path) -> Path:
    """Derive key path from machines.yml location (../.key)."""
    return machines_file.parent / KEY_FILENAME


def ensure_key(keyfile: Path) -> bytes:
    """Create a new Fernet key if missing; return key bytes."""
    keyfile.parent.mkdir(parents=True, exist_ok=True)
    if not keyfile.exists():
        key = Fernet.generate_key()
        keyfile.write_bytes(key)
        os.chmod(keyfile, 0o600)
        return key
    return keyfile.read_bytes()


def load_key(keyfile: Path) -> bytes:
    """Load an existing key (raises if missing)."""
    if not keyfile.exists():
        raise FileNotFoundError(f"Key not found: {keyfile}")
    return keyfile.read_bytes()


def is_encrypted(value: str | None) -> bool:
    return isinstance(value, str) and value.startswith(ENC_PREFIX)


def encrypt_str(key: bytes, plaintext: str) -> str:
    token = Fernet(key).encrypt(plaintext.encode("utf-8"))
    return ENC_PREFIX + token.decode("utf-8")


def decrypt_str(key: bytes, value: str) -> str:
    if not is_encrypted(value):
        return value
    token = value[len(ENC_PREFIX) :].encode("utf-8")
    try:
        return Fernet(key).decrypt(token).decode("utf-8")
    except InvalidToken:
        raise ValueError("Invalid encryption token or wrong key")


# -------- new helpers --------


def load_effective_key(
    machines_file: Path, override: Optional[Path] = None
) -> Optional[bytes]:
    """
    Load a key for decrypting machines.yml.
    Priority:
      1) override path argument
      2) OSW_KEY env var
      3) <ws>/.key beside machines.yml
    Returns None if no key found.
    """
    if override:
        return load_key(override)
    env_path = os.getenv("OSW_KEY")
    if env_path:
        return load_key(Path(env_path))
    kp = key_path_for(machines_file)
    if kp.exists():
        return load_key(kp)
    return None


def rotate_passwords_inplace(
    machines_file: Path, old_key: bytes, new_key: bytes
) -> int:
    """
    Re-encrypt all password fields: ENC(old_key, ...) -> ENC(new_key, ...).
    Returns count of changed entries.
    """
    data = yaml.safe_load(machines_file.read_text()) or []
    changed = 0
    for m in data:
        pwd = m.get("password", "")
        if is_encrypted(pwd):
            # decrypt with old, re-encrypt with new
            plain = decrypt_str(old_key, pwd)
            m["password"] = encrypt_str(new_key, plain)
            changed += 1
        elif pwd:
            # plaintext → encrypt with new
            m["password"] = encrypt_str(new_key, pwd)
            changed += 1
    machines_file.write_text(yaml.safe_dump(data))
    return changed
