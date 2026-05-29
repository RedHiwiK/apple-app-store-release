# apple-app-store-release

面向 iOS 独立开发者的 **Apple App Store 上架 Skill**（iPad / macOS 同理）。

**兼容 Codex / ChatGPT（推荐）以及 Claude Code**——只要是支持自定义 skill / 自然语言驱动文件操作的 AI 工具都能跑。

## 这是什么

一个自包含的上架 skill，覆盖从准备文案到上架审核的完整流程：

- 元信息（Name / Subtitle / Description / Keywords / What's New / 多语言 / 中国大陆 ICP 备案号 / 法律链接）
- 隐私清单（PrivacyInfo.xcprivacy + ASC App Privacy 问卷）
- 内购 / 订阅配置
- 加密合规
- Xcode 打包 + 签名诊断 + 版本号管理
- TestFlight 上传 + 处理状态轮询
- 通过 ASC API 把审核数据推到 ASC，最终 Submit for Review **由用户在 ASC 后台亲手点**（不可逆，不替用户做）
- 审核状态追踪
- **营销预览图引导式制作**（无需 OpenAI API Key）
- **提审前自检清单**（首次提审 + 版本更新两份，含 2025 高频拒审原因 Top 13）

跟 Xcode 项目根平级建一个 `<项目名>-appstoreconnect/` 目录，所有发版材料**持续维护**在里面——首次上架建立，后续每次发版回来更新增量。

## 推荐使用 Codex（端到端，含出图）

| 工具 | 端到端体验 | 备注 |
| --- | --- | --- |
| **Codex / ChatGPT（推荐）** | ✅ 一气呵成 | **自带图像生成**：营销图制作的 Phase 6 可以直接出图、归档，不需要任何手动跳工具 |
| Claude Code | ⚠️ 出图前需要换工具 | 无原生出图能力，营销图流程跑到 prompt 包齐为止；最后一步用户拿 prompt 到 Codex / ChatGPT 图片模式出图，再归档回项目目录 |

发版 / 打包 / 上传 / 提审等**非出图**操作两个工具都能完整跑。

## 安装

### Codex / ChatGPT
按你所用的 Codex 客户端的 skill 装载方式，把仓库的 `skills/app-store-release` 目录注册为可用 skill 即可。Codex 触发后会自动读取 `SKILL.md` 并按路由表工作。

### Claude Code
```bash
git clone https://github.com/RedHiwiK/apple-app-store-release.git ~/code/apple-app-store-release
mkdir -p ~/.claude/skills
ln -s ~/code/apple-app-store-release/skills/app-store-release ~/.claude/skills/
```

软链方式后续**拉更新**只需进 clone 目录 `git pull`（软链指向同一份文件，自动生效）。

> 想要"一行命令安装 + 自动收更新"的体验，可以进一步把本 repo 包装成 Claude Code Plugin（`/plugin marketplace add RedHiwiK/apple-app-store-release`）——非必需，当前软链方式已可用。

## 用法示例

自然语言触发，例如：
- "帮我把当前 Xcode 项目打包成 ipa"
- "上传到 TestFlight"
- "用 AI 给我生成 App Store 截图"
- "我要发新版本 1.3.0，端到端做完"
- "提审前我准备好了吗？给我看清单"

AI 触发 skill 后会先跟你对齐**发版材料存储位置**（默认 `<项目名>-appstoreconnect/`），再按需读取对应阶段文档。

## 凭据存放约定

**绝不入库**。敏感凭据放用户家目录：

```
~/.appstoreconnect/
├── AuthKey_XXXXXXXXXX.p8      # ASC API Key（用 .p8 + JWT 签名）
└── config.json                # { "key_id":..., "issuer_id":..., "key_path":... }
```

营销图制作**不需要任何 API Key**——出图能力来自驱动 skill 的 AI 工具本身（Codex / ChatGPT 自带；Claude Code 无原生出图，需要把 skill 产出的 prompt 包带到 Codex / ChatGPT 完成最后一步）。

`.gitignore` 拦截了 `*.p8 / *.p12 / *.cer / *.mobileprovision / .env*` 等敏感文件。

## 项目资料目录约定

**所有发版材料（metadata / 截图 / IAP 配置 / Review Notes / 演示视频 / ipa 产物等）统一放在 `<项目名>-appstoreconnect/`**，跟 Xcode 项目根平级。详见 [`skills/app-store-release/SKILL.md`](skills/app-store-release/SKILL.md) 顶部"项目目录约定"段。

这个目录是**持续维护的资料底账**：首次上架建立，后续每次发版回来更新增量。

## 仓库布局

```
apple-app-store-release/
├── README.md                       # 本文件
├── .gitignore
└── skills/
    └── app-store-release/          # 唯一的 skill
        ├── SKILL.md                # 入口路由
        ├── workflow.md             # 典型上架工作流
        ├── checklists.md           # 提审前自检 + 2025 高频拒审 Top 13
        ├── faq.md                  # 30+ 高频问题
        ├── stages/                 # 12 个发版阶段文档
        ├── preview-studio/         # 营销预览图制作子区
        │   └── overview.md         # 六阶段流程
        └── scripts/                # 5 个核心脚本（JWT 签名 / 截图上传 / 截图校验 / 字符数校验 / profile 解析）；其余步骤 AI 现场实现
```

## 平台说明

- iOS / iPadOS 共用 ipa 流程
- macOS：`xcodebuild -destination 'generic/platform=macOS'` + `notarytool` 公证，详见 `stages/build.md`
- visionOS：尺寸表已含，构建流程同 iOS

## 关键安全边界

**最终的 "Submit for Review" 由用户在 ASC 后台亲手点**——skill 通过 API 把所有审核数据（metadata / 截图 / Review Notes / 演示视频）推到 ASC，**然后停下来**给用户一个后台 URL 让用户去 review 并提审。提审是不可逆操作，不让 AI 替按。

## 拒审预防 ≫ 拒审应对

仓库**不预置拒审 playbook**。定位是"把发版做扎实"——`checklists.md` 顶部的 Top 13 高频拒审原因 + 完整自检清单覆盖了 80%+ 的拒审场景。真被拒的小概率事件：让 AI 直接读 reviewer 邮件原文 + Apple Guidelines 公开文档现答即可。

## License

[MIT](LICENSE) © 2026 sikunhong。可自由使用、修改、商用，保留版权声明即可。
