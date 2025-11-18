"""Base authentication request DTO"""

from dataclasses import dataclass


@dataclass
class BaseAuthRequestDTO:
    """Base class for authentication requests"""
    id: str = None
    version: str = None

