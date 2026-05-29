# Stage: Metadata（元信息准备）

为新 App 或新版本生成 ASC 元信息脚手架。

## 生成内容（按 ASC 字段对齐）

**App Information（一次性）**
- Name（30 字符上限，**全局唯一**——见下方"名称占用对策"）
- Subtitle（30 字符上限，无唯一性要求）
- Primary Category / Secondary Category
- Privacy Policy URL（必填）
- Support URL（必填）
- Marketing URL（可选）

### 名称占用对策（App Name 全局唯一）

App Name 在整个 ASC 全球唯一——你想叫 "Notes"，但已经被 Apple 自家或别人占了，会直接报：
> The App Name 'Notes' is not available. Please enter a different name.

被占了**只能改**。indie 圈最常见的几种处理：

| 形式 | 例子 | 备注 |
| --- | --- | --- |
| `Name - Tagline`（**最推荐**） | `Notes - Quick Capture` | Apple 自己很多 App 也这么用，看起来自然 |
| `Name: Subtitle` | `Notes: Daily Journal` | 紧凑一些 |
| `Name for X` | `Notes for Writers` | 限定用途，差异化清晰 |
| `Name App` / `Name —` | `Notes App` / `Notes —` | 较弱，凑数感强，不推荐 |

**建议做法**：
1. 想好理想名后，**先去 App Store 搜一下**——能搜到同名 App，就基本被占了
2. 在 ASC 创建 App 记录时（"My Apps → +"），输入 Name 即时校验，被占会立即告知
3. 想注册但还没准备好提审的名字，可以**先创建 App 记录占住**（创建后名字保留期较长；如果一直不提审，Apple 会在 180 天后回收）
4. 取名时把"差异化后缀"也算进 30 字符上限：`Notes - Quick Capture` 是 21 字符，刚好
5. **Subtitle 不受唯一性约束**，可以放最想说的卖点——这是被 Name 唯一性逼出来的设计

> 注意：取名时**不能蹭品牌**——比如 `Notes for Apple` / `WeChat Helper` 这种含他人商标的会被 Guideline 5.2.1 拒。差异化后缀应该是描述功能或定位，不是借光。

## 法律文档 — Privacy Policy & EULA

两个边界完全不同：

