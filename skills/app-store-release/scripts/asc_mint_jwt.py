#!/usr/bin/env python3
"""签出 App Store Connect API 的 ES256 JWT，输出到 stdout。

读取 ~/.appstoreconnect/config.json + 对应的 .p8 私钥，按 Apple 规范签 token：
- header: alg=ES256, typ=JWT, kid=<Key ID>
- payload: iss=<Issuer ID>, iat=now, exp=now+ttl(<=1200s), aud=appstoreconnect-v1
- 故意不带 scope —— 带了会把 token 限制到指定接口，导致其他调用 401。

依赖：cryptography（ES256 必需）。缺了会给出 pip 提示。

用法：
    TOKEN=$(./asc_mint_jwt.py)
    TOKEN=$(./asc_mint_jwt.py --config ~/.appstoreconnect/config.json --ttl 1200)
    curl -H "Authorization: Bearer $TOKEN" https://api.appstoreconnect.apple.com/v1/apps
"""
import argparse
import base64
import json
import os
import sys
import time


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="~/.appstoreconnect/config.json",
                    help="config.json 路径（含 key_id / issuer_id / key_path）")
    ap.add_argument("--ttl", type=int, default=1200,
                    help="token 有效期（秒），Apple 上限 1200")
    args = ap.parse_args()

    cfg_path = os.path.expanduser(args.config)
    try:
        with open(cfg_path) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        sys.exit(f"找不到 config：{cfg_path}（首次配置见 stages/asc-auth.md）")
    except json.JSONDecodeError as e:
        sys.exit(f"config.json 不是合法 JSON：{e}")

    try:
        key_id = cfg["key_id"]
        issuer_id = cfg["issuer_id"]
        key_path = os.path.expanduser(cfg["key_path"])  # 展开 ~，避免读不到 .p8
    except KeyError as e:
        sys.exit(f"config.json 缺字段 {e}（需要 key_id / issuer_id / key_path）")

    try:
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
    except ImportError:
        sys.exit("缺少依赖 cryptography，请先安装：pip install cryptography")

    try:
        with open(key_path, "rb") as f:
            private_key = load_pem_private_key(f.read(), password=None)
    except FileNotFoundError:
        sys.exit(f"找不到 .p8 私钥：{key_path}")

    ttl = min(max(args.ttl, 1), 1200)
    now = int(time.time())
    header = {"alg": "ES256", "kid": key_id, "typ": "JWT"}
    payload = {"iss": issuer_id, "iat": now, "exp": now + ttl, "aud": "appstoreconnect-v1"}

    signing_input = (
        b64url(json.dumps(header, separators=(",", ":")).encode())
        + "."
        + b64url(json.dumps(payload, separators=(",", ":")).encode())
    )
    der = private_key.sign(signing_input.encode("ascii"), ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    raw_sig = r.to_bytes(32, "big") + s.to_bytes(32, "big")  # DER -> JOSE raw(r||s)
    print(signing_input + "." + b64url(raw_sig))


if __name__ == "__main__":
    main()
