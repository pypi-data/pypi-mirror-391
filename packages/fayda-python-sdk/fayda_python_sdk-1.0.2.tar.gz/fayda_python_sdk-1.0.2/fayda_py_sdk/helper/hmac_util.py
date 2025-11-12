"""HMAC utility"""

import hmac
import hashlib


def digest_as_plain_text(data: bytes) -> str:
    """Calculate SHA-256 digest and return as uppercase hex string"""
    return hashlib.sha256(data).hexdigest().upper()


def hmac_sha256(key: bytes, data: bytes) -> bytes:
    """Calculate HMAC-SHA256"""
    return hmac.new(key, data, hashlib.sha256).digest()

