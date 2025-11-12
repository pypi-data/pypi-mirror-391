"""Biometric identity info DTO"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BioIdentityInfoDTO:
    """Biometric identity information"""
    data: Optional[str] = None
    bio_type: Optional[str] = None
    bio_sub_type: Optional[str] = None
    device_provider_id: Optional[str] = None
    device_provider: Optional[str] = None
    device_code: Optional[str] = None
    timestamp: Optional[str] = None

