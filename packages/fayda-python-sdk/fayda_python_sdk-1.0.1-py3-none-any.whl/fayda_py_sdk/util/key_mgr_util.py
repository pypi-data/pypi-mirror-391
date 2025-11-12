"""Key management utility"""

import os
import logging
import warnings
from pathlib import Path
from typing import Optional, Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
import base64

logger = logging.getLogger(__name__)

# Suppress cryptography deprecation warnings about certificate serial numbers
warnings.filterwarnings('ignore', category=DeprecationWarning, module='cryptography')


class KeyMgrUtil:
    """Key management utility class"""

    CERTIFICATE_TYPE = "X.509"
    CA_P12_FILE_NAME = "-ca.p12"
    INTER_P12_FILE_NAME = "-inter.p12"
    PARTNER_P12_FILE_NAME = "-partner.p12"
    CA_CER_FILE_NAME = "-ca.cer"
    INTER_CER_FILE_NAME = "-inter.cer"
    PARTNER_CER_FILE_NAME = "-partner.cer"
    TEMP_P12_PWD = "qwerty@123"
    KEY_ALIAS = "keyAlias"
    KEY_STORE = "PKCS12"

    def __init__(self, key_path: str = None, p12_password: str = None):
        self.key_path = key_path or os.getenv("P12_PATH", "keys")
        self.p12_password = p12_password or os.getenv("P12_PASSWORD", self.TEMP_P12_PWD)

    def get_keys_dir_path(self) -> str:
        """Get the keys directory path"""
        return os.path.abspath(self.key_path)

    def get_key_entry(self, dir_path: str, partner_id: str) -> Optional[Tuple[rsa.RSAPrivateKey, x509.Certificate]]:
        """Get private key entry from PKCS12 file"""
        file_prepend = partner_id
        partner_file_path = os.path.join(dir_path, file_prepend + self.PARTNER_P12_FILE_NAME)
        return self._get_private_key_entry(partner_file_path)

    def _get_private_key_entry(self, file_path: str) -> Optional[Tuple[rsa.RSAPrivateKey, x509.Certificate]]:
        """Get private key entry from PKCS12 file"""
        path = Path(file_path)
        if not path.exists():
            return None
        
        try:
            with open(file_path, 'rb') as f:
                p12_data = f.read()
            
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                p12_data,
                self.p12_password.encode('utf-8'),
                backend=default_backend()
            )
            
            if private_key is None or certificate is None:
                return None
            
            return (private_key, certificate)
        except Exception as e:
            logger.error(f"Error loading key entry: {e}")
            return None

    def get_certificate_entry(self, dir_path: str, partner_id: str) -> Optional[x509.Certificate]:
        """Get certificate from .cer file"""
        partner_cert_file_path = os.path.join(dir_path, partner_id + self.PARTNER_CER_FILE_NAME)
        path = Path(partner_cert_file_path)
        if path.exists():
            try:
                cert_data = path.read_text()
                cert_data = self.trim_begin_end(cert_data)
                cert_bytes = base64.b64decode(cert_data)
                return x509.load_der_x509_certificate(cert_bytes, default_backend())
            except Exception as e:
                logger.error(f"Error loading certificate: {e}")
        return None

    @staticmethod
    def trim_begin_end(p_key: str) -> str:
        """Trim BEGIN and END markers from certificate"""
        import re
        p_key = re.sub(r"-*BEGIN([^-]*)-*(\r?\n)?", "", p_key)
        p_key = re.sub(r"-*END([^-]*)-*(\r?\n)?", "", p_key)
        p_key = re.sub(r"\s", "", p_key)
        return p_key

