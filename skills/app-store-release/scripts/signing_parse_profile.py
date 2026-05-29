#!/usr/bin/env python3
"""解析 .mobileprovision（CMS/PKCS7 包裹的 plist），打印关键签名信息（纯 stdlib）。

.mobileprovision 是 CMS DER 容器，但里面那段 plist 是明文 XML——
直接在二进制里截出 <?xml ... </plist> 即可，无需 openssl/security 解 CMS。

提取并打印：
  - Name / TeamIdentifier / AppIDName
  - application-identifier（含 Bundle ID）
  - ExpirationDate（并标注是否已过期）
  - aps-environment（Push 用，常见漏配点）
  - get-task-allow（development=true / distribution=false）
  - ProvisionedDevices 数量（adhoc/development 才有）

用法：
    ./signing_parse_profile.py path/to/App.mobileprovision
    ./signing_parse_profile.py ~/Library/MobileDevice/Provisioning\\ Profiles/
"""
import argparse
import datetime
import os
import plistlib
import sys


def extract_plist(path):
    with open(path, "rb") as f:
        blob = f.read()
    start = blob.find(b"<?xml")
    end = blob.find(b"</plist>")
    if start == -1 or end == -1:
        raise ValueError("找不到内嵌 plist（文件可能损坏或不是 mobileprovision）")
    return plistlib.loads(blob[start:end + len(b"</plist>")])


def summarize(path):
    try:
        p = extract_plist(path)
    except (ValueError, plistlib.InvalidFileException) as e:
        print(f"✗ {os.path.basename(path)}: {e}")
        return

    ent = p.get("Entitlements", {})
    name = p.get("Name", "?")
    team = ",".join(p.get("TeamIdentifier", [])) or "?"
    app_id = ent.get("application-identifier", "?")
    aps = ent.get("aps-environment")
    get_task_allow = ent.get("get-task-allow")
    exp = p.get("ExpirationDate")

    print(f"● {os.path.basename(path)}")
    print(f"    Name:        {name}")
    print(f"    Team:        {team}")
    print(f"    AppID:       {app_id}")
    if exp is not None:
        now = datetime.datetime.now(tz=exp.tzinfo) if exp.tzinfo else datetime.datetime.now()
        expired = exp < now
        flag = "已过期 ✗" if expired else "有效 ✓"
        print(f"    Expires:     {exp:%Y-%m-%d}  ({flag})")
    if aps is not None:
        print(f"    aps-env:     {aps}")
    if get_task_allow is not None:
        kind = "development" if get_task_allow else "distribution"
        print(f"    get-task-allow: {get_task_allow}  ({kind} profile)")
    devices = p.get("ProvisionedDevices")
    if devices:
        print(f"    Devices:     {len(devices)} 台（development/adhoc）")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help=".mobileprovision 文件或目录")
    args = ap.parse_args()

    targets = []
    if os.path.isdir(args.path):
        for n in sorted(os.listdir(args.path)):
            if n.endswith(".mobileprovision"):
                targets.append(os.path.join(args.path, n))
    else:
        targets = [args.path]

    if not targets:
        sys.exit(f"没找到 .mobileprovision：{args.path}")

    for t in targets:
        summarize(t)
        print()


if __name__ == "__main__":
    main()
