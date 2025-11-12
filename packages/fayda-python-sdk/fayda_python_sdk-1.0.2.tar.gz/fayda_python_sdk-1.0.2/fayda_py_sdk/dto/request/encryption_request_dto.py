"""Encryption request DTO"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class EncryptionRequestDto:
    """Encryption request DTO"""
    identity_request: Optional[Dict[str, Any]] = None

