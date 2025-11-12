"""eKYC client"""

import logging
import json
from typing import Dict, Any

from ..dto.request.auth_request_dto import AuthRequestDTO, AuthTypeDTO
from ..dto.request.otp_request_dto import OtpRequestDTO
from ..service.auth_service import AuthService
from ..service.ekyc_service import EkycService
from ..service.otp_service import OtpService

logger = logging.getLogger(__name__)


class EkycClient:
    """eKYC client class"""

    def __init__(self, auth_service: AuthService, otp_service: OtpService, ekyc_service: EkycService):
        self.auth_service = auth_service
        self.otp_service = otp_service
        self.ekyc_service = ekyc_service

    def request_otp(self, otp_request_dto: OtpRequestDTO) -> Dict[str, Any]:
        """Request an OTP for a user"""
        try:
            logger.debug(f"Requesting OTP: {json.dumps(otp_request_dto.to_dict())}")
            return self.otp_service.request_otp(otp_request_dto)
        except Exception as e:
            logger.error("Failed to request OTP", exc_info=True)
            raise RuntimeError("Failed to request OTP") from e

    def yes_no_auth(self, auth_request_dto: AuthRequestDTO) -> Dict[str, Any]:
        """Yes/No Auth using OTP"""
        try:
            logger.debug(f"Yes/No Auth: {json.dumps(auth_request_dto.to_dict())}")

            if auth_request_dto.requested_auth is None:
                auth_request_dto.requested_auth = AuthTypeDTO()
            auth_request_dto.requested_auth.otp = True
            auth_request_dto.requested_auth.bio = False

            return self.auth_service.authenticate(auth_request_dto)
        except Exception as e:
            logger.error("Yes/No Auth failed", exc_info=True)
            raise RuntimeError("Yes/No Auth failed") from e

    def perform_ekyc(self, auth_request_dto: AuthRequestDTO) -> Dict[str, Any]:
        """Perform eKYC (OTP + Demographic)"""
        try:
            logger.debug(f"Performing eKYC: {json.dumps(auth_request_dto.to_dict())}")

            if auth_request_dto.requested_auth is None:
                auth_request_dto.requested_auth = AuthTypeDTO()
            auth_request_dto.requested_auth.otp = True
            auth_request_dto.requested_auth.demo = True

            return self.ekyc_service.perform_ekyc(auth_request_dto)
        except Exception as e:
            logger.error("eKYC failed", exc_info=True)
            raise RuntimeError("eKYC failed") from e

