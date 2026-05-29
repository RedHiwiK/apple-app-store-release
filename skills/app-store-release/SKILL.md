---
name: app-store-release
description: iOS/iPadOS/macOS App Store 上架全流程——元信息、隐私清单、Xcode 打包、签名诊断、版本号管理、加密合规、内购配置、TestFlight 上传、提交审核、审核状态追踪，以及营销预览图的引导式制作。当用户提到"上架"、"上传 TestFlight"、"提审"、"submit for review"、"打包 ipa"、"archive"、"xcodebuild"、"ASC API"、"App Store Connect"、"签名错误"、"profile"、"version bump"、"build number"、"What's New"、"App 隐私"、"PrivacyInfo.xcprivacy"、"加密合规"、"ITSAppUsesNonExemptEncryption"、"内购"、"IAP"、"订阅"、"做 App Store 截图"、"营销图"、"预览图"、"AI 出图"、"App Icon 设计"等场景时触发。
---

# app-store-release

iOS 独立开发者的 App Store 上架流水线。iPad / macOS 同理（macOS 多一步公证）。

## 项目目录约定（重要）

**所有发版材料统一放在一个项目专属目录里**，跟 Xcode 项目根平级，**绝不放进 skill 仓库本身**。

### 触发本 skill 后第一件事：确认材料存储位置

AI 在执行任何具体阶段操作前，**必须先跟用户对齐材料存储位置**：

1. 默认位置：`<Xcode 项目名>-appstoreconnect/`，跟 Xcode 项目根平级（例如 `~/MyApp/MyApp-appstoreconnect/`）
2. 主动询问用户："发版材料默认放到 `<Xcode 项目名>-appstoreconnect/`，需要改到别的位置吗？"
3. 用户回复后：
   - 同意默认 → 后续所有 stage 用这个路径
   - 指定别的路径 → 用用户指定的路径
4. **位置一旦确认，整个会话沿用，不要每个 stage 再问一次**

这样：
- 多个 App 同时维护不会串味
- 仓库本身保持纯净
- 用户切到任何一个项目目录，AI 都能找到该项目专属的发版资产
- 用户也能选择把材料放别的位置（比如统一的 `~/AppStore-Materials/MyApp/`）

标准结构（按需创建，不必一开始就全建）：
```
~/MyApp/                          ← Xcode 项目根
├── MyApp.xcodeproj
├── MyApp/                        ← 源码
└── MyApp-appstoreconnect/        ← 本约定的目录，所有发版材料在这
    ├── metadata/                 ← ASC 文案（per-locale）
    │   ├── en-US/
    │   └── zh-Hans/
    ├── screenshots/              ← App Store 营销截图
    │   ├── base/                 ← 模拟器/真机原始截图（preview-studio Phase 4）
    │   └── final/                ← AI 出图后的最终图（per-platform per-locale）
    ├── prompts/                  ← preview-studio 产物
    │   ├── _skeleton/
    │   └── final/
    ├── style.yaml                ← 营销图 Style DNA
    ├── copy.yaml                 ← 每张图的文案
    ├── iap-config.yaml           ← 内购商品配置
    ├── iap-screenshots/          ← 内购审核截图（可选）
    ├── review/
    │   ├── notes.md              ← Review Notes 内容（提审用）
    │   └── demo-video.mp4        ← 演示视频
    ├── privacy-answers.md        ← ASC 隐私问卷答案备份
    └── build/                    ← 打包产物
        ├── MyApp.xcarchive
        └── MyApp.ipa
```

> `PrivacyInfo.xcprivacy` 是例外：它必须**进 Xcode 项目本身**才能打进 ipa，不放这个目录。

