# Stage: Privacy（隐私清单 / Nutrition Label）

ASC 的 "App Privacy" 问卷 + 打包进 ipa 的 `PrivacyInfo.xcprivacy` 文件，两者必须一致。

## 两个独立但相关的东西

1. **ASC App Privacy 问卷** — 在网页上勾选，影响 App Store 详情页"App 隐私"卡片
2. **PrivacyInfo.xcprivacy** — 打包进 ipa 的 plist，声明本 App + 第三方 SDK 的：
   - Required Reason APIs 使用理由
   - 收集的数据类型
   - Tracking Domains

不一致 → 审核必拒。

## 步骤

1. 扫描 `Podfile` / `Package.resolved` / `Cartfile`，列出所有第三方 SDK
2. 比对 [Apple commonly used SDK 清单](https://developer.apple.com/support/third-party-SDK-requirements/)，标出哪些 **必须**带 privacy manifest
3. 问卷式询问每类数据：
   - Contact Info / Health / Financial / Location / Sensitive Info / Contacts / User Content / Browsing / Search / Identifiers / Purchases / Usage Data / Diagnostics / Other
   - 每类问：是否收集？用途？是否与用户身份关联？是否用于追踪？
4. 输出两份产物：
   - `privacy-answers.md` — 给人类看，对照 ASC 网页逐项勾选
   - `PrivacyInfo.xcprivacy` — 直接加到 Xcode 项目

## 脚本
本阶段无预置脚本，AI 现场实现即可：
- 扫 SDK：`grep`/读取 `Podfile` / `Package.resolved` / `Cartfile` 列依赖，比对 Apple commonly-used SDK 清单
- 生成 `PrivacyInfo.xcprivacy`：按问卷答案现场填一个 plist 模板

## 参考
- https://developer.apple.com/documentation/bundleresources/privacy_manifest_files
- https://developer.apple.com/support/third-party-SDK-requirements/
- Required Reason APIs: https://developer.apple.com/documentation/bundleresources/privacy_manifest_files/describing_use_of_required_reason_api
