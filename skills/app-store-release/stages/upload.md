# Stage: Upload（上传 TestFlight）

## 上传方式对比

| 方式 | 工具 | 说明 |
| --- | --- | --- |
| altool（旧） | `xcrun altool --upload-app` | 简单，日志少 |
| **Transporter** | `iTMSTransporter` | 默认走这个，最稳 |
| ASC API multipart | curl + 自实现 | 最可控，CI 用 |

## 前置
- `.ipa` 已有（见 `build.md`）
- ASC 凭据就绪（见 `asc-auth.md`）
- Bundle ID 在 ASC 已注册对应 App 记录

## ⚠️ altool 找 `.p8` 的路径规则（高频坑）
`xcrun altool --apiKey <key_id>` **不接受文件路径**，它只按文件名 `AuthKey_<key_id>.p8` 在固定目录里搜：
`./private_keys/`、`~/private_keys/`、`~/.private_keys/`、`~/.appstoreconnect/private_keys/`。

本 skill 的凭据约定是放在 `~/.appstoreconnect/` **根目录**，altool 搜不到。两种解法：
- 推荐：把 `.p8` 同时软链/复制到 `~/.appstoreconnect/private_keys/AuthKey_<key_id>.p8`
  ```bash
  mkdir -p ~/.appstoreconnect/private_keys && \
  ln -sf ~/.appstoreconnect/AuthKey_<key_id>.p8 ~/.appstoreconnect/private_keys/
  ```
- 或改用 `iTMSTransporter` / ASC API multipart 上传（不依赖这个搜索路径）。

## 步骤
1. 校验 ipa：`unzip -p App.ipa Payload/*.app/Info.plist | plutil -p -` 抓 Bundle ID / Version / Build
2. `xcrun altool --validate-app -f App.ipa --type ios --apiKey <key_id> --apiIssuer <issuer_id>`（`.p8` 须在上述搜索路径内）
3. 通过后 `xcrun altool --upload-app -f App.ipa ...`
4. 用 ASC API `GET /v1/builds?filter[app]=<appId>&sort=-uploadedDate` 轮询，直到 `processingState` 由 `PROCESSING` 变 `VALID`（通常 5–30 分钟）
5. （可选）`POST /v1/betaGroupBuilds` 加到指定 Beta Group
6. （可选）`POST /v1/betaBuildLocalizations` 写 What to Test

## 输出
- 打印 ASC 后台对应 build URL
- 处理完成时 push notification 提醒

## 脚本
本阶段无预置脚本，AI 现场实现即可（都是拼命令 / 单个 API 调用 / 一个轮询循环）：
- 上传：直接 `xcrun altool --upload-app ...` 或 `iTMSTransporter`
- 等处理：循环 `GET /v1/builds?filter[app]=<appId>&sort=-uploadedDate`，读 `processingState` 到 `VALID`（token 用 `../scripts/asc_mint_jwt.py` 签）
- 分组分发：`POST /v1/betaGroupBuilds`

## 常见错误
- `ITMS-90189: Redundant Binary Upload` → build number 重复，跑 `version-bump.md`
- `ITMS-90683: Missing Purpose String` → Info.plist 少 `NSXxxUsageDescription`
- `Invalid Provisioning Profile` → 跑 `signing.md`

## 参考
- https://developer.apple.com/documentation/appstoreconnectapi/uploading-builds
