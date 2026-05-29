# Stage: Signing（签名诊断）

## 诊断维度（按命中率排序）

1. **证书是否存在 & 未过期**
   - `security find-identity -v -p codesigning`
   - 同时检查 "Apple Distribution" 和 "Apple Development"

2. **Provisioning Profile**
   - 位置：`~/Library/MobileDevice/Provisioning Profiles/*.mobileprovision`
   - 解析每个 profile：Team ID / Bundle ID / Entitlements / 过期时间
   - 与项目 `PRODUCT_BUNDLE_IDENTIFIER` 比对

3. **Bundle ID 一致性**
   - `xcodebuild -showBuildSettings | grep BUNDLE`
   - 主 App / Extensions / WatchKit target 父子关系

4. **Entitlements 与 Capabilities 对账**
   - 读 `*.entitlements` 文件
   - 对比 profile 内嵌的 entitlements
   - 常错点：Push Notification / iCloud / Sign in with Apple / App Groups / Associated Domains

5. **Team ID** — 项目 `DEVELOPMENT_TEAM` vs 证书 vs profile 三者一致

## 步骤
1. `xcodebuild -showBuildSettings` 抓 Team ID / Bundle ID / Code Sign Identity
2. 列本机所有签名证书 + profile
3. 交叉比对，输出诊断报告：
   ```
   ✗ Bundle ID 不匹配：项目 com.foo.bar，profile 是 com.foo.baz
   ✗ Profile 已过期 (2025-04-01)
   ✓ Team ID 一致
   ! Capability "Push Notification" 已开启但 profile 未包含 aps-environment
   ```
4. 给修复建议（去开发者后台重生 profile / Xcode 自动修复按钮 / 改 Bundle ID）

## 脚本
- `../scripts/signing_parse_profile.py` — 解析 `.mobileprovision`，打印 Name / Team / Bundle ID / 过期时间 / aps-environment / get-task-allow（**已收录**，纯 stdlib，从 CMS 容器里直接截内嵌 plist）。用法：
  ```bash
  ../scripts/signing_parse_profile.py ~/Library/MobileDevice/Provisioning\ Profiles/
  ```
- 上面"步骤"里的证书列举 + 交叉比对无需脚本，AI 现场跑 `security find-identity` / `xcodebuild -showBuildSettings` 配合本脚本输出做诊断即可。

## 参考
- https://developer.apple.com/documentation/security/code-signing-services
