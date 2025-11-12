"""eKYC service"""

import logging
import json
import base64
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any
import requests
from urllib.parse import urlencode

from ..dto.request.auth_request_dto import AuthRequestDTO
from ..dto.request.request_dto import RequestDTO
from ..dto.request.encryption_request_dto import EncryptionRequestDto
from ..dto.response.encryption_response_dto import EncryptionResponseDto
from ..service.auth_service import AuthService
from ..util.key_mgr_util import KeyMgrUtil
from ..helper.crypto_utility import CryptoUtility
from ..helper.crypto_core import CryptoCore
from ..helper.crypto_util import CryptoUtil
from ..helper.hmac_util import digest_as_plain_text
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

logger = logging.getLogger(__name__)


class EkycService:
    """eKYC service"""

    KEY_SPLITTER = "#KEY_SPLITTER#"

    def __init__(self, config: Dict[str, Any], auth_service: AuthService,
                 key_mgr_util: KeyMgrUtil, crypto_utility: CryptoUtility):
        self.config = config
        self.auth_service = auth_service
        self.key_mgr_util = key_mgr_util
        self.crypto_utility = crypto_utility
        self.crypto_core = CryptoCore()

    def perform_ekyc(self, auth_request_dto: AuthRequestDTO) -> Dict[str, Any]:
        """Perform eKYC"""
        auth_request_dto.request_time = self._get_utc_current_datetime_iso_string()
        if auth_request_dto.transaction_id is None:
            auth_request_dto.transaction_id = "1234567890"
        
        auth_request_dto.id = "mosip.identity.kyc"
        auth_request_dto.version = "1.0"
        auth_request_dto.consent_obtained = True

        request_dto = auth_request_dto.request or RequestDTO()
        if auth_request_dto.request is None:
            auth_request_dto.request = request_dto

        request_dto.otp = auth_request_dto.otp
        request_dto.timestamp = self._get_utc_current_datetime_iso_string()

        identity_block = {
            "otp": request_dto.otp,
            "timestamp": request_dto.timestamp
        }

        encryption_request_dto = EncryptionRequestDto()
        encryption_request_dto.identity_request = identity_block
        encrypted = self._kernel_encrypt(encryption_request_dto, False)

        auth_request_dto.thumbprint = encrypted.thumbprint
        request_map = auth_request_dto.to_dict()
        request_map["request"] = encrypted.encrypted_identity
        request_map["requestSessionKey"] = encrypted.encrypted_session_key
        request_map["requestHMAC"] = encrypted.request_hmac

        req_json = json.dumps(request_map)
        headers = {
            "signature": self.auth_service.get_signature(req_json),
            "Content-Type": "application/json"
        }

        url = self.config.get("ida.ekyc.url")

        try:
            session = self._create_session()
            response = session.post(url, json=request_map, headers=headers,
                                  verify=self.config.get("ida.ssl.verify", False))
            
            try:
                body = response.json()
            except Exception as e:
                logger.error(f"[eKYC] Failed to parse response as JSON: {e}")
                raise
            
            if body is None:
                raise RuntimeError("Empty response from eKYC service")

            if "errors" in body and body.get("errors"):
                errors = body.get("errors", [])
                for error in errors:
                    error_code = error.get("errorCode", "UNKNOWN")
                    error_message = error.get("errorMessage", "No message")
                    logger.error(f"[eKYC] Error {error_code}: {error_message}")

            resp_obj = body.get("response")
            if not isinstance(resp_obj, dict):
                logger.warning("[eKYC] No 'response' object found. Returning raw body.")
                return body

            ekyc = {}
            identity_obj = resp_obj.get("identity")
            
            if isinstance(identity_obj, str):
                try:
                    decrypted = self._decrypt_identity(resp_obj)
                    resp_obj["decryptedIdentity"] = decrypted
                    ekyc["kycStatus"] = resp_obj.get("kycStatus")
                    ekyc["psut"] = resp_obj.get("authToken")
                    ekyc["identity"] = decrypted
                except Exception as ex:
                    logger.error("[eKYC] Failed to decrypt identity", exc_info=True)
                    ekyc["decryptionError"] = str(ex)
            else:
                logger.warning("[eKYC] 'response.identity' not present. Nothing to decrypt.")
                ekyc["errors"] = body.get("errors")
                ekyc["response"] = resp_obj if isinstance(resp_obj, dict) else {}

            return ekyc
        except Exception as e:
            logger.error(f"[eKYC] Failed calling {url}", exc_info=True)
            raise RuntimeError("eKYC request failed") from e

    def _decrypt_identity(self, response_map: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt identity from eKYC response"""
        identity = response_map.get("identity")
        session_key = response_map.get("sessionKey")

        if identity is None:
            raise RuntimeError("No identity field in eKYC response")

        key_dir = self.key_mgr_util.get_keys_dir_path()
        partner_id = self.config.get("partnerId", "mpartner-tech5-lora")
        key_entry = self.key_mgr_util.get_key_entry(key_dir, partner_id)
        if key_entry is None:
            raise RuntimeError("No eKYC key found")

        private_key, certificate = key_entry

        if session_key is None:
            parts = self._split_encrypted_data(identity)
            enc_sec_key = CryptoUtil.decode_url_safe_base64(parts["encryptedSessionKey"])
            enc_kyc_data = CryptoUtil.decode_url_safe_base64(parts["encryptedData"])
        else:
            enc_sec_key = CryptoUtil.decode_url_safe_base64(session_key)
            enc_kyc_data = CryptoUtil.decode_url_safe_base64(identity)

        dec_sec_key = self._decrypt_secret_key(private_key, enc_sec_key)

        nonce = enc_kyc_data[-16:]
        encrypted_kyc_data = enc_kyc_data[:-16]

        aesgcm = AESGCM(dec_sec_key)
        decrypted_bytes = aesgcm.decrypt(nonce, encrypted_kyc_data, None)

        return json.loads(decrypted_bytes.decode('utf-8'))

    def _split_encrypted_data(self, data_url_safe_b64: str) -> Dict[str, str]:
        """Split encrypted data at key splitter"""
        data_bytes = CryptoUtil.decode_url_safe_base64(data_url_safe_b64)
        splitter = self.KEY_SPLITTER.encode('utf-8')
        splits = self._split_at_first_occurrence(data_bytes, splitter)

        return {
            "encryptedSessionKey": CryptoUtil.encode_to_url_safe_base64(splits[0]),
            "encryptedData": CryptoUtil.encode_to_url_safe_base64(splits[1])
        }

    @staticmethod
    def _split_at_first_occurrence(str_bytes: bytes, sep_bytes: bytes) -> tuple:
        """Split bytes at first occurrence of separator"""
        index = EkycService._find_index(str_bytes, sep_bytes)
        if index >= 0:
            first = str_bytes[:index]
            second = str_bytes[index + len(sep_bytes):]
            return (first, second)
        return (str_bytes, b'')

    @staticmethod
    def _find_index(arr: bytes, subarr: bytes) -> int:
        """Find index of subarray in array"""
        for i in range(len(arr) - len(subarr) + 1):
            if arr[i:i+len(subarr)] == subarr:
                return i
        return -1

    def _decrypt_secret_key(self, private_key, enc_key: bytes) -> bytes:
        """Decrypt secret key using RSA-OAEP"""
        oaep_padding = padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
        return private_key.decrypt(enc_key, oaep_padding)

    def _kernel_encrypt(self, dto: EncryptionRequestDto, is_internal: bool) -> EncryptionResponseDto:
        """Kernel encryption"""
        out = EncryptionResponseDto()
        identity_block = json.dumps(dto.identity_request, separators=(',', ':'))

        secret_key = self.crypto_utility.gen_sec_key()
        encrypted_identity = self.crypto_utility.symmetric_encrypt(
            identity_block.encode('utf-8'), secret_key)
        out.encrypted_identity = base64.urlsafe_b64encode(
            encrypted_identity).decode('utf-8').rstrip('=')

        cert = self._get_certificate_for_encryption(identity_block, is_internal)
        enc_session_key = self.crypto_utility.asymmetric_encrypt(
            secret_key, cert.public_key())
        out.encrypted_session_key = base64.urlsafe_b64encode(
            enc_session_key).decode('utf-8').rstrip('=')

        hmac_digest = digest_as_plain_text(identity_block.encode('utf-8'))
        hmac_bytes = self.crypto_utility.symmetric_encrypt(
            hmac_digest.encode('utf-8'), secret_key)
        out.request_hmac = base64.urlsafe_b64encode(
            hmac_bytes).decode('utf-8').rstrip('=')

        thumbprint_bytes = self._get_certificate_thumbprint(cert)
        thumbprint = base64.urlsafe_b64encode(thumbprint_bytes).decode('utf-8').rstrip('=')
        out.thumbprint = thumbprint
        return out

    def _get_certificate_thumbprint(self, cert) -> bytes:
        """Get certificate thumbprint"""
        cert_der = cert.public_bytes(serialization.Encoding.DER)
        return hashlib.sha256(cert_der).digest()

    def _get_certificate_for_encryption(self, data: str, is_internal: bool):
        """Get certificate for encryption"""
        session = self._create_session()
        url = self.config.get("ida.certificate.url")
        params = {
            "applicationId": "IDA",
            "referenceId": self.config.get("ida.reference.id", "PARTNER")
        }
        full_url = f"{url}?{urlencode(params)}"

        response = session.get(full_url, verify=self.config.get("ida.ssl.verify", False))
        response.raise_for_status()
        resp = response.json()
        
        if not resp or "response" not in resp:
            raise RuntimeError("Invalid certificate response")

        certificate_str = resp["response"]["certificate"]
        cert_trimmed = self._trim_begin_end(certificate_str)

        cert_bytes = base64.b64decode(cert_trimmed)
        return x509.load_der_x509_certificate(cert_bytes, default_backend())

    @staticmethod
    def _trim_begin_end(p_key: str) -> str:
        """Trim BEGIN and END markers from certificate"""
        import re
        p_key = re.sub(r"-*BEGIN([^-]*)-*(\r?\n)?", "", p_key)
        p_key = re.sub(r"-*END([^-]*)-*(\r?\n)?", "", p_key)
        p_key = re.sub(r"\s", "", p_key)
        return p_key

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
            body = {
                "clientId": self.config.get("clientId", "default-client"),
                "secretKey": self.config.get("secretKey", "default-secret"),
                "appId": self.config.get("appId", "regproc")
            }

            dt = datetime.now(timezone.utc)
            request_time = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            request = {
                "requesttime": request_time,
                "request": body
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
        except Exception as e:
            logger.error("[Auth] Failed to generate token", exc_info=True)
        return ""

    def _get_utc_current_datetime_iso_string(self) -> str:
        """Get current UTC datetime as ISO string with Z suffix"""
        dt = datetime.now(timezone.utc)
        iso_str = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        return f"{iso_str}Z"
