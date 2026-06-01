# Checklists — 提审前自检清单 + 常见拒审原因

两份独立的清单：**首次提审** 跟 **版本更新**。AI 在 `submit.md` 准备数据前会带用户走对应的一份。

> 不强求每项都打勾——但每项都应该问一遍。空着的项必须有意识地知道为啥空着。

---

## 0、为什么要走清单 — 2025 高频拒审原因 Top 13

按实际命中率排序（综合 indie 圈反馈 + 公开数据），下面 13 条占了 **80%+** 的拒审。**每条都对应下面清单里某个分组**——走完清单等于把这些雷区都扫了一遍。

| # | 高频拒审原因 | Guideline | 关联清单分组 |
| --- | --- | --- | --- |
| 1 | 缺核心功能演示视频（**首次提审基本必传**，2024 起 reviewer 默认会要） | 2.1 | "审核信息" |
| 2 | 订阅 Paywall 缺 Restore Purchases / per-month / 自动续期字样 / ToS Privacy 链接 | 3.1.2 | "订阅类 App 特别项" |
| 3 | Demo 账号登不上 / 不存在 / 密码错 | 2.1 | "审核信息" |
| 4 | Review Notes 太糊弄 / 没有从启动到核心功能的路径步骤 | 2.1 | "审核信息" |
| 5 | Privacy Policy URL 不可访问 / 404 / 内容跟实际收集不符 | 5.1.1 | "Metadata" |
| 6 | ASC App Privacy 问卷 vs `PrivacyInfo.xcprivacy` vs 实际收集 **三方不一致** | 5.1.1 | "ASC App Privacy 问卷" |
| 7 | `PrivacyInfo.xcprivacy` 没建 / 第三方 SDK（Firebase / Sentry 等）没声明 | 5.1.1 | "项目代码 & 配置" |
| 8 | `Info.plist` 缺必要的 `NSXxxUsageDescription`（相机/相册/定位/麦克风/通讯录） | 5.1.1 | "项目代码 & 配置" |
| 9 | 中国大陆区 ICP 备案号没填 / 主体不符 / App 名跟备案不一致 | 区域强制 | "中国大陆地区" |
| 10 | reviewer 测试中 App 崩溃 / 关键功能不可用 | 2.1 | "Build & TestFlight" |
| 11 | IAP 审核截图多个 SKU 共用同一张 / 看不出对应订阅周期 | 2.3.10 | "IAP" |
| 12 | `ITSAppUsesNonExemptEncryption` 未在 Info.plist 声明 | 5.5 | "加密合规" |
| 13 | App Name 蹭他人品牌（`for Apple` / `WeChat Helper` 等） | 4.3 / 5.2.1 | "Metadata" |

**怎么用这张表**：
- **用户自己**提审前把这张表 + 下面的清单完整过一遍（AI **不主动**逐条审问；用户问到某一条时 AI 按对应分组解答）
- 任一条没把握 → 跳到对应清单分组逐项确认
- 走完清单再让 `submit.md` 推 ASC

---

## 一、首次提审清单（覆盖一切）

