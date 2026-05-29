#!/usr/bin/env python3
"""校验 ASC metadata 文案的字符数上限（纯 stdlib）。

遍历 metadata 根目录下的每个 locale 子目录，对每个已知字段文件做字符数检查，
超限即 FAIL。关键词字段额外提示空格浪费（空格也算字符）。

字段上限（与 stages/metadata.md 一致）：
    name.txt              30
    subtitle.txt          30
    description.txt       4000
    keywords.txt          100
    promotional_text.txt  170
    release_notes.txt     4000

URL 类文件（*_url.txt）只做非空 + 简单 http(s) 前缀检查。

任意字段超限退出码为 1。

用法：
    ./validate_lengths.py <项目名>-appstoreconnect/metadata/
    ./validate_lengths.py path/to/metadata --locale zh-Hans
"""
import argparse
import os
import sys

LIMITS = {
    "name.txt": 30,
    "subtitle.txt": 30,
    "description.txt": 4000,
    "keywords.txt": 100,
    "promotional_text.txt": 170,
    "release_notes.txt": 4000,
}
URL_FILES = {"marketing_url.txt", "privacy_url.txt", "support_url.txt"}


def read_text(path):
    with open(path, encoding="utf-8") as f:
        # 末尾换行不计入字符数（编辑器常自动加），其余原样统计
        return f.read().rstrip("\n")


def check_locale(locale_dir):
    problems = []
    for fname, limit in LIMITS.items():
        fp = os.path.join(locale_dir, fname)
        if not os.path.exists(fp):
            continue
        text = read_text(fp)
        n = len(text)
        status = "✓" if n <= limit else "✗"
        if n > limit:
            problems.append(f"{fname}: {n}/{limit} 超 {n - limit}")
        print(f"    {status} {fname}: {n}/{limit}")
        if fname == "keywords.txt":
            spaces = text.count(" ")
            if spaces:
                print(f"      ! 含 {spaces} 个空格（空格也算字符，逗号后别加空格）")
            if text.endswith(",") or ",," in text:
                print("      ! 关键词有空项/末尾逗号，建议清理")

    for fname in URL_FILES:
        fp = os.path.join(locale_dir, fname)
        if not os.path.exists(fp):
            continue
        text = read_text(fp).strip()
        ok = text.startswith("http://") or text.startswith("https://")
        print(f"    {'✓' if ok else '✗'} {fname}: {text or '(空)'}")
        if not ok:
            problems.append(f"{fname}: 不是合法 http(s) URL")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help="metadata 根目录")
    ap.add_argument("--locale", help="只校验指定 locale（如 zh-Hans）")
    args = ap.parse_args()

    if not os.path.isdir(args.path):
        sys.exit(f"目录不存在：{args.path}")

    locales = []
    if args.locale:
        locales = [args.locale]
    else:
        locales = sorted(
            d for d in os.listdir(args.path)
            if os.path.isdir(os.path.join(args.path, d)) and not d.startswith(".")
        )
    if not locales:
        sys.exit(f"{args.path} 下没有 locale 子目录")

    total_problems = 0
    for loc in locales:
        loc_dir = os.path.join(args.path, loc)
        if not os.path.isdir(loc_dir):
            print(f"[{loc}] 跳过：目录不存在")
            continue
        print(f"[{loc}]")
        problems = check_locale(loc_dir)
        total_problems += len(problems)

    print(f"\n共 {total_problems} 处超限/不合法。")
    sys.exit(1 if total_problems else 0)


if __name__ == "__main__":
    main()
