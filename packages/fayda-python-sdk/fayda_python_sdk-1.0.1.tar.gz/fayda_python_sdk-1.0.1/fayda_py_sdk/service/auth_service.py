"""Authentication service"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any
import requests
from urllib.parse import urlencode
import hashlib
import base64

from ..dto.request.auth_request_dto import AuthRequestDTO
from ..dto.request.request_dto import RequestDTO
from ..dto.request.encryption_request_dto import EncryptionRequestDto
from ..dto.response.encryption_response_dto import EncryptionResponseDto
from ..constants.auth_constants import AUTH_REQUEST_ID, EKYC_REQUEST_ID
from ..helper.crypto_utility import CryptoUtility
from ..helper.crypto_core import CryptoCore
from ..helper.hmac_util import digest_as_plain_text
from ..util.signature_util import SignatureUtil
from ..util.key_mgr_util import KeyMgrUtil
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service"""

    def __init__(self, config: Dict[str, Any], signature_util: SignatureUtil,
                 key_mgr_util: KeyMgrUtil, crypto_utility: CryptoUtility):
        self.config = config
        self.signature_util = signature_util
        self.key_mgr_util = key_mgr_util
        self.crypto_utility = crypto_utility
        self.crypto_core = CryptoCore()

    def authenticate(self, auth_request_dto: AuthRequestDTO) -> Dict[str, Any]:
        """Perform authentication"""
        auth_request_dto.request_time = self._get_utc_current_datetime_iso_string()
        auth_request_dto.transaction_id = "1234567890"
        
        is_ekyc = (auth_request_dto.requested_auth is not None and
                   auth_request_dto.requested_auth.demo)
        auth_request_dto.id = EKYC_REQUEST_ID if is_ekyc else AUTH_REQUEST_ID
        auth_request_dto.version = "1.0"
        auth_request_dto.consent_obtained = True

        request_dto = auth_request_dto.request
        if request_dto is None:
            request_dto = RequestDTO()
            auth_request_dto.request = request_dto
        
        request_dto.timestamp = self._get_utc_current_datetime_iso_string()
        request_dto.otp = auth_request_dto.otp
        
        identity_block = {
            "otp": request_dto.otp,
            "timestamp": request_dto.timestamp,
            "demographics": request_dto.demographics,
            "biometrics": request_dto.biometrics
        }
        identity_block = {k: v for k, v in identity_block.items() if v is not None}

        encryption_request_dto = EncryptionRequestDto()
        encryption_request_dto.identity_request = identity_block
        kernel_encrypt = self._kernel_encrypt(encryption_request_dto, False)

        auth_request_dto.thumbprint = kernel_encrypt.thumbprint
        auth_request_map = auth_request_dto.to_dict()
        auth_request_map["request"] = kernel_encrypt.encrypted_identity
        auth_request_map["requestSessionKey"] = kernel_encrypt.encrypted_session_key
        auth_request_map["requestHMAC"] = kernel_encrypt.request_hmac

        req_json = json.dumps(auth_request_map)

        headers = {
            "signature": self.get_signature(req_json),
            "Content-Type": "application/json"
        }

        url = (self.config.get("ida.ekyc.url") if is_ekyc
               else self.config.get("ida.auth.url"))

        try:
            session = self._create_session()
            response = session.post(url, json=auth_request_map, headers=headers, verify=self.config.get("ida.ssl.verify", False))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[Auth] Failed to call authentication endpoint: {url}", exc_info=True)
            raise RuntimeError("Authentication request failed") from e

    def _kernel_encrypt(self, encryption_request_dto: EncryptionRequestDto, is_internal: bool) -> EncryptionResponseDto:
        """Kernel encryption"""
        encryption_response_dto = EncryptionResponseDto()
        identity_block = json.dumps(encryption_request_dto.identity_request, separators=(',', ':'))

        secret_key = self.crypto_utility.gen_sec_key()

        encrypted_identity_block = self.crypto_utility.symmetric_encrypt(
            identity_block.encode('utf-8'), secret_key)
        encryption_response_dto.encrypted_identity = base64.urlsafe_b64encode(
            encrypted_identity_block).decode('utf-8').rstrip('=')

        certificate = self._get_certificate_for_encryption(identity_block, is_internal)
        public_key = certificate.public_key()

        encrypted_session_key_byte = self.crypto_utility.asymmetric_encrypt(
            secret_key, public_key)
        encryption_response_dto.encrypted_session_key = base64.urlsafe_b64encode(
            encrypted_session_key_byte).decode('utf-8').rstrip('=')

        identity_bytes = identity_block.encode('utf-8')
        hmac_digest = digest_as_plain_text(identity_bytes)
        hmac_digest_bytes = hmac_digest.encode('utf-8')
        byte_arr = self.crypto_utility.symmetric_encrypt(
            hmac_digest_bytes, secret_key)
        encryption_response_dto.request_hmac = base64.urlsafe_b64encode(
            byte_arr).decode('utf-8').rstrip('=')

        thumbprint_bytes = self._get_certificate_thumbprint(certificate)
        thumbprint = base64.urlsafe_b64encode(thumbprint_bytes).decode('utf-8').rstrip('=')
        encryption_response_dto.thumbprint = thumbprint
        return encryption_response_dto

    def _get_certificate_thumbprint(self, cert) -> bytes:
        """Get certificate thumbprint (SHA-256)"""
        cert_der = cert.public_bytes(encoding=serialization.Encoding.DER)
        return hashlib.sha256(cert_der).digest()

    def _get_certificate_for_encryption(self, data: str, is_internal: bool):
        """Get certificate for encryption"""
        response = self.get_certificate("IDA", self.config.get("ida.reference.id", "PARTNER"))
        certificate_str = response.get("certificate")
        certificate_trimmed = self._trim_begin_end(certificate_str)
        cert_bytes = base64.b64decode(certificate_trimmed)
        return x509.load_der_x509_certificate(cert_bytes, default_backend())

    @staticmethod
    def _trim_begin_end(p_key: str) -> str:
        """Trim BEGIN and END markers from certificate"""
        import re
        s = re.sub(r"-*BEGIN([^-]*)-*(\r?\n)?", "", p_key)
        s = re.sub(r"-*END([^-]*)-*(\r?\n)?", "", s)
        s = re.sub(r"\s", "", s)
        return s

    def get_certificate(self, application_id: str, reference_id: str) -> Dict[str, Any]:
        """Get certificate from server"""
        url = self.config.get("ida.certificate.url")
        params = {
            "applicationId": application_id,
            "referenceId": reference_id
        }
        full_url = f"{url}?{urlencode(params)}"

        try:
            session = self._create_session()
            response = session.get(full_url, verify=self.config.get("ida.ssl.verify", False))
            response.raise_for_status()
            data = response.json()
            
            if not data or "response" not in data:
                raise RuntimeError("Invalid certificate response")
            
            return data["response"]
        except Exception as e:
            logger.error(f"[Cert] Failed to get certificate: {e}")
            raise

    def get_signature(self, req_json: str) -> str:
        """Get signature for request JSON"""
        partner_id = self.config.get("partnerId", "mpartner-tech5-lora")
        key_dir = self.key_mgr_util.get_keys_dir_path()
        return self.signature_util.sign(
            req_json, False, True, False, None, key_dir, partner_id)

    def _create_session(self) -> requests.Session:
        """Create requests session with auth token"""
        session = requests.Session()
        auth_token = self._generate_auth_token()
        if auth_token:
            session.headers.update({
                "Cookie": f"Authorization={auth_token}",
                "Authorization": f"Bearer {auth_token}"
            })
        
        if not self.config.get("ida.ssl.verify", False):
            session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        return session

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
