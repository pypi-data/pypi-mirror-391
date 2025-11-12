"""
Python IDA SDK - Reusable IDA Client Library for OTP, Authentication and eKYC
"""

__version__ = "1.0.1"

from .client.ekyc_client import EkycClient
from .client.ekyc_client_config import EkycClientConfig
from .config.config_builder import ConfigBuilder

__all__ = ["EkycClient", "EkycClientConfig", "ConfigBuilder"]

