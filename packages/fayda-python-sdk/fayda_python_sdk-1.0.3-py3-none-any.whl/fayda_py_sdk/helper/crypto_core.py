"""Crypto core implementation"""

import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import secrets


class CryptoCore:
    """Core cryptographic operations"""

    # Hardcoded configuration values
    HASH_ALGORITHM = hashes.SHA256()
    TAG_LENGTH = 128  # bits
    SYMMETRIC_KEY_LENGTH = 256  # bits
    ASYMMETRIC_KEY_LENGTH = 2048  # bits

    def __init__(self):
        self.backend = default_backend()

    def symmetric_encrypt(self, key: bytes, data: bytes, aad: bytes = None) -> bytes:
        """Symmetric encryption using AES-GCM"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits)")
        
        iv = secrets.token_bytes(16)
        aesgcm = AESGCM(key)
        if aad:
            ciphertext = aesgcm.encrypt(iv, data, aad)
        else:
            ciphertext = aesgcm.encrypt(iv, data, None)
        
        return ciphertext + iv

    def symmetric_encrypt_with_iv(self, key: bytes, data: bytes, iv: bytes, aad: bytes = None) -> bytes:
        """Symmetric encryption with provided IV"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits)")
        
        aesgcm = AESGCM(key)
        if aad:
            return aesgcm.encrypt(iv, data, aad)
        else:
            return aesgcm.encrypt(iv, data, None)

    def symmetric_decrypt(self, key: bytes, data: bytes, aad: bytes = None) -> bytes:
        """Symmetric decryption using AES-GCM"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits)")
        
        iv = data[-16:]
        ciphertext = data[:-16]
        
        aesgcm = AESGCM(key)
        if aad:
            return aesgcm.decrypt(iv, ciphertext, aad)
        else:
            return aesgcm.decrypt(iv, ciphertext, None)

    def symmetric_decrypt_with_iv(self, key: bytes, data: bytes, iv: bytes, aad: bytes = None) -> bytes:
        """Symmetric decryption with provided IV"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits)")
        
        aesgcm = AESGCM(key)
        if aad:
            return aesgcm.decrypt(iv, data, aad)
        else:
            return aesgcm.decrypt(iv, data, None)

    def asymmetric_encrypt(self, public_key, data: bytes) -> bytes:
        """Asymmetric encryption using RSA-OAEP with SHA-256"""
        oaep_padding = padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
        return public_key.encrypt(data, oaep_padding)

    def asymmetric_decrypt(self, private_key, data: bytes) -> bytes:
        """Asymmetric decryption using RSA-OAEP with SHA-256"""
        oaep_padding = padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
        return private_key.decrypt(data, oaep_padding)

