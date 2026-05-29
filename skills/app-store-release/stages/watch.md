# Stage: Watch（审核状态轮询）

## 状态机（ASC `appStoreVersion.appStoreState`）
```
PREPARE_FOR_SUBMISSION
   ↓ submit
WAITING_FOR_REVIEW
   ↓
IN_REVIEW
   ↓
PENDING_DEVELOPER_RELEASE        （AFTER_APPROVAL 跳过此态）
   ↓ release
READY_FOR_SALE  ✅

其他终态：
REJECTED  ❌
METADATA_REJECTED ❌
DEVELOPER_REJECTED       （主动撤回）
INVALID_BINARY
```

## 步骤
1. 列最近 5 个版本，让用户选要监控的
2. 轮询 `GET /v1/apps/{appId}/appStoreVersions`，默认每 10 分钟一次
3. 状态变化时：
   - 控制台打印
   - 调 PushNotification 发推送（标题 "审核状态变更: IN_REVIEW → PENDING_DEVELOPER_RELEASE"）
4. 到达终态停止
5. **REJECTED 时**自动抓 Resolution Center 拒审原文，把 reviewer 消息 + Guideline 编号呈现给用户。后续修改让 Claude 基于 reviewer 原文 + Apple Guidelines 公开文档现答（仓库不预置 playbook），改完回 `build.md` 重新打包

## 与 /loop 的关系
适合用 `/loop` 定时唤起做轮询，例如：

> `/loop 10m 查一下 <App> 的 App Store 审核状态，有变化就告诉我`

`/loop` 会按间隔重复执行这段自然语言任务；不存在专门的 `/review-status-watch` 命令。

## 脚本
本阶段无预置脚本，AI 现场实现即可：单次 `GET /v1/apps/{appId}/appStoreVersions`（token 用 `../scripts/asc_mint_jwt.py` 签），与上次状态对比，变化时打印 + 调 PushNotification。状态可缓存在 `~/.appstoreconnect/state_cache.json`。

## 参考
- https://developer.apple.com/documentation/appstoreconnectapi/appstoreversion/attributes
