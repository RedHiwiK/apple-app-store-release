#!/usr/bin/env python3
"""把一张/一批截图上传到指定的 ASC App Screenshot Set（纯 stdlib + asc_mint_jwt.py）。

ASC 截图上传是个三步 reservation 流程，繁琐易错，故固化为脚本：
  1. POST /v1/appScreenshots           预留（带 fileName/fileSize + screenshotSet 关系）
                                         → 返回 uploadOperations（分块 PUT 指令）
  2. 按 uploadOperations 逐块 PUT 原始字节（url/method/requestHeaders/offset/length）
  3. PATCH /v1/appScreenshots/{id}      提交（uploaded=true + sourceFileChecksum=md5）

前置：screenshotSet 需已存在（先 GET/POST /v1/appScreenshotSets 拿到 id——这步简单，
由调用方/AI 现场完成）。本脚本只负责"把图灌进某个 set"这段最容易写错的部分。

token 默认调用同目录 asc_mint_jwt.py 现签；也可用 --token 直接传。

用法：
    ./submit_upload_screenshots.py --set-id <screenshotSetId> img1.png img2.png
    ./submit_upload_screenshots.py --set-id <id> screenshots/final/iphone-6.9/en-US/
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

API = "https://api.appstoreconnect.apple.com"


def mint_token():
    here = os.path.dirname(os.path.abspath(__file__))
    script = os.path.join(here, "asc_mint_jwt.py")
    out = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"签 JWT 失败：{out.stderr.strip()}")
    return out.stdout.strip()


def api_request(method, url, token, body=None, headers=None, raw=False):
    data = None
    hdrs = {"Authorization": f"Bearer {token}"}
    if headers:
        hdrs.update(headers)
    if body is not None and not raw:
        data = json.dumps(body).encode()
        hdrs["Content-Type"] = "application/json"
    elif raw:
        data = body
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req) as resp:
            payload = resp.read()
            return resp.status, (json.loads(payload) if payload and not raw else None)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        sys.exit(f"{method} {url} -> {e.code}\n{detail}")


def reserve(token, set_id, fname, fsize):
    body = {
        "data": {
            "type": "appScreenshots",
            "attributes": {"fileName": fname, "fileSize": fsize},
            "relationships": {
                "appScreenshotSet": {"data": {"type": "appScreenshotSets", "id": set_id}}
            },
        }
    }
    _, resp = api_request("POST", f"{API}/v1/appScreenshots", token, body)
    data = resp["data"]
    return data["id"], data["attributes"]["uploadOperations"]


def put_chunks(file_bytes, operations):
    for op in operations:
        offset = op["offset"]
        length = op["length"]
        chunk = file_bytes[offset:offset + length]
        hdrs = {h["name"]: h["value"] for h in op.get("requestHeaders", [])}
        req = urllib.request.Request(op["url"], data=chunk, method=op["method"], headers=hdrs)
        try:
            urllib.request.urlopen(req).read()
        except urllib.error.HTTPError as e:
            sys.exit(f"上传分块失败 {op['method']} {op['url']} -> {e.code}\n{e.read().decode(errors='replace')}")


def commit(token, shot_id, md5_hex):
    body = {
        "data": {
            "type": "appScreenshots",
            "id": shot_id,
            "attributes": {"uploaded": True, "sourceFileChecksum": md5_hex},
        }
    }
    api_request("PATCH", f"{API}/v1/appScreenshots/{shot_id}", token, body)


def upload_one(token, set_id, path):
    fname = os.path.basename(path)
    with open(path, "rb") as f:
        file_bytes = f.read()
    fsize = len(file_bytes)
    md5_hex = hashlib.md5(file_bytes).hexdigest()

    shot_id, operations = reserve(token, set_id, fname, fsize)
    put_chunks(file_bytes, operations)
    commit(token, shot_id, md5_hex)
    print(f"✓ {fname} -> {shot_id}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--set-id", required=True, help="目标 appScreenshotSet 的 id")
    ap.add_argument("--token", help="ASC JWT（省略则现签）")
    ap.add_argument("paths", nargs="+", help="截图文件或目录")
    args = ap.parse_args()

    token = args.token or mint_token()

    files = []
    for p in args.paths:
        if os.path.isdir(p):
            files.extend(
                os.path.join(p, n) for n in sorted(os.listdir(p)) if n.lower().endswith(".png")
            )
        else:
            files.append(p)
    if not files:
        sys.exit("没有要上传的 PNG")

    for fp in files:
        upload_one(token, args.set_id, fp)

    print(f"\n完成 {len(files)} 张。")


if __name__ == "__main__":
    main()
