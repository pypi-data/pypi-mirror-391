import os
import json
from .加解密 import *

import sys
TOKENS_FILE = "tokens_otp.json"   # 旧的总文件
if len(sys.argv) > 1:
    TOKENS_FILE = sys.argv[1]
TOKENS_DIR = "tokens"             # 新的目录
if len(sys.argv) > 2:
    TOKENS_DIR = sys.argv[2]


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