**这个目录的定位是"持续维护的资料底账"**：
- 第一次上架时建立，**每次发新版本回来更新**（不是 throw-away 输出）
- 旧版本的 metadata / 截图 / Review Notes 都保留——下次发版时大部分可复用，只改增量
- 多 App 工作时不会混；切到任何项目目录，AI 都能定位到该项目专属的发版资产
- 跟 Xcode 项目一起 git 管理（**敏感信息除外**：`.p8` / `demo-video.mp4`（含演示账号操作）等不要入库）

后续所有 stage 文档里引用路径时，统一用 `<项目名>-appstoreconnect/...` 形式。AI 触发时先确认项目名（默认取 Xcode 项目名），再展开实际路径。

## 这个 skill 怎么用

SKILL.md 是入口路由，**不要把所有阶段细节读进上下文**。先判断用户当前在哪一步，再 Read 对应 stage 文件。

| 用户场景关键词 | 读这个文件 |
| --- | --- |
| **完整发版** / 发新版本 / 端到端流程 / "帮我发 1.x.x" | 先读 `workflow.md`，按阶段顺序依次读对应 stage |
| 做 App Store 截图 / 营销图 / 预览图 / AI 出图 / App Icon 设计 | `preview-studio/overview.md` |
| 准备文案 / What's New / 多语言描述 / 关键词 | `stages/metadata.md` |
| 截图**规格** / 校验图片 / sRGB / 8MB 上限 / 像素尺寸 | `stages/screenshots.md` |
| App 隐私 / PrivacyInfo.xcprivacy / nutrition label / SDK 隐私 | `stages/privacy.md` |
| 内购 / IAP / 订阅 / price tier | `stages/iap.md` |
| 打 ipa / archive / xcodebuild | `stages/build.md` |
| 签名错误 / profile 不匹配 / entitlements | `stages/signing.md` |
| 升版本号 / bump version / 改 build number | `stages/version-bump.md` |
| 加密合规 / ITSAppUsesNonExemptEncryption / ERN | `stages/export-compliance.md` |
| 配 ASC API / .p8 / JWT / 401 | `stages/asc-auth.md` |
| 上传 TestFlight / altool / Transporter | `stages/upload.md` |
| 提审前自检 / 上架检查清单 / 常见拒审原因 / "我准备好了吗" / "上线前要看的" | `checklists.md` |
| 提交审核（准备数据，**不替用户点最终提审**） / submit for review | `stages/submit.md` |
| 审核状态 / review status / 审核到哪了 | `stages/watch.md` |

如果一次请求横跨多个阶段（"帮我打包并提交"），按顺序读相关 stage 文件，但每次只读 1–2 个，避免上下文爆掉。

## 凭据约定

ASC API Key 统一放 `~/.appstoreconnect/`：
```
~/.appstoreconnect/
├── AuthKey_XXXXXXXXXX.p8
└── config.json   # {"key_id":"...","issuer_id":"...","key_path":"..."}
```

**绝对不入库**（仓库 `.gitignore` 已拦截 `.p8 / .p12 / .cer / .mobileprovision`）。

## 内部资源索引

- 完整工作流：`workflow.md`
- 提审前自检清单（首次 / 版本更新）：`checklists.md`
- 常见问题：`faq.md`
- 营销预览图制作：`preview-studio/overview.md`（六阶段引导式流程）

## 关键安全边界

**最终的 "Submit for Review" 由用户在 ASC 后台亲手点**，skill 不替用户做这一步。skill 只负责把所有审核数据通过 API 推到 ASC，然后停下来给用户一个后台 URL 让用户去 review 并提审。详见 `stages/submit.md`。

## 拒审预防 ≫ 拒审应对

仓库定位是"上架做扎实"。`checklists.md` 顶部列了 **2025 高频拒审原因 Top 13**，覆盖 80%+ 的拒审场景，每条都对应清单里某个分组——AI 在 `submit.md` 准备数据前必须带用户走一遍这份清单。

真被拒的小概率事件：让 Claude 直接读 reviewer 邮件原文 + Apple Guidelines 公开文档现答即可，本仓库不预置 playbook。

