"""Crypto utility functions"""

import base64
from typing import Optional


class CryptoUtil:
    """Crypto utility class for common crypto operations"""

    @staticmethod
    def encode_to_url_safe_base64(data: bytes) -> Optional[str]:
        """Encodes to BASE64 URL Safe"""
        if data is None:
            return None
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

    @staticmethod
    def decode_url_safe_base64(data: str) -> Optional[bytes]:
        """Decodes from BASE64 URL Safe"""
        if not data:
            return None
        # Add padding if needed
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        return base64.urlsafe_b64decode(data)

    @staticmethod
    def encode_to_plain_base64(data: bytes) -> Optional[str]:
        """Encodes to BASE64 String"""
        if data is None:
            return None
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def decode_plain_base64(data: str) -> Optional[bytes]:
        """Decodes from BASE64"""
        if not data:
            return None
        return base64.b64decode(data)

    @staticmethod
    def combine_byte_array(data: bytes, key: bytes, key_splitter: str) -> bytes:
        """Combine data, key and key splitter"""
        key_splitter_bytes = key_splitter.encode('utf-8')
        combined = bytearray(key)
        combined.extend(key_splitter_bytes)
        combined.extend(data)
        return bytes(combined)

