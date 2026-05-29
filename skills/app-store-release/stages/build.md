# Stage: Build（Xcode archive + export ipa/pkg）

## 前置
- Xcode 项目根目录可定位
- 签名配置正常（出错时切到 `signing.md`）
- Build number 已 bump（见 `version-bump.md`）
- Info.plist 已有 `ITSAppUsesNonExemptEncryption`（见 `export-compliance.md`）

## 步骤

1. 探测 workspace / project / scheme（`xcodebuild -list`）
2. 询问目标平台：iOS / iPadOS（同 iOS） / macOS / visionOS
3. archive（产物写到项目 `<项目名>-appstoreconnect/build/`，约定见 SKILL.md 顶部）：
   ```bash
   xcodebuild archive \
     -workspace App.xcworkspace \
     -scheme App \
     -configuration Release \
     -destination 'generic/platform=iOS' \
     -archivePath <项目名>-appstoreconnect/build/App.xcarchive \
     CODE_SIGN_STYLE=Automatic
   ```
4. 写 `<项目名>-appstoreconnect/build/ExportOptions.plist`（`method=app-store-connect` / `signingStyle=automatic`）
   > `method` 值：Xcode 15.3+ 用 `app-store-connect`；更旧的 Xcode 用 `app-store`。报 "Unsupported option" 时换另一个。
5. `xcodebuild -exportArchive ... -exportOptionsPlist <项目名>-appstoreconnect/build/ExportOptions.plist -exportPath <项目名>-appstoreconnect/build/ipa/`
6. **macOS 额外**：`xcrun notarytool submit --wait` 公证 + `stapler staple`

## 输出
```
<项目名>-appstoreconnect/build/
├── App.xcarchive/
├── ipa/
│   └── App.ipa     # macOS 时是 App.pkg
└── ExportOptions.plist
```

旧版本的 `.xcarchive` 建议保留（崩溃日志符号化要用），定期清旧的 ipa 即可。

## 脚本
本阶段无预置脚本，AI 现场拼命令即可：
- archive / exportArchive：上方"步骤"里的 `xcodebuild` 命令直接用
- ExportOptions.plist：按 `method` / `signingStyle` 现场写一个小 plist
- macOS 公证：`xcrun notarytool submit --wait` + `xcrun stapler staple`

## 常见错误兜底
- "No profiles for 'xxx' were found" → 切 `signing.md`
- "exportArchive: No applicable devices found" → destination 应写 `generic/platform=...`

## 参考
- https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases
