"""Security, cryptographic hashing, AES-256-GCM vault, and CEO authentication."""

import base64
import hashlib
import json
import os
import secrets
from typing import Any, Dict, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import Header, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.config import settings


api_key_header = APIKeyHeader(name="X-CEO-Key", auto_error=False)


def get_encryption_key() -> bytes:
    """Derive or load 32-byte AES key."""
    if settings.ENCRYPTION_KEY_32BYTES_BASE64:
        return base64.b64decode(settings.ENCRYPTION_KEY_32BYTES_BASE64)
    # Derive deterministic key from SECRET_KEY using SHA-256
    return hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()


def encrypt_token(plaintext: str) -> str:
    """Encrypt a plaintext OAuth or secret token using AES-256-GCM."""
    key = get_encryption_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    # Combine nonce + ciphertext and base64 encode
    payload = nonce + ciphertext
    return base64.b64encode(payload).decode("utf-8")


def decrypt_token(encoded: str) -> str:
    """Decrypt an AES-256-GCM ciphertext."""
    key = get_encryption_key()
    aesgcm = AESGCM(key)
    raw = base64.b64decode(encoded.encode("utf-8"))
    nonce = raw[:12]
    ciphertext = raw[12:]
    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
    return decrypted.decode("utf-8")


def canonical_json_hash(payload: Any) -> str:
    """Compute a deterministic, canonical SHA-256 hash of any JSON payload."""
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception:
            pass
    canonical_str = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()


async def verify_ceo_auth(x_ceo_key: Optional[str] = Security(api_key_header)) -> bool:
    """Authenticate CEO commands from Android client or local loopback."""
    # Loopback dev mode check or valid token check
    if not x_ceo_key:
        # In strict mode, reject without key
        if settings.APP_ENV == "production":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="CEO Authorization Key (X-CEO-Key) is missing.",
            )
        return True  # Permissive loopback dev default

    if not secrets.compare_digest(x_ceo_key, settings.CEO_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CEO authorization key.",
        )
    return True
