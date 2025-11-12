"""Configuration builder for IDA SDK"""

import os
from typing import Dict, Any, Optional
from ..service.auth_service import AuthService
from ..service.ekyc_service import EkycService
from ..service.otp_service import OtpService
from ..util.signature_util import SignatureUtil
from ..util.key_mgr_util import KeyMgrUtil
from ..helper.crypto_utility import CryptoUtility
from ..helper.crypto_core import CryptoCore
from ..client.ekyc_client import EkycClient


class ConfigBuilder:
    """Builder class to configure and create EkycClient"""

    def __init__(self):
        self.config: Dict[str, Any] = {}

    def from_dict(self, config: Dict[str, Any]) -> 'ConfigBuilder':
        """Load configuration from dictionary"""
        self.config = config.copy()
        return self

    def from_env(self) -> 'ConfigBuilder':
        """Load configuration from environment variables"""
        self.config = {
            "partnerId": os.getenv("PARTNER_ID", ""),
            "fayda.base.url": os.getenv("FAYDA_BASE_URL", ""),
            "mispLicenseKey": os.getenv("MISP_LICENSE_KEY", ""),
            "partnerApiKey": os.getenv("PARTNER_API_KEY", ""),
            "ida.reference.id": os.getenv("IDA_REFERENCE_ID", "PARTNER"),
            "clientId": os.getenv("CLIENT_ID", ""),
            "secretKey": os.getenv("SECRET_KEY", ""),
            "appId": os.getenv("APP_ID", ""),
            "p12.path": os.getenv("P12_PATH", "keys"),
            "p12.password": os.getenv("P12_PASSWORD", "pass@123"),
            "ida.ssl.verify": os.getenv("IDA_SSL_VERIFY", "false").lower() == "true",
        }
        
        # Build URLs
        base_url = self.config["fayda.base.url"]
        misp_license_key = self.config["mispLicenseKey"]
        partner_id = self.config["partnerId"]
        partner_api_key = self.config["partnerApiKey"]
        
        self.config["ida.otp.url"] = f"{base_url}/idauthentication/v1/otp/{misp_license_key}/{partner_id}/{partner_api_key}"
        self.config["ida.auth.url"] = f"{base_url}/idauthentication/v1/auth/{misp_license_key}/{partner_id}/{partner_api_key}"
        self.config["ida.ekyc.url"] = f"{base_url}/idauthentication/v1/kyc/{misp_license_key}/{partner_id}/{partner_api_key}"
        self.config["ida.certificate.url"] = f"{base_url}/idauthentication/v1/internal/getCertificate"
        self.config["ida.authmanager.url"] = f"{base_url}/v1/authmanager/authenticate/clientidsecretkey"
        
        return self

    def set_config(self, key: str, value: Any) -> 'ConfigBuilder':
        """Set a configuration value"""
        self.config[key] = value
        return self

    def build(self) -> EkycClient:
        """Build and return configured EkycClient"""
        # Initialize utilities
        key_mgr_util = KeyMgrUtil(
            key_path=self.config.get("p12.path", "keys"),
            p12_password=self.config.get("p12.password", "qwerty@123")
        )
        
        signature_util = SignatureUtil(key_mgr_util)
        
        crypto_core = CryptoCore()
        crypto_utility = CryptoUtility(crypto_core)
        
        # Initialize services
        auth_service = AuthService(self.config, signature_util, key_mgr_util, crypto_utility)
        otp_service = OtpService(self.config, auth_service)
        ekyc_service = EkycService(self.config, auth_service, key_mgr_util, crypto_utility)
        
        # Create client
        return EkycClient(auth_service, otp_service, ekyc_service)

