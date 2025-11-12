"""OTP service"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any
import requests

from ..dto.request.otp_request_dto import OtpRequestDTO
from ..constants.auth_constants import OTP_REQUEST_ID, TRANSACTION_ID
from ..service.auth_service import AuthService

logger = logging.getLogger(__name__)


class OtpService:
    """OTP service"""

    def __init__(self, config: Dict[str, Any], auth_service: AuthService):
        self.config = config
        self.auth_service = auth_service

    def request_otp(self, otp_request_dto: OtpRequestDTO) -> Dict[str, Any]:
        """Request OTP"""
        try:
            otp_request_dto.id = OTP_REQUEST_ID
            otp_request_dto.request_time = self._get_utc_current_datetime_iso_string()
            otp_request_dto.transaction_id = TRANSACTION_ID
            otp_request_dto.version = "1.0"

            if not otp_request_dto.otp_channel:
                otp_request_dto.otp_channel = ["email"]

            req_json = json.dumps(otp_request_dto.to_dict())

            headers = {
                "Content-Type": "application/json",
                "signature": self.auth_service.get_signature(req_json)
            }

            auth_token = self._generate_auth_token()
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
                headers["Cookie"] = f"Authorization={auth_token}"

            url = self.config.get("ida.otp.url")
            logger.info(f"[OTP] Sending OTP request to URL: {url}")

            response = requests.post(
                url,
                json=otp_request_dto.to_dict(),
                headers=headers,
                verify=self.config.get("ida.ssl.verify", False)
            )

            return response.json()
        except Exception as e:
            logger.error("[OTP] Failed to request OTP", exc_info=True)
            raise

    def _generate_auth_token(self) -> str:
        """Generate authentication token"""
        try:
            request_body = {
                "clientId": self.config.get("clientId", "default-client"),
                "secretKey": self.config.get("secretKey", "default-secret"),
                "appId": self.config.get("appId", "regproc")
            }

            dt = datetime.now(timezone.utc)
            request_time = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            request = {
                "requesttime": request_time,
                "request": request_body
            }

            headers = {"Content-Type": "application/json"}
            url = self.config.get("ida.authmanager.url")
            response = requests.post(
                url,
                json=request,
                headers=headers,
                verify=self.config.get("ida.ssl.verify", False)
            )

            auth_header = response.headers.get("authorization") or response.headers.get("Authorization")
            if auth_header:
                token = auth_header.replace("Bearer ", "").strip()
                if token:
                    return token
            
            set_cookie_header = response.headers.get("Set-Cookie", "") or response.headers.get("set-cookie", "")
            if isinstance(set_cookie_header, list):
                set_cookie_values = set_cookie_header
            elif set_cookie_header:
                set_cookie_values = [set_cookie_header]
            else:
                set_cookie_values = []
            
            if set_cookie_values:
                for cookie in set_cookie_values:
                    auth_pos = cookie.find("Authorization=")
                    if auth_pos >= 0:
                        token_start = auth_pos + len("Authorization=")
                        token_end = cookie.find(";", token_start)
                        if token_end == -1:
                            token_end = len(cookie)
                        token = cookie[token_start:token_end].strip()
                        if token:
                            return token

            try:
                if response.content:
                    body_json = response.json()
                    if isinstance(body_json, dict):
                        if "token" in body_json:
                            return body_json["token"]
                        if "response" in body_json and isinstance(body_json["response"], dict):
                            if "token" in body_json["response"]:
                                return body_json["response"]["token"]
            except:
                pass

            logger.warning("[Auth] No Authorization token found")
        except Exception as e:
            logger.error("[Auth] Failed to generate auth token", exc_info=True)
        return ""

    def _get_utc_current_datetime_iso_string(self) -> str:
        """Get current UTC datetime as ISO string with Z suffix"""
        dt = datetime.now(timezone.utc)
        iso_str = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        return f"{iso_str}Z"
