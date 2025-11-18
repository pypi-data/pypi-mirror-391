"""Authentication type DTO"""

from dataclasses import dataclass


@dataclass
class AuthTypeDTO:
    """Authentication type specification"""
    demo: bool = False
    bio: bool = False
    otp: bool = False
    pin: bool = False

