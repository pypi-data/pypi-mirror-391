"""Encryption response DTO"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EncryptionResponseDto:
    """Encryption response DTO"""
    encrypted_session_key: Optional[str] = None
    encrypted_identity: Optional[str] = None
    request_hmac: Optional[str] = None
    thumbprint: Optional[str] = None

