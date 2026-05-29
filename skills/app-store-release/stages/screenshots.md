# Stage: Screenshots（截图规格 & 校验）

> 截图**生成**（AI 合成营销图）在本 skill 的子区：`../preview-studio/overview.md`。
> 这里只管**规格 & 校验**。

## Apple 当前规则要点（2025+）

**iPhone**（必传至少一组最大尺寸即可，ASC 会自动派生其他尺寸；建议手动出图保证视觉）
- 6.9" Display: 1320 × 2868（iPhone 16 Pro Max）— **必传**
- 6.5" Display: 1242 × 2688 / 1284 × 2778
- 5.5" Display: 1242 × 2208 — 老 App 才需要

**iPad**
- 13" Display: 2064 × 2752（iPad Pro M4）— **必传（若支持 iPad）**
- 12.9" Display: 2048 × 2732

**macOS**
- 2880 × 1800 / 2560 × 1600 / 1440 × 900 / 1280 × 800

**visionOS**
- 3840 × 2160

**App Preview（视频）**
- iPhone 6.9": 886 × 1920 或 1080 × 1920 / 1920 × 1080
- 时长 15–30 秒，H.264，≤ 500 MB

每个语言 / 平台：≤ 10 张截图 + 3 个预览视频。

## 校验维度
- 像素尺寸严格匹配
- 颜色空间：**sRGB**（不能是 Display P3 / Adobe RGB）
- 不能有 alpha 通道（PNG 必须 RGB 而非 RGBA）
- 文件 ≤ 8 MB

## 脚本
- `../scripts/screenshots_validate.py <dir>` — 批量校验目录下 PNG：尺寸命中 Apple 集合 / 无 alpha / 未嵌非 sRGB profile / ≤8MB（**已收录**，纯 stdlib 不依赖 Pillow，FAIL 时退出码 1）。用法：
  ```bash
  ../scripts/screenshots_validate.py screenshots/final/
  ../scripts/screenshots_validate.py screenshots/final/iphone-6.9/en-US/ --expect 1320x2868
  ```
- 规格矩阵无需脚本——直接看本文档上方"Apple 当前规则要点"表即可。

## 参考
- https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications
