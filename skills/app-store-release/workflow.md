# 典型上架工作流

> 所有路径相对 skill 根（即 `skills/app-store-release/`）。

## 阶段 0 — 一次性准备

- `stages/asc-auth.md` — 配置 `~/.appstoreconnect/`（ASC API Key）
- 触发本 skill 后 AI 会先跟用户对齐**材料存储位置**（默认 `<项目名>-appstoreconnect/`，详见 `SKILL.md` 顶部"项目目录约定"）
- 营销图制作不需要配 OpenAI API Key——出图由用户在 Codex / ChatGPT 图片模式里完成

## 阶段 1 — 立项 & 素材准备

```
stages/metadata.md             起多语言文案
stages/privacy.md              扫 SDK、做隐私问卷、生成 PrivacyInfo.xcprivacy
stages/iap.md                  （如有内购）配置商品
preview-studio/overview.md     六阶段引导式制作预览图：
                                 ① 读项目定义建立 App 画像
                                 ② 讨论确定视觉风格
                                 ③ 生成基础 prompt 套件
                                 ④ 收集 base 截图（手动 / simctl 自动）
                                 ⑤ 逐张确定文案与重点
                                 ⑥ 产出最终 prompt 包，用户拿到 Codex 出图
stages/screenshots.md          校验出图规格（sRGB / 无 alpha / 尺寸）
```

## 阶段 2 — 出包

```
stages/signing.md              签名出错时跑
stages/version-bump.md         bump build number
stages/export-compliance.md    Info.plist 加 ITSAppUsesNonExemptEncryption
stages/build.md                打 ipa（macOS 含公证）
```

## 阶段 3 — 上传 & 准备审核（最终提审由用户手动）

```
stages/upload.md               上传 ipa + 等处理 + 分发到内部组
                               （内部测试一轮后…）
checklists.md                  跑一遍首次提审清单 / 版本更新清单
stages/submit.md               通过 API 把 metadata / 截图 / Review Notes 推到 ASC
                               ⚠️ 完成后停下来，给用户 ASC 后台 URL，
                                  用户亲手点 Submit for Review（不可逆，不让 AI 替按）
stages/watch.md                提审后挂着轮询，状态变化推送
```

## 阶段 4 — 万一被拒（小概率）

如果上述流程走扎实（隐私 / 元信息 / 加密合规 / 截图规格 / Review Notes / 演示视频 都达标），首次过审率本来就高。
真被拒：让 Claude 直接读 reviewer 邮件原文 + Apple Guidelines 公开文档现答即可，本 skill **不预置 playbook**。改完代码回阶段 2 重新打包。

## 串行调用示意

在 Claude Code 里就是连续自然语言：

> "帮我准备新版本 1.3.0 的上架。当前在 Xcode 项目根目录。"

Claude 触发本 skill，**先跟用户确认材料目录位置**，然后根据"上架新版本"判断需要走的 stage，按序 Read：
`version-bump.md` → `export-compliance.md` → `build.md` → `upload.md` → 等用户确认 → `submit.md` → `watch.md`。
