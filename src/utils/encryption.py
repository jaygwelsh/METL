# src/utils/encryption.py

import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization, hashes, keywrap
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import json

class EncryptionManager:
    def __init__(self, key: bytes):
        # key should be 32 bytes for AES-256
        self.key = key

    def encrypt_metadata(self, metadata: dict) -> bytes:
        plaintext = json.dumps(metadata, sort_keys=True).encode('utf-8')
        iv = os.urandom(12)  # GCM nonce
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return iv + encryptor.tag + ciphertext

    def decrypt_metadata(self, data: bytes) -> dict:
        # data format: iv(12 bytes) + tag(16 bytes) + ciphertext
        if len(data) < 28:
            raise ValueError("Invalid encrypted data length.")
        iv = data[:12]
        tag = data[12:28]
        ciphertext = data[28:]
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return json.loads(plaintext.decode('utf-8'))