### Apple 开发者后台 & ASC 基础设施
- [ ] Apple Developer Program 会员已激活（年费 $99 已付）
- [ ] Bundle ID 在 Certificates, Identifiers & Profiles 已注册
- [ ] 必要的 Capabilities 都已启用（Push / iCloud / Sign in with Apple / App Groups 等）
- [ ] ASC 后台 App 记录已创建，拿到 App ID（SKU + Primary Language 都填了）
- [ ] **（若用 CloudKit）schema 已在 CloudKit Console 从 Development「Deploy 到 Production」**（[icloud.developer.apple.com](https://icloud.developer.apple.com/) → 选 container → Deploy Schema Changes…；Development schema 不会自动同步到 Production，漏做会导致正式用户报 record type / field 不存在；**无公开 API，只能在 Console 手动点**，`xcrun cktool export-schema/import-schema` 只能管 schema 文件本身，不做环境 promote）

### 项目代码 & 配置
- [ ] `PrivacyInfo.xcprivacy` 已建（Xcode 15+ 必须，含第三方 SDK 的隐私声明）
- [ ] `Info.plist` 含 `ITSAppUsesNonExemptEncryption` 声明（true / false 都行，**不能不写**）
- [ ] `Info.plist` 含必要的 `NSXxxUsageDescription`（每个用到的相机/相册/定位/麦克风/通讯录等都要写）
- [ ] App Icon 在 Asset Catalog 配齐了所有尺寸（特别是 1024×1024 store icon）
- [ ] Launch Screen / Storyboard 已配置（不能用纯黑或空白）
- [ ] 支持 iPad 的话：iPad 适配测试过（横竖屏、Split View）
- [ ] 支持 Dark Mode 的话：暗色模式无破版

### Metadata（每个上架的 locale 一份）
- [ ] Name (30 字符内，**已确认全局唯一可用**——ASC 创建 App 记录时即时校验；被占了用 `Name - Tagline` 等形式加后缀，详见 `stages/metadata.md`)
- [ ] Subtitle (30 字符内，无唯一性要求，放最想说的卖点)
- [ ] Description (4000 字符内)
- [ ] Keywords (100 字符内，逗号分隔无空格)
- [ ] Promotional Text (170 字符内)
- [ ] What's New (4000 字符内，首版可以写"Welcome to xxx")
- [ ] **Description 末尾附 Privacy Policy URL + Terms of Use URL**（订阅 App **几乎必须**；其他 App 也强烈推荐——用户和 reviewer 不用跳出 App Store 详情页就能看到法律链接）
- [ ] **Privacy Policy URL 可访问**（必填，**Apple 无默认必须自己托管**——GitHub Pages / Notion / Vercel 都行）
- [ ] Privacy Policy 内容跟 ASC App Privacy 问卷 + `PrivacyInfo.xcprivacy` **三方一致**
- [ ] **EULA / Terms of Use**：决定用 Apple Standard EULA（不填即默认）还是自定义；订阅 App 的 paywall ToS 链接已确认
- [ ] Support URL **可访问**（必填）
- [ ] （可选）Marketing URL

### 截图（按 `screenshots.md` 规格）
- [ ] iPhone **6.9"** 至少一组（1320×2868，**必传**）
- [ ] 支持 iPad 的话：iPad **13"** 至少一组（2064×2752）
- [ ] 支持 macOS / visionOS 的话：对应尺寸至少一组
- [ ] 截图均通过校验：sRGB / 无 alpha / 像素尺寸严格 / ≤ 8MB
- [ ] 每个 locale 都有对应语言的截图（或确认共用英文截图）

### IAP（如有内购 / 订阅）
- [ ] ASC 后台 IAP 商品已创建（Product ID 永久不可改，想清楚再创建）
- [ ] 每个商品有 Localization（每个 locale 的 Display Name + Description）
- [ ] Price tier 已设
- [ ] 订阅必须放进 Subscription Group
- [ ] 订阅商品的 Family Sharing 开关明确设置
- [ ] 审核截图（可选，传了就要满足"能看出 SKU"+"不同 SKU 不共用图"两条铁律）

### 订阅类 App 特别项（拒审重灾区）

**订阅入口 & 文档明确性**
- [ ] **Review Notes 明确写出订阅 Paywall 的进入路径**（启动到 Paywall 的具体 1/2/3 步骤，参考上面"审核信息"组）
- [ ] **演示视频完整录到 Paywall 出现 → 完整支付流程 → 解锁内容**（缺一就拒；详见 `stages/submit.md` "订阅类 App 的特别要求"段）
- [ ] Description 末尾 / Promotional Text 里附 Privacy Policy + ToS 链接

**Paywall 视觉必含元素（缺一拒）**
- [ ] Paywall 上有 Restore Purchases 按钮（**几乎必拒项**）
- [ ] Paywall 上订阅周期清晰可见（"per month" / "monthly" 字样）
- [ ] Paywall 上明确"自动续期"字样
- [ ] Paywall 上有可点击的 Terms of Service 链接
- [ ] Paywall 上有可点击的 Privacy Policy 链接
- [ ] App 内有文字说明取消订阅路径（"Settings → Apple ID → Subscriptions"）
- [ ] 试用期 / introductory offer 转付费时点已明确

### 审核信息（Review Information）
- [ ] **演示账号已创建并能登录**（自己测一遍）
- [ ] Review Notes 含从启动到核心功能的 1/2/3 步骤路径
- [ ] **若含 IAP / 订阅**：Review Notes 明确写**如何从启动进入 Paywall**（具体 1/2/3 步骤，不能只说"在某个 tab"——例如 "启动 → 用演示账号登录 → 点'我的' Tab → 设置 → '升级 Pro'"）
- [ ] Review Notes 含每个 IAP SKU 对应的权益说明
- [ ] Review Notes 如有隐藏入口（蓝牙、定位等）已说明触发条件
- [ ] Review Notes 中英都写
- [ ] **首次提审：演示视频必传**（不是"建议"——2024 年起 reviewer 默认会主动要，首次没传几乎必被卡）
  - 规格：≤ 500MB mp4/mov，1080p / 30fps，时长 30–90 秒
  - 内容：启动 → 进入核心功能 → 完成一次完整流程 → 看到结果
  - 含订阅 / 复杂功能 / 多步流程的尤其必传
- [ ] 联系人 Phone / Email 真能联系上你（拒审时 Apple 会用）

### ASC App Privacy 问卷
- [ ] 问卷已填，跟 `PrivacyInfo.xcprivacy` 内容**一致**（不一致必拒）
- [ ] Data Types 每项都明确：是否收集、用途、是否与用户关联、是否用于追踪

### 中国大陆地区（**若上架中国区必查**）
- [ ] **ICP 备案号已下来**（工信部 / 接入服务商，2–4 周流程）
- [ ] 备案号已填到 ASC 的 zh-Hans Localization → ICP License Number 字段
- [ ] 备案主体（公司或个体工商户）跟 ASC 账号开发者主体一致
- [ ] 备案的 App 名称跟 ASC 上的 App Name 一致
- [ ] zh-Hans metadata 全套已准备（name / subtitle / description / keywords / What's New）
- [ ] **隐私政策有中文版本**（reviewer 在中国区会要求）
- [ ] （建议）隐私政策有中国大陆可访问的镜像（gitee pages / 阿里云 OSS，防 GitHub Pages 抖动）
- [ ] 若 App 含直播 / 短视频 / 游戏 / 新闻 / 出版 / 金融 等特定品类：对应的行业许可证已备齐（《网络文化经营许可证》/《信息网络传播视听节目许可证》/ 游戏版号 等，跟 ASC 一并提交）

### 不上架中国大陆
- [ ] ASC → Pricing and Availability → China 已取消勾选（此时上面整组中国项可全部跳过）

### 加密合规
- [ ] 若 `ITSAppUsesNonExemptEncryption = false`：可跳过 ASC 问卷
- [ ] 若 = true 且豁免：ASC 网页问卷已答完
- [ ] 若 = true 且非豁免：BIS ERN 已申请（每年 2/1 前交年度报告）

### Build & TestFlight
- [ ] Build number 比 ASC 上该 version 下已有最大值大
- [ ] ipa 已上传，processingState=VALID
- [ ] TestFlight 内部测试已跑一轮，无崩溃 / 关键功能可用
- [ ] （建议）外部 TestFlight 也跑一轮（首次需 24-48h Beta Review）

---

## 二、版本更新清单（轻量）

> 大部分东西沿用上次的，只检查"这次改了什么"对应的项。

### 必查（每次都查）
- [ ] **build number 比上一版大**（哪怕只 +1）
- [ ] **What's New 已写**（不能空，没大改也得写"修复若干问题"）
- [ ] Demo 账号还能登（密码可能过期）
- [ ] Review Notes 引用的路径还有效（如改了 Tab 顺序 / 设置入口位置要同步更新）

### 条件查（按本次改动判断）
- [ ] **UI 改了** → 截图重新生成 + 校验
- [ ] **加了新功能** → metadata Description 是否需要更新 / Review Notes 需要补新路径 / 演示视频是否要重录
- [ ] **加了新 IAP / 订阅** → ASC 后台创建商品 + 本地化 + 价格 + Review Notes 补 SKU 说明
- [ ] **改了订阅 Paywall** → 重新核对订阅类 App 七项必含元素
- [ ] **改了 CloudKit schema**（新增 record type / 字段 / 索引） → 上线前必须在 CloudKit Console 重新「Deploy 到 Production」，否则正式用户取不到新字段（仅 Console 手动，无 API）
- [ ] **加了新 SDK** → `PrivacyInfo.xcprivacy` 同步 + ASC App Privacy 问卷同步
- [ ] **加了新硬件能力**（相机/相册/定位等） → `Info.plist` 加对应 `NSXxxUsageDescription`
- [ ] **改了核心功能流程** → 演示视频更新
- [ ] **改了 App 名称 / 备案主体**（中国区） → 必须重新做 ICP 备案，新备案号下来才能提审中国区
- [ ] **新增了上架中国大陆**（之前没勾） → 必须先完成 ICP 备案才能上

### 时效性事项
- [ ] 加密合规年度自报告（若适用：每年 2 月 1 日前向 BIS 提交）
- [ ] 演示视频里如果有日期 / 节日内容，确认还合时宜

---

## 用法

跑 `submit.md` 前，AI 应主动问用户："这是首次提审还是版本更新？" 然后带用户走对应清单。每项问"已经做了"/"不适用"/"还没做"，**未完成项必须先回去做完再继续推送 ASC**。
