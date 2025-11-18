"""eKYC client configuration"""

from typing import Dict, Any
from .ekyc_client import EkycClient
from ..service.auth_service import AuthService
from ..service.ekyc_service import EkycService
from ..service.otp_service import OtpService


class EkycClientConfig:
    """Configuration class for EkycClient"""

    @staticmethod
    def create_ekyc_client(
            auth_service: AuthService,
            otp_service: OtpService,
            ekyc_service: EkycService
    ) -> EkycClient:
        """Create and configure EkycClient instance"""
        return EkycClient(auth_service, otp_service, ekyc_service)

