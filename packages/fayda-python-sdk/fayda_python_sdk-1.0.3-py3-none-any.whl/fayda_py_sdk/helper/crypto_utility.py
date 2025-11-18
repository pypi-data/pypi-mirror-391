"""Crypto utility wrapper"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import os

from .crypto_core import CryptoCore
from .crypto_util import CryptoUtil


class CryptoUtility:
    """Crypto utility wrapper class"""

    # Hardcoded configuration values
    SYMMETRIC_ALGORITHM = "AES/GCM/NoPadding"
    ASYMMETRIC_ALGORITHM = "RSA/ECB/OAEPWithSHA-256AndMGF1Padding"
    AES_ALGORITHM = "AES"
    AES_KEY_LENGTH = 256  # bits
    GCM_TAG_LENGTH = 128  # bits
    HASH_ALGORITHM = "SHA-256"
    MGF1_ALGORITHM = "MGF1"

    def __init__(self, crypto_core: CryptoCore):
        self.crypto_core = crypto_core

    def symmetric_encrypt(self, data: bytes, secret_key: bytes) -> bytes:
        """Symmetric encryption"""
        return self.crypto_core.symmetric_encrypt(secret_key, data, None)

    def symmetric_decrypt(self, secret_key: bytes, encrypted_data: bytes) -> bytes:
        """Symmetric decryption"""
        return self.crypto_core.symmetric_decrypt(secret_key, encrypted_data, None)

    def gen_sec_key(self) -> bytes:
        """Generate a secret key (AES 256-bit)"""
        return secrets.token_bytes(32)  # 32 bytes = 256 bits

    def asymmetric_encrypt(self, data: bytes, public_key) -> bytes:
        """Asymmetric encryption"""
        return self.crypto_core.asymmetric_encrypt(public_key, data)

    def decode_base64(self, data: str) -> bytes:
        """Decode base64"""
        return CryptoUtil.decode_plain_base64(data)

    def symmetric_encrypt_with_iv_aad(self, secret_key: bytes, data: bytes, iv_bytes: bytes, aad_bytes: bytes) -> bytes:
        """Symmetric encryption with IV and AAD"""
        return self.crypto_core.symmetric_encrypt_with_iv(secret_key, data, iv_bytes, aad_bytes)

    def get_symmetric_key(self) -> bytes:
        """Get symmetric key"""
        return self.gen_sec_key()

    def _get_xor(self, a: str, b: str) -> bytes:
        """XOR two strings"""
        a_bytes = a.encode('utf-8')
        b_bytes = b.encode('utf-8')
        a_len = len(a_bytes)
        b_len = len(b_bytes)
        
        if a_len > b_len:
            b_bytes = b'\x00' * (a_len - b_len) + b_bytes
        elif b_len > a_len:
            a_bytes = b'\x00' * (b_len - a_len) + a_bytes
        
        len_max = max(a_len, b_len)
        xor_bytes = bytearray(len_max)
        for i in range(len_max):
            xor_bytes[i] = a_bytes[i] ^ b_bytes[i]
        return bytes(xor_bytes)

    def _get_last_bytes(self, xor_bytes: bytes, last_bytes_num: int) -> bytes:
        """Get last N bytes"""
        assert len(xor_bytes) >= last_bytes_num
        return xor_bytes[-last_bytes_num:]

