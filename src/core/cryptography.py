# src/core/cryptography.py

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
import base64

def generate_key_pair():
    # Generate Ed25519 keys deterministically
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

def sign_data(data_str, private_key):
    # Ed25519 is deterministic: same message + same key = same signature
    signature = private_key.sign(data_str.encode('utf-8'))
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(data_str, signature_b64, public_key):
    signature = base64.b64decode(signature_b64)
    try:
        public_key.verify(signature, data_str.encode('utf-8'))
        return True
    except Exception:
        return False

def serialize_private_key(private_key):
    # Not needed if we never write keys to disk, but let's keep it
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

def serialize_public_key(public_key):
    # Not needed if we never write keys to disk, but let's keep it
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
