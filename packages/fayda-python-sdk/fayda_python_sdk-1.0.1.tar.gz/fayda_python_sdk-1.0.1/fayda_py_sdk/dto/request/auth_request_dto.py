"""Authentication request DTO"""

from dataclasses import dataclass, field
from typing import Optional
from .base_auth_request_dto import BaseAuthRequestDTO
from .auth_type_dto import AuthTypeDTO
from .request_dto import RequestDTO


@dataclass
class AuthRequestDTO(BaseAuthRequestDTO):
    """Authentication request DTO"""
    requested_auth: Optional[AuthTypeDTO] = None
    transaction_id: Optional[str] = None
    request_time: Optional[str] = None
    request: Optional[RequestDTO] = None
    consent_obtained: bool = False
    individual_id: Optional[str] = None
    individual_id_type: Optional[str] = None
    request_hmac: Optional[str] = None
    thumbprint: Optional[str] = None
    request_session_key: Optional[str] = None
    env: Optional[str] = None
    otp: Optional[str] = None
    domain_uri: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        result = {}
        if self.id:
            result["id"] = self.id
        if self.version:
            result["version"] = self.version
        if self.requested_auth:
            result["requestedAuth"] = {
                "demo": self.requested_auth.demo,
                "bio": self.requested_auth.bio,
                "otp": self.requested_auth.otp,
                "pin": self.requested_auth.pin
            }
        if self.transaction_id:
            result["transactionID"] = self.transaction_id
        if self.request_time:
            result["requestTime"] = self.request_time
        if self.request:
            req_dict = {}
            if self.request.otp:
                req_dict["otp"] = self.request.otp
            if self.request.timestamp:
                req_dict["timestamp"] = self.request.timestamp
            if self.request.demographics:
                req_dict["demographics"] = self.request.demographics
            if self.request.biometrics:
                req_dict["biometrics"] = [
                    {
                        "data": bio.data,
                        "bioType": bio.bio_type,
                        "bioSubType": bio.bio_sub_type
                    } for bio in self.request.biometrics
                ]
            result["request"] = req_dict
        result["consentObtained"] = self.consent_obtained
        if self.individual_id:
            result["individualId"] = self.individual_id
        if self.individual_id_type:
            result["individualIdType"] = self.individual_id_type
        if self.request_hmac:
            result["requestHMAC"] = self.request_hmac
        if self.thumbprint:
            result["thumbprint"] = self.thumbprint
        if self.request_session_key:
            result["requestSessionKey"] = self.request_session_key
        if self.env:
            result["env"] = self.env
        if self.otp:
            result["otp"] = self.otp
        if self.domain_uri:
            result["domainUri"] = self.domain_uri
        return result

