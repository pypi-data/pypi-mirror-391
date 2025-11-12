"""OTP request DTO"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class OtpRequestDTO:
    """OTP request DTO"""
    id: Optional[str] = None
    version: Optional[str] = None
    transaction_id: Optional[str] = None
    request_time: Optional[str] = None
    individual_id: Optional[str] = None
    individual_id_type: Optional[str] = None
    otp_channel: List[str] = field(default_factory=list)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        result = {}
        if self.id:
            result["id"] = self.id
        if self.version:
            result["version"] = self.version
        if self.transaction_id:
            result["transactionID"] = self.transaction_id
        if self.request_time:
            result["requestTime"] = self.request_time
        if self.individual_id:
            result["individualId"] = self.individual_id
        if self.individual_id_type:
            result["individualIdType"] = self.individual_id_type
        if self.otp_channel:
            result["otpChannel"] = self.otp_channel
        return result

