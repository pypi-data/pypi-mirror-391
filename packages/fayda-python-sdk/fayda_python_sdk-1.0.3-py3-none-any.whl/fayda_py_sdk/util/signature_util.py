"""Signature utility"""

import logging
import hashlib
import json
import base64
from typing import Optional, Tuple
import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from .key_mgr_util import KeyMgrUtil

logger = logging.getLogger(__name__)


class SignatureUtil:
    """Signature utility class"""

    SIGN_ALGO = "RS256"

    def __init__(self, key_mgr_util: KeyMgrUtil):
        self.key_mgr_util = key_mgr_util

    def sign(self, data_to_sign: str, include_payload: bool, include_certificate: bool,
             include_cert_hash: bool, certificate_url: Optional[str], dir_path: str,
             partner_id: str) -> str:
        """Sign data using RSA private key"""
        try:
            key_entry = self.key_mgr_util.get_key_entry(dir_path, partner_id)
            if key_entry is None:
                raise ValueError(f"Key file not available for partner type: {partner_id}")
            
            private_key, certificate = key_entry
            
            # Get certificate from .cer file if available, otherwise use from p12
            x509_certificate = self.key_mgr_util.get_certificate_entry(dir_path, partner_id)
            if x509_certificate is None:
                x509_certificate = certificate
            
            # Create JWT headers
            headers = {}
            if include_certificate:
                cert_der = x509_certificate.public_bytes(serialization.Encoding.DER)
                cert_b64 = base64.b64encode(cert_der).decode('utf-8')
                headers['x5c'] = [cert_b64]
            
            if include_cert_hash:
                cert_der = x509_certificate.public_bytes(serialization.Encoding.DER)
                thumbprint = hashlib.sha256(cert_der).digest()
                headers['x5t#S256'] = base64.urlsafe_b64encode(thumbprint).decode('utf-8').rstrip('=')
            
            if certificate_url:
                headers['x5u'] = certificate_url
            
            if include_payload:
                token = jwt.encode(
                    {"data": data_to_sign},
                    private_key,
                    algorithm=self.SIGN_ALGO,
                    headers=headers
                )
                return token
            else:
                headers['alg'] = self.SIGN_ALGO
                header_json = json.dumps(headers, separators=(',', ':')).encode('utf-8')
                header_b64 = base64.urlsafe_b64encode(header_json).decode('utf-8').rstrip('=')
                
                payload_bytes = data_to_sign.encode('utf-8')
                payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode('utf-8').rstrip('=')
                
                signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
                
                signature = private_key.sign(
                    signing_input,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                sig_b64 = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
                
                return f"{header_b64}..{sig_b64}"
        except Exception as e:
            logger.error(f"Error signing data: {e}")
            raise

