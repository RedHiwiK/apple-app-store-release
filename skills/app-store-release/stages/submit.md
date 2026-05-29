# Stage: Submit（准备审核 — **不替用户点最终提审**）

> **重要边界**：本 stage 的 skill 通过 ASC API 把所有需要的数据准备好（建版本、绑 build、推 metadata、上传截图、填审核信息），**到此为止**。
> **最终的"Submit for Review"按钮由用户在 ASC web 后台亲手点**。提审是不可逆操作（虽然可以撤回但要走流程），不应该由 AI 自动触发。

## 前置

- 目标 build 已上传且 `processingState=VALID`（见 `upload.md`）
- 元信息 / 截图 / 隐私问卷 / 加密合规已准备（`metadata.md` / `screenshots.md` / `privacy.md` / `export-compliance.md`）
- 强烈推荐：先过一遍 `../checklists.md` 的"首次提审清单"或"版本更新清单"

## 数据流向（重要）

本 stage 是把本地 `<项目名>-appstoreconnect/` 里准备好的资料**集中推到 ASC**的环节：

```
<项目名>-appstoreconnect/metadata/*           ─PATCH→ ASC App Store Version Localization
<项目名>-appstoreconnect/metadata/zh-Hans/icp_number.txt
                                              ─PATCH→ ASC App Info Localization (China ICP)  ← 上架中国区必传
<项目名>-appstoreconnect/screenshots/final/*  ─POST→  ASC App Screenshot Sets
<项目名>-appstoreconnect/review/notes.md      ─PATCH→ ASC App Store Review Details
<项目名>-appstoreconnect/review/demo-video.mp4 ─PATCH→ ASC App Review Attachment
```

每一步推完都要让用户在 ASC web 后台验证一眼。

## ASC API 调用链（skill 通过 API 完成）

1. `POST /v1/appStoreVersions` — 创建版本（versionString / platform / releaseType）
2. `PATCH /v1/appStoreVersions/{id}/relationships/build` — 绑定 build
3. `PATCH /v1/appStoreVersionLocalizations/{id}` — 推送 What's New / Description / Promotional Text（读本地 `metadata/<locale>/*.txt`）
4. 上传截图：`POST /v1/appScreenshotSets` + `POST /v1/appScreenshots`（multipart 分块；读本地 `screenshots/final/<platform>/<locale>/*.png`）
5. `POST /v1/appStoreReviewDetails` — 填审核信息（详见下方"审核信息"段，读本地 `review/notes.md` + 演示账号 + 联系人）
6. （可选）上传演示视频附件：`POST /v1/appStoreVersionReviewAttachments`（读本地 `review/demo-video.mp4`）

## 然后停下来 — 交给用户

完成上述 1–6 步后，skill **不要**调 `POST /v1/appStoreVersionSubmissions`。

输出给用户：
```
✅ 所有审核数据已推到 ASC：
   - 版本 1.2.3 已创建（status: PREPARE_FOR_SUBMISSION）
   - build 42 已绑定
   - metadata: en-US / zh-Hans / ja 已更新
   - 截图: iPhone 6.9" × 6 张 / iPad 13" × 5 张 已上传
   - Review Notes / 演示账号 / 演示视频 已填

🔗 请到 ASC 后台 review 一遍后亲手点 Submit for Review：
   https://appstoreconnect.apple.com/apps/<appId>/appstore/version/inflight

⚠️ skill 不会替你点最终提审——这是不可逆操作，由你自己确认。
```

提审后，可以触发 `watch.md` 跟踪状态。

## 审核信息（Review Information）—— 拒审率最大的隐性杠杆

reviewer 平均只花 5–10 分钟看一个 App，**不会主动探索你的产品**。Review Notes 写得糊弄一点，过审率立即腰斩。AI 在帮用户准备 Review Notes 时**必须主动**提示用户把以下都写清楚：

### 必填项

1. **演示账号**（contactFirstName / contactLastName / contactPhone / contactEmail + demoAccountName / demoAccountPassword）
   - 用**真能登的账号**，不要 placeholder
   - 测试前自己登一遍验证

