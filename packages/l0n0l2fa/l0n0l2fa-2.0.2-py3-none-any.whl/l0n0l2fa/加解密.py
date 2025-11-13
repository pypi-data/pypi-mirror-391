import hashlib
import base64
import json
from cryptography.fernet import Fernet

# ========== 加密工具 ==========
def derive_key_from_token(token: str) -> bytes:
    h = hashlib.sha256(token.encode()).digest()
    return base64.urlsafe_b64encode(h)


def encrypt_data(token: str, data: dict) -> bytes:
    key = derive_key_from_token(token)
    f = Fernet(key)
    return f.encrypt(json.dumps(data, ensure_ascii=False).encode())


def decrypt_data(token: str, enc: bytes) -> dict:
    key = derive_key_from_token(token)
    f = Fernet(key)
    return json.loads(f.decrypt(enc).decode())


def token_hash(token: str) -> str:
    sha_value = hashlib.sha512(token.encode()).digest()
    return hashlib.sha256(sha_value).hexdigest()
