import secrets
import string

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

AUTH_SIZE = 16


def encrypt(secret: str, secret_key_file: str) -> bytes:
    """Encrypt a secret with Cipher"""
    recipient_key = RSA.import_key(
        open(f"{secret_key_file}.pub").read())
    session_key = get_random_bytes(16)
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    key = cipher_rsa.encrypt(session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(secret.encode('utf-8'))
    data = key + cipher_aes.nonce + tag + ciphertext
    return data


def decrypt(secret: bytes, secret_key_file: str) -> bytes:
    "Decode a secret with Cipher"
    private_key = RSA.import_key(
        open(f"{secret_key_file}").read())
    cipher_rsa = PKCS1_OAEP.new(private_key)
    info = []
    for size in (private_key.size_in_bytes(), 16, 16, None):
        info.append(secret[:size])
        secret = secret[size:]

    enc_session_key, nonce, tag, ciphertext = info
    session_key = cipher_rsa.decrypt(enc_session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return data

def generate_password(length=20):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