2. **Review Notes（reviewNotes 字段，约 4000 字符）** —— 至少包含：
   - **从启动到核心功能的路径**，用 1/2/3 步骤式写法，例如：
     ```
     1. Launch app, sign in with demo account
     2. Tap "我的" tab at bottom right
     3. Tap settings icon top right
     4. Scroll to bottom, tap "Upgrade to Pro"
     5. Subscription page visible with ¥28/month and ¥288/year
     ```
   - **如有 IAP / 订阅**：每个 SKU 对应什么权益（表格更清晰）
   - **如有隐藏入口**：明确说明触发条件（"该功能仅在连接蓝牙设备后出现"）
   - 中英文都写更稳妥

3. **演示视频附件**（App Review Attachment，≤ 500 MB mp4/mov） —— 满足下面任一条件**强烈建议**主动上传：
   - 核心功能复杂（AI 类、工具类、需硬件配合）
   - 含订阅 / 内购（**几乎必传**，详见下方）
   - 用户从启动到看到核心价值超过 3 步

### 订阅类 App 的特别要求

订阅类 App 是 2025 年拒审重灾区。演示视频**必须**完整覆盖：
- Paywall 页面：周期 / 价格 / "自动续期"字样 / ToS 链接 / Privacy Policy 链接 / **Restore Purchases 按钮**
- 完整支付流程（包括 Apple 原生支付 sheet，不要剪掉）
- 试用期 / introductory offer 转付费的时点说明

Review Notes 里同时附上每个 SKU 的权益表 + 取消订阅路径说明（"通过 Settings → Apple ID → Subscriptions 管理"）。

### Pro tip
把 Review Notes 当成"给 5 分钟前刚下载 App 的陌生人写的快速上手指南"，过审率立即提升。这条同样适用于演示视频解说。

## 发布策略（用户在 ASC 网页提审时一并选定）

- `MANUAL` — 审核通过后手动点发布
- `AFTER_APPROVAL` — 审核通过自动发布
- `SCHEDULED` — 指定时间发布（带时区）
- 分阶段发布：在 ASC 网页里勾选（API 也支持 `POST /v1/appStoreVersionPhasedReleases`）

skill 可以在 `POST /v1/appStoreVersions` 时把 `releaseType` 一并填好，但**最终提审是用户手动**，所以建议把这个选择留给用户在 ASC 网页确认。

## 步骤汇总

1. 列 App 所有 App Store 版本，确认是新增还是更新
2. 询问 versionString（默认从 ipa Info.plist 取 MARKETING_VERSION）
3. 跑 `../checklists.md` 自检（首次 / 更新二选一）
4. 调上述 ASC API 调用链 1–6 推数据
5. **停下来**，输出 ASC 后台 URL，提示用户去后台亲手点 Submit for Review
6. 用户提审后，可以切到 `watch.md` 跟踪状态

## 脚本
- `../scripts/submit_upload_screenshots.py` — 截图批量上传到指定 screenshot set（**已收录**；封装了 reservation→分块 PUT→commit 这段易错流程）。用法：
  ```bash
  ../scripts/submit_upload_screenshots.py --set-id <screenshotSetId> screenshots/final/iphone-6.9/en-US/
  ```
  > screenshot set 的查询/创建（`GET`/`POST /v1/appScreenshotSets`）很简单，由 AI 现场完成后把 set-id 传进来。
- 调用链 1–6 的其余步骤（建版本 / 绑 build / 推 metadata / 审核信息）无预置脚本，AI 按上方 API 调用链现场实现，token 用 `../scripts/asc_mint_jwt.py` 签。
  ⚠️ **现场实现时绝不调 `POST /v1/appStoreVersionSubmissions`**（那是最终提审，留给用户手点）。

## 参考
- https://developer.apple.com/documentation/appstoreconnectapi/app_store/managing_app_store_versions
- 完整 checklist 见 `../checklists.md`
