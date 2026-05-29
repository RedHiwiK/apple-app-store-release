#!/usr/bin/env python3
"""校验 App Store 截图是否满足 Apple 的提交规格（纯 stdlib，不依赖 Pillow）。

逐张检查：
  - 像素尺寸命中 Apple 接受的截图尺寸集合（横竖向都认）
  - 无 alpha 通道（PNG color type 必须是 RGB/灰度，不能 RGBA/带 tRNS）
  - 未嵌入非 sRGB 的 ICC profile（检测 iCCP chunk → 警告可能是 Display P3）
  - 文件 <= 8 MB

直接解析 PNG chunk（IHDR / iCCP / sRGB / tRNS），不读整张像素，速度快。
任意一张 FAIL 时退出码为 1，方便在流程里做闸口。

用法：
    ./screenshots_validate.py <项目名>-appstoreconnect/screenshots/final/
    ./screenshots_validate.py path/to/dir --expect 1320x2868
"""
import argparse
import os
import struct
import sys

MAX_BYTES = 8 * 1024 * 1024

# Apple 接受的常见截图像素尺寸（竖向写法；脚本会自动补横向）。
_PORTRAIT = {
    (1320, 2868),  # iPhone 6.9"
    (1290, 2796),  # iPhone 6.7" (15 Pro Max 等)
    (1284, 2778),  # iPhone 6.5"
    (1242, 2688),  # iPhone 6.5"
    (1242, 2208),  # iPhone 5.5"
    (2064, 2752),  # iPad 13" (M4)
    (2048, 2732),  # iPad 12.9"
    (2880, 1800),  # macOS
    (2560, 1600),
    (1440, 900),
    (1280, 800),
}
ACCEPTED = _PORTRAIT | {(h, w) for (w, h) in _PORTRAIT}

# PNG color type：含 alpha 的是 4(灰+α) 和 6(RGBA)
_ALPHA_COLOR_TYPES = {4, 6}


def read_png_info(path):
    """返回 (width, height, color_type, has_iccp, has_srgb, has_trns) 或 raise。"""
    with open(path, "rb") as f:
        sig = f.read(8)
        if sig != b"\x89PNG\r\n\x1a\n":
            raise ValueError("不是 PNG（App Store 截图建议用 PNG）")
        width = height = color_type = None
        has_iccp = has_srgb = has_trns = False
        while True:
            length_bytes = f.read(4)
            if len(length_bytes) < 4:
                break
            (length,) = struct.unpack(">I", length_bytes)
            ctype = f.read(4)
            if ctype == b"IHDR":
                data = f.read(length)
                width, height, _bitdepth, color_type = struct.unpack(">IIBB", data[:10])
                f.read(4)  # CRC
            elif ctype == b"iCCP":
                has_iccp = True
                f.seek(length + 4, os.SEEK_CUR)
            elif ctype == b"sRGB":
                has_srgb = True
                f.seek(length + 4, os.SEEK_CUR)
            elif ctype == b"tRNS":
                has_trns = True
                f.seek(length + 4, os.SEEK_CUR)
            elif ctype == b"IDAT":
                # 像素数据开始，关心的 ancillary chunk 都在它之前，提前结束
                break
            else:
                f.seek(length + 4, os.SEEK_CUR)
        if width is None:
            raise ValueError("缺 IHDR，PNG 损坏")
        return width, height, color_type, has_iccp, has_srgb, has_trns


def check(path, expect):
    problems = []
    warnings = []

    size = os.path.getsize(path)
    if size > MAX_BYTES:
        problems.append(f"文件 {size/1024/1024:.1f}MB > 8MB")

    try:
        w, h, color_type, has_iccp, has_srgb, has_trns = read_png_info(path)
    except ValueError as e:
        return [str(e)], []

    if (w, h) not in ACCEPTED:
        if expect and (w, h) == expect:
            pass
        else:
            problems.append(f"尺寸 {w}x{h} 不在 Apple 接受集合内")
    if expect and (w, h) != expect:
        problems.append(f"尺寸 {w}x{h} != 期望 {expect[0]}x{expect[1]}")

    if color_type in _ALPHA_COLOR_TYPES or has_trns:
        problems.append("含 alpha 通道（需导出为不带透明的 RGB）")

    if has_iccp and not has_srgb:
        warnings.append("嵌入了 ICC profile 且无 sRGB 标记，可能是 Display P3，请确认导出为 sRGB")

    return problems, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help="截图文件或目录")
    ap.add_argument("--expect", help="强制期望尺寸，如 1320x2868")
    args = ap.parse_args()

    expect = None
    if args.expect:
        try:
            ew, eh = args.expect.lower().split("x")
            expect = (int(ew), int(eh))
        except ValueError:
            sys.exit("--expect 格式应为 WxH，如 1320x2868")

    files = []
    if os.path.isdir(args.path):
        for root, _, names in os.walk(args.path):
            for n in sorted(names):
                if n.lower().endswith(".png"):
                    files.append(os.path.join(root, n))
    else:
        files = [args.path]

    if not files:
        sys.exit(f"没找到 PNG：{args.path}")

    failed = 0
    for fp in files:
        problems, warnings = check(fp, expect)
        rel = os.path.relpath(fp, args.path if os.path.isdir(args.path) else os.path.dirname(fp) or ".")
        if problems:
            failed += 1
            print(f"✗ {rel}")
            for p in problems:
                print(f"    - {p}")
        else:
            print(f"✓ {rel}")
        for wmsg in warnings:
            print(f"    ! {wmsg}")

    print(f"\n{len(files)} 张，{failed} 张未通过。")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