| 文档 | Apple 默认 | 必须自己准备吗 |
| --- | --- | --- |
| **Privacy Policy（隐私政策）** | ❌ **没有官方默认** | ✅ **必须自己写 + 自己托管** |
| **EULA / Terms of Use（用户协议）** | ✅ 有 [Apple Standard EULA](https://www.apple.com/legal/internet-services/itunes/dev/stdeula/) | 不强制，多数 App 用 Apple 默认即可 |

### Privacy Policy（必填）

ASC 必填字段 `Privacy Policy URL`。Apple 不给默认版，用户必须自己写一份并托管在公网可访问的 URL。

**托管方案**（indie 圈常用）：
- **GitHub Pages**（免费，建议） — 起一个 `<user>.github.io/<app>` 仓库，写 `privacy.md`
- **Notion Sites**（免费 / 入门付费） — Notion 公共页面发布即得 URL
- **自有域名静态站** — Vercel / Netlify / Cloudflare Pages 免费托管
- **专门生成器**：PrivacyPolicies.com / Termly / iubenda（含模板 + 托管，有免费档）

**内容必须包含**（否则 Guideline 5.1.1 拒）：
1. 收集哪些数据（要跟 ASC App Privacy 问卷 + `PrivacyInfo.xcprivacy` **一致**）
2. 用途（功能 / 分析 / 广告）
3. 是否与第三方共享、共享给谁
4. 用户怎么联系你删除数据 / 行使权利
5. 数据保留期限
6. 更新日期

**文件位置**：
本仓库不替你写 Privacy Policy（每个 App 内容不同），但建议把 URL 记到 `<项目名>-appstoreconnect/metadata/<locale>/privacy_url.txt`，方便所有 locale 复用同一份 URL（也可以每个 locale 各自托管对应语言版本）。

### EULA / Terms of Use（可不写，Apple 默认兜底）

ASC 字段：App Information → License Agreement。不填则自动套用 **Apple Standard EULA**：
- URL: https://www.apple.com/legal/internet-services/itunes/dev/stdeula/
- 内容：含禁止逆向工程 / 责任限制 / Apple 作为第三方受益人 等通用条款
- 完全够 95% 的 App 用

**什么时候需要自定义 EULA**：
- App 有特殊责任划分（用户产生内容 UGC / 在线社区 / 涉医疗法律金融建议）
- 订阅条款想自己定义续期 / 退款规则（罕见，多数情况 Apple 标准够）
- 公司法务要求

自定义就上传一份 RTF / PDF 到 ASC，或托管在自有 URL。

### 订阅类 App 的 Paywall 要求（Guideline 3.1.2）

订阅类 App 的 paywall 上**必须有可点击的**：
- **Terms of Service 链接** —— 用 Apple Standard EULA URL 就够，或链到自定义 EULA URL
- **Privacy Policy 链接** —— 必须链到你自己的隐私政策

两个链接缺一就拒。详见 `submit.md` "订阅类 App 的特别要求"段。

### 中国大陆地区特别要求

- 隐私政策**必须有中文版本**（reviewer 在中国区会要求）
- 域名：托管隐私政策的域名**可以**不备案（只要 App 本身备案了即可），但 GitHub Pages 等境外站点在中国大陆访问偶尔会慢/挂，建议有中国大陆访问需求时也准备国内可访问的镜像（gitee pages / 阿里云 OSS）

### Checklist 关联

完整提审前自检见 `../checklists.md` 中 "Metadata" 和 "中国大陆地区" 两组。

**Version Information（每个版本）**
- Promotional Text（170 字符，可在不重新提审下更新）
- Description（4000 字符，**末尾建议附 Privacy Policy + Terms of Use URL**——详见下方"Description 末尾的法律链接约定"）
- Keywords（100 字符，逗号分隔，不要加空格——空格也算字符）
- What's New in This Version（4000 字符）
- Support URL

### Description 末尾的法律链接约定

- **订阅类 App 几乎必须**：reviewer 在中国区尤其会主动找；不附直接打回让你"在描述里加上法律链接后重提"
- **非订阅 App 也强烈推荐**：用户和 reviewer 不用跳出 App Store 详情页就能看到法律链接，过审顺滑

模板（贴到 description.txt 末尾）：
```
─────────────
隐私政策 / Privacy Policy: https://your-domain.com/privacy
用户协议 / Terms of Use: https://www.apple.com/legal/internet-services/itunes/dev/stdeula/
```

> 用户协议链接如果你没自定义 EULA，直接用 Apple Standard EULA URL 即可。详见下方"法律文档"段。

## 步骤

1. 问清 App 定位、目标用户、核心卖点 3 条
2. 询问要支持的语言（默认 en-US + zh-Hans）
3. 为每个语言生成 `<项目名>-appstoreconnect/metadata/<locale>/*.txt`（与 fastlane deliver 兼容的目录结构）
4. 自动做字符数校验，超长立即报错
5. 关键词去重 + 去空格

## 输出结构

**统一写到项目的 `<项目名>-appstoreconnect/metadata/`** 下（约定见 SKILL.md 顶部）：
```
<项目名>-appstoreconnect/metadata/
├── en-US/
│   ├── name.txt
│   ├── subtitle.txt
│   ├── description.txt
│   ├── keywords.txt
│   ├── release_notes.txt
│   ├── promotional_text.txt
│   ├── marketing_url.txt
│   ├── privacy_url.txt
│   └── support_url.txt
└── zh-Hans/
    └── ...
```

这套目录跟 fastlane deliver 兼容，老版本文件保留即可——下次发版只需更新 `release_notes.txt` 等增量字段。

## 中国大陆地区特别项 — ICP 备案号（**上架中国区必填**）

自 2023-09-29（新 App）/ 2024-04-01（存量 App）起，Apple 强制要求中国大陆区上架的 App 必须填写 **ICP 备案号**，否则上架中国区会被拒。

### 在 ASC 哪填
- **App Information → Localizable Information → Chinese (Simplified)**
- 字段名："中国大陆地区上架许可证编号"（ICP License Number）
- 格式示例：`京ICP备12345678号` 或 `沪ICP备20240001号-1A`

### 文件位置
本 stage 在 `<项目名>-appstoreconnect/metadata/zh-Hans/` 下额外建一个：
- `icp_number.txt` — 一行，备案号字符串

`submit.md` 推送 zh-Hans localization 时会一并 PATCH 这个字段。

### 备案本身怎么搞（**skill 不替你做**）
ICP 备案是工信部那边的独立流程，跟 ASC 无关。Apple 只是"把已有备案号填进来"。备案路径：
1. 选一家"接入服务商"——阿里云 / 腾讯云 / 七牛云 / 华为云等
2. 在服务商网站提交 **App 备案**申请（不是网站备案，是 App 备案）
3. 提交主体材料（公司营业执照 / 个体户营业执照 / 大陆居民身份证）+ App 材料（包 + 描述 + 域名）
4. 审核周期：通常 2–4 周
5. 通过后拿到备案号

**指引**：
- 工信部入口：https://beian.miit.gov.cn/
- 没有公司营业执照的个人开发者：以**个体工商户**身份备案是目前唯一路径（注册个体工商户成本约 ¥200–500）

### 不上架中国大陆怎么办
ASC 后台 → Pricing and Availability → 把 China 取消勾选即可。skill 在准备 metadata 时会问用户"是否上架中国大陆"，回答"否"则跳过 ICP 字段。

## 脚本
- `../scripts/validate_lengths.py <metadata 根目录>` — 逐 locale 校验各字段字符数上限（name 30 / subtitle 30 / keywords 100 / description 4000 …），并提示关键词空格浪费（**已收录**，超限退出码 1）。用法：
  ```bash
  ../scripts/validate_lengths.py <项目名>-appstoreconnect/metadata/
  ../scripts/validate_lengths.py <项目名>-appstoreconnect/metadata/ --locale zh-Hans
  ```
- 目录结构创建无需脚本，AI 现场 `mkdir -p` + 写 `.txt` 即可。

## 参考
- https://developer.apple.com/help/app-store-connect/reference/app-information
