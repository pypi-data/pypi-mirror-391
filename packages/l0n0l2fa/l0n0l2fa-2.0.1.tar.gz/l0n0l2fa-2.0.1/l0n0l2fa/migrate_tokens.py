import os
import json
import hashlib
import base64
from cryptography.fernet import Fernet
import sys
TOKENS_FILE = "tokens_otp.json"   # 旧的总文件
if len(sys.argv) > 1:
    TOKENS_FILE = sys.argv[1]
TOKENS_DIR = "tokens"             # 新的目录
if len(sys.argv) > 2:
    TOKENS_DIR = sys.argv[2]


def derive_key_from_token(token: str) -> bytes:
    h = hashlib.sha256(token.encode()).digest()
    return base64.urlsafe_b64encode(h)


def encrypt_data(token: str, data: dict) -> bytes:
    key = derive_key_from_token(token)
    f = Fernet(key)
    return f.encrypt(json.dumps(data, ensure_ascii=False).encode())


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def migrate(path: str, outdir: str):
    if not os.path.exists(path):
        print("未找到旧文件")
        return
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    with open(path, "r", encoding="utf-8") as f:
        users = json.load(f)

    for user in users:
        token = user.get("token")
        if not token:
            print(f"用户 {user.get('user')} 缺少 token，跳过")
            continue

        # 删除明文 token，保留 user 和 secrets
        user.pop("token", None)

        enc = encrypt_data(token, user)
        fname = os.path.join(outdir, f"{token_hash(token)}.json.enc")
        with open(fname, "wb") as f:
            f.write(enc)

        print(f"用户 {user['user']} 已迁移到 {fname}")

    print("迁移完成")


def main():
    migrate(TOKENS_FILE, TOKENS_DIR)


if __name__ == "__main__":
    main()
