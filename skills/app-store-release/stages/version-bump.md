# Stage: Version Bump

## 概念区分（最容易混的）
- **MARKETING_VERSION** = "Version" 字段（CFBundleShortVersionString），用户看到的，如 `1.2.3`
- **CURRENT_PROJECT_VERSION** = "Build" 字段（CFBundleVersion），ASC 内部用，必须**严格递增**，常用 `1`/`2`/`3`... 或时间戳 `20260528.1`

## 步骤
1. 读当前两个值（`xcrun agvtool what-version` / `what-marketing-version`，或直接 grep `.pbxproj`）
2. 询问 bump 类型：patch / minor / major / 自定义
3. Build number：默认 +1，可选时间戳模式
4. 多 target / extension 全部同步
5. 询问是否 git commit + tag（`v1.2.4`）

## 脚本
本阶段无预置脚本，AI 现场实现即可：
- 优先 `xcrun agvtool next-version -all`（build）/ `agvtool new-marketing-version 1.2.4`（version）
- agvtool 不适用时（如纯 SPM / 版本写在 `.pbxproj` 的 build settings）直接读写 `MARKETING_VERSION` / `CURRENT_PROJECT_VERSION`

## Git 行为约定
**不主动 commit / tag**（遵循用户全局偏好）。只有用户明确说"顺便 tag 一下"才执行。

## 参考
- https://developer.apple.com/library/archive/qa/qa1827/_index.html
