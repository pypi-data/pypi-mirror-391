"""Request DTO"""

from dataclasses import dataclass
from typing import List, Optional
from .bio_identity_info_dto import BioIdentityInfoDTO


@dataclass
class RequestDTO:
    """Request payload DTO"""
    otp: Optional[str] = None
    timestamp: Optional[str] = None
    demographics: Optional[dict] = None  # IdentityDTO
    biometrics: Optional[List[BioIdentityInfoDTO]] = None

