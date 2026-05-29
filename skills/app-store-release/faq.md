# FAQ — App Store 上架常见问题

按主题分组，每个答案尽量短，需要深入时跳到对应 stage 文档。

---

## 一、ASC API & 鉴权

### Q: ASC API Key 在哪生成？需要选什么角色？
ASC → **Users and Access → Integrations → App Store Connect API → +**。角色推荐 **App Manager**（够用），需要管财务时再用 **Admin**。`.p8` 只能下载一次，丢了要重生。

### Q: 调 ASC API 返回 401，怎么排查？
按顺序排查：
1. JWT 是不是过期了（Apple 强制最长 20 分钟）
2. `kid` 是不是写成了 Issuer ID（应该是 Key ID）
3. `aud` 必须是 `appstoreconnect-v1`，不是 URL
4. `.p8` 是不是被改过格式（必须保留 `-----BEGIN PRIVATE KEY-----` 头尾）

详见 `stages/asc-auth.md`。

### Q: Issuer ID、Team ID、Key ID 有什么区别？
- **Key ID** (10 位)：单个 API Key 的标识，每个 `.p8` 一个
- **Issuer ID** (UUID)：你这个 ASC 组织的标识，所有 Key 共用
- **Team ID** (10 位)：开发者证书上的团队 ID，跟 ASC API 无关，签名用

---

## 二、版本号 & 构建号

### Q: build number 必须递增吗？
**严格递增**。规则是：同一个 marketing version (1.2.3) 下，新上传的 build number 必须比该 version 下已存在的最大值大。跨 version 不要求（1.2.3 (10) → 1.2.4 (1) 允许）。

### Q: 同一个 build number 能重新上传吗？
不能。报错 `ITMS-90189: Redundant Binary Upload`。bump 一下重传即可。

### Q: build number 用什么格式好？
- 简单：纯递增整数 `1 / 2 / 3...`
- CI 友好：时间戳 `20260528.1`（同一天多次构建用 `.N` 后缀）
- 避免：纯日期 `20260528`，第二次构建当天就没法递增

---

## 三、签名 & Profile

### Q: Automatic vs Manual signing 怎么选？
- **个人/小团队**：Automatic（Xcode 帮你管 profile）
- **CI / 多人协作 / 严格审计**：Manual（profile 入库，构建可复现）
- 用 fastlane match 是 Manual 的常见方案

### Q: "No profiles for 'com.xxx' were found" 怎么修？
1. 确认 Bundle ID 在开发者后台已注册
2. 确认证书在 Keychain 里且未过期
3. Xcode → Signing & Capabilities → Try Again（或勾掉 Automatic 再勾上）
4. 还不行，跑 `stages/signing.md` 的诊断脚本

### Q: 加了 Push Notification capability 后构建挂了？
profile 没包含 `aps-environment` entitlement。解决：去开发者后台编辑 App ID → 启用 Push Notifications → 重新下载/regenerate profile。

---

## 四、TestFlight

### Q: 上传后多久能在 TestFlight 用？
通常 5–30 分钟（`processingState`: PROCESSING → VALID）。超过 1 小时还在 PROCESSING 大概率是失败了——去 ASC 后台看构建详情，常见原因：缺 Purpose String、缺 icon、entitlements 不合法。

### Q: 内部测试和外部测试有什么区别？
- **内部**：≤ 100 个 ASC 账号，无需 Beta App Review，立即可用
- **外部**：≤ 10000 个邮箱，**首次需要 Beta App Review**（24–48 小时），后续小改不用

### Q: 外部 TestFlight 被 Beta Review 拒了，影响正式审核吗？
不影响，但说明问题大概率正式审核也会拒，建议先修。

### Q: 上传后 ASC 网页一直看不到构建？
- 看邮件，可能收到了 ITMS-XXXXX 错误
- 看 Xcode → Window → Organizer → Archives → Distribute App 的 status
- 用 `xcrun altool --notarization-history 0` 查上传记录

---

## 五、提审 & 审核

### Q: 审核一般要多久？
官方统计 90% 在 24 小时内有结果，实际中位数 ~12 小时。周末 / 节假日（尤其美国节假日）会慢。

### Q: 加急审核（Expedited Review）什么时候能用？
真实紧急情况：线上重大 bug 修复、有时效性的功能（比如奥运/选举相关）。提交入口 `https://developer.apple.com/contact/app-store/request-expedited-review/`。**滥用会被记录**，影响后续审核态度。

### Q: 提审后还能改文案吗？
- **Promotional Text**：可以，无需重新提审，立即生效
- **Description / Keywords / What's New / 截图**：不行，只能撤回（Developer Rejected）改了重提
- **App Name / Subtitle**：审核中不能改，已发布的版本也不能改（要等下一版）

### Q: Phased Release（7 天分阶段发布）能暂停吗？
能。ASC 网页或 API `PATCH /v1/appStoreVersionPhasedReleases/{id}` 把 state 改成 `PAUSED`。可以恢复，也可以一键全量（state = `COMPLETE`）。

### Q: 主动撤回审核（Developer Rejected）会影响以后吗？
不会影响审核态度，但提审排队要重新走。比"等 Apple 拒"快——发现问题立刻撤回比硬等更省时间。

---

## 六、隐私 & 合规

### Q: 第一次提审被 Guideline 5.1.1 拒，最常见原因？
按命中率：
1. 隐私政策 URL 打不开 / 404
2. 启动就要登录但没说明为什么需要
3. 收集了数据但 ASC App Privacy 问卷没勾
4. 用了第三方 SDK（Firebase / Sentry）但 `PrivacyInfo.xcprivacy` 没声明
5. 用了 `NSUserDefaults` 等 Required Reason API 没写理由

### Q: 隐私政策可以用什么语言？
英文是必须的。如果 App 上架某语言地区，建议该语言也提供（比如中国大陆地区强烈建议中文）。Apple 不强制每个 locale 单独 URL，但有就更好。

### Q: 隐私政策和用户协议（EULA）我必须自己写吗？Apple 有没有官方版？
两个完全不同：
- **隐私政策**：✅ **必须自己写 + 自己托管 URL**。Apple **没有**官方默认版。常见免费托管：GitHub Pages / Notion Sites / Vercel / Cloudflare Pages。内容要跟 ASC App Privacy 问卷 + `PrivacyInfo.xcprivacy` 三方一致，否则 Guideline 5.1.1 拒。
- **EULA / Terms of Use**：✅ **Apple 有官方默认版**（[Apple Standard EULA](https://www.apple.com/legal/internet-services/itunes/dev/stdeula/)）。ASC 不填 License Agreement 就自动套用，够 95% App 用。

**订阅类 App 额外**：Paywall 必须有可点击的 **Terms of Service 链接** + **Privacy Policy 链接**（Guideline 3.1.2 要求）。ToS 链接用 Apple Standard EULA URL 就够，Privacy Policy 链接必须是你自己的。两个缺一就拒。

详见 `stages/metadata.md` "法律文档"段。

### Q: 上架中国大陆区，ICP 备案号是什么？必须吗？
**必须**。自 2023-09-29 起（存量 App 2024-04-01 起），中国大陆 App Store 强制要求所有上架 App 填 ICP 备案号，没填或填错直接拒绝上架中国区。
- **在哪填**：ASC → App Information → Localizable Information → Chinese (Simplified) → ICP License Number
- **格式**：`京ICP备12345678号` 之类
- **备案本身不在 Apple 走**：去阿里云 / 腾讯云 / 七牛云等接入服务商提交 **App 备案**（不是网站备案），审核 2–4 周
- **个人开发者怎么办**：注册个体工商户（成本约 ¥200–500）后以个体工商户主体备案，是目前唯一路径
- **不上中国区怎么办**：ASC → Pricing and Availability 把 China 取消勾选，跳过这一项
- 详见 `stages/metadata.md` "中国大陆地区特别项"段

### Q: 加密合规年度报告什么时候交？
若 Info.plist 声明了 `ITSAppUsesNonExemptEncryption=true` 且不属于豁免条款，每年 **2 月 1 日前**向 BIS 提交。豁免条款的 App 不需要交。

### Q: 我只用 HTTPS，要勾"使用了加密"吗？
不用。Info.plist 写 `ITSAppUsesNonExemptEncryption = false` 即可，跳过 ASC 问卷。

---

## 七、元信息 & 截图

### Q: 关键词字段中的空格算字符吗？
**算**。100 字符上限里空格也占位，所以 `swift, ios, app` 比 `swift,ios,app` 浪费 2 个字符。逗号后不要加空格。

### Q: 想用的 App 名字被占了怎么办？
App Name 在 ASC **全局唯一**（subtitle 不要求）。被占了只能改，indie 圈常见解法：
- `Name - Tagline`（**最推荐**，例如 `Notes - Quick Capture`，Apple 自己很多 App 也这么用）
- `Name: Subtitle`
- `Name for X`（限定用途，差异化清晰）

**关键操作**：
1. 取名前先去 App Store 搜一下，能搜到同名 App 基本就被占了
2. ASC 创建 App 记录时输入 Name 即时校验
3. 想保留名字但还没准备好提审的，**先创建 App 记录占住**（不提审的话 180 天后 Apple 回收）
4. 算上"差异化后缀"也别超 30 字符
5. **不能蹭品牌**——`Notes for Apple` / `WeChat Helper` 这类含他人商标的会被 Guideline 5.2.1 拒

详见 `stages/metadata.md` "名称占用对策"段。

### Q: 截图能用设计 mockup 框架吗？（手持手机背景的那种）
能。Apple 允许营销性截图，但**不能伪装成不是 iPhone 的设备**（比如把 iPhone 截图塞进 Android 框架）。本 skill 的 `preview-studio/overview.md` 默认就是这种 mockup 风格。

### Q: 多语言文案审核会逐个审吗？
是。某个语言的描述/截图踩雷会得到 `METADATA_REJECTED`，其他语言可能正常。拒审邮件会指明是哪个 locale。

### Q: What's New 不写会怎样？
不能为空。首次提审写新版本介绍即可；后续没大改也得写一句"修复若干问题"，否则 ASC 不让提交。

### Q: 截图传上去显示"尺寸不正确"，但我量过没错？
常见三种：
1. PNG 带了 alpha 通道（要 RGB 不要 RGBA）
2. 颜色空间不是 sRGB（Sketch/Figma 默认 P3，导出时要转）
3. 像素尺寸看起来对但实际是 @2x scale 信息错乱——用 `sips -g all xxx.png` 看真实尺寸

---

## 八、价格 & 内购

### Q: 免费 App 改成付费会发生什么？
立即生效，已下载用户保留终身使用权。但**已购买过付费版的不能改回免费再涨价**，会被视为操纵。

### Q: 订阅价格能涨吗？老用户怎么处理？
能。ASC 提供两种模式：
- **Preserve current price**：老用户保留原价，新用户用新价
- **Apply new price to existing users**：要求用户主动同意（弹窗）才生效，否则会自动取消订阅。涨幅 >50% 强制走这条路径。

### Q: StoreKit 测试在沙盒环境总是失败？
- 沙盒账号必须是新邮箱（不能是已注册过 Apple ID 的）
- 设备 Settings → App Store → Sandbox Account 单独登录，不是主 Apple ID
- iOS 14+ 推荐用 Xcode 的本地 `Configuration.storekit` 文件，比沙盒稳定

---

## 九、AI 出图（preview-studio 子区）

### Q: 出图怎么收费？需要 OpenAI API Key 吗？
**不需要 API Key**。本 skill 不直接调 API，出图能力来自驱动它的 AI 工具本身：
- 用 **Codex / ChatGPT** 跑：自带出图，端到端搞定，走你的 ChatGPT Plus / Pro 订阅额度
- 用 **Claude Code** 跑：无原生出图能力，跑到 prompt 包齐为止；最后一步用户手动把 prompt 粘到 Codex / ChatGPT 出图（同样走 Plus 订阅）

两条路都没有额外的 API 计费。

### Q: AI 生成的截图算"误导性 marketing"吗？
**只要 UI 部分是真的就不算**。流程是把 App 真截图作为 base 喂给模型，prompt 里强制要求"不修改 UI 内容、不画假按钮"，背景 / 设备氛围 / 标题是 AI 生成的——跟用 Figma 做营销图本质一样。Apple 关心"App 实际功能与展示是否一致"，不是"图怎么做出来的"。

### Q: 文字渲染错了字怎么办？
gpt-image 偶尔会写错字（尤其是中日韩）。两个办法：
1. 让 Codex 重新生成 2–3 张候选，挑对的
2. 让 AI 出"无文字版本"，标题再用图像编辑工具后期叠上（最稳但失去 AI 排版灵活性）
3. 多语言版本必须人工至少扫一眼

### Q: 怎么保证整套图风格一致？
本 skill 在 Phase 2 会让用户确认一个 `style.yaml` Style DNA（配色、字体、设备摆放、氛围），后续每张图的 prompt 都嵌入这段描述。出图时把第一张满意的作为后续每张的 reference image 上传，可显著提升一致性。

### Q: base 截图从哪来？要在真机截吗？
两种方式都行：
- **真机/模拟器手动截**：自己跑 App、切到目标页面、截图保存到 `<项目名>-appstoreconnect/screenshots/base/`
- **Claude 用 simctl 自动截**：模拟器跑起 App，每切到一个页面就让 Claude 跑 `xcrun simctl io booted screenshot`，分辨率天然就是 Apple 标准 device pixel

### Q: 一套图大概要做多少张？
ASC 要求每个尺寸每个语言至少 1 张，建议 **5–8 张**（不会被刷下去也不会信息过载）。第一张是 App 的 hero feature，最重要。

---

## 十、流程 / 工具链

### Q: 不用 fastlane 行吗？
完全可以。本仓库的 skill 直接调 `xcodebuild + ASC API`，不依赖 fastlane。fastlane 优势在 metadata 同步和团队协作，独立开发用 skill 反而更轻。

### Q: 第一次上架最容易忘的事？
按 2025 年实际拒审命中率排序：
1. **缺核心功能演示录屏**（reviewer 近 1–2 年明显加强了这条，复杂功能 / AI 功能 / 工具类 App 几乎必问）
2. **订阅 App 缺完整购买流程录屏**（订阅类 App 拒审重灾区，详见下条 Q）
3. `PrivacyInfo.xcprivacy` 没建（Xcode 15+ 必须）
4. ASC App Privacy 问卷没填 / 与 `PrivacyInfo.xcprivacy` 不一致
5. Demo 账号没给 / 给错了 / 登不进去
6. 截图缺最大尺寸（iPhone 6.9" / iPad 13"）
7. Info.plist 缺 `NSXxxUsageDescription`（用相机/相册/定位等）

### Q: reviewer 要求"提供核心功能演示视频"怎么办？
2024 年起 reviewer 越来越倾向**主动索要演示视频**，尤其是：
- AI / 大模型功能（怕你只是套个壳）
- 工具类 / 效率类 App（怕功能描述跟实际对不上）
- 需要硬件配合的（摄像头、传感器、外设）
- 复杂的多步流程

提交渠道：ASC → App Review Information → **App Review Attachment**（直接上传 mp4/mov，≤ 500 MB）。
建议规格：
- 1080p / 30fps 即可，无需 4K
- 时长 30–90 秒
- 屏幕录制 + 简短中文/英文字幕说明每一步在干什么
- 覆盖：启动 → 进入核心功能 → 完成一次完整流程 → 看到结果

**Pro tip**：第一次提审就主动把视频附上，能显著降低被卡的概率。

### Q: 订阅类 App 的录屏到底要拍什么？（拒审重灾区）
Apple 对自动续期订阅有非常严格的"信息披露"要求，**视频必须完整覆盖以下所有点**，缺一就拒：

**Paywall 页面（订阅入口）**
- [ ] 订阅周期清晰可见（月度 / 年度 / …）
- [ ] **价格清晰可见**（如 ¥28/月）
- [ ] **明确写"自动续期"**字样
- [ ] 提供"Terms of Service" 和 "Privacy Policy" **可点击**链接
- [ ] 提供"Restore Purchases" 恢复购买按钮（**不可缺**）
- [ ] 试用期 / introductory offer 如果有，必须显式说明转付费的时点

**完整购买流程**
- [ ] 点订阅 → 系统弹出 Apple 原生支付确认 sheet → 完成支付 → 解锁内容
- [ ] 全过程录下来，不要剪掉支付 sheet 那一步

**取消订阅说明**
- 不强制在 App 里做取消入口，但 App 内要有文字说明"通过 Settings → Apple ID → Subscriptions 管理"

附带提交：演示账号 + 演示视频 + 一段 Review Notes 文字解释每个 SKU 对应什么权益。

**最容易踩的雷**：
- Paywall 上只写"¥28"不写"per month"
- 没有 Restore Purchases 按钮（**几乎必拒**）
- ToS / Privacy Policy 是死链或弹窗里看不到
- 试用期没说清楚什么时候开始扣费

### Q: 订阅的"审核截图"（IAP Review Screenshot）要怎么处理？
**实际是可选的**（虽然 ASC 后台暗示该传）。但你**一旦上传，必须遵守两条**否则会被拒：

1. **截图要能"看出"是哪个订阅商品**——月度订阅的图里必须明显有"月/monthly/per month"等字样，年度订阅同理。只放通用 paywall 全景图、看不出特定 SKU，会被打回。
2. **不同 SKU 不能共用同一张图**——月度和年度两个商品的审核截图必须视觉上有区别。最简单做法是截 paywall 上对应 SKU 被高亮选中的状态。

实操建议：没把握就**不传**，把演示视频做扎实即可。要传就批量截每个 SKU 选中态，命名 `pro_monthly_selected.png` / `pro_yearly_selected.png` 一一对应。

### Q: 内购 / 订阅入口要不要在 Review Notes 里写清楚？
**必须**。reviewer 平均花 5–10 分钟看一个 App，不会主动到处翻找付费入口。点了几下没看到 paywall，直接给你打回来说"无法定位 IAP"。

Review Notes（ASC → App Review Information → Notes）至少写清楚：

1. **演示账号**：账号 + 密码（**用真能登的，别用占位**）
2. **从启动到 paywall 的完整路径**，例如：
   ```
   1. 打开 App，使用演示账号登录
   2. 点击右上角"我的"图标
   3. 进入"设置" -> 滚动到底部
   4. 点击"升级 Pro" -> 进入订阅页面
   5. 可看到 ¥28/月 和 ¥288/年 两个 SKU
   ```
3. **每个 SKU 对应什么权益**（必要时表格形式）
4. **如果功能需要特定数据**（已上传文件 / 已建立的项目），说明在哪能看到，或者提示 reviewer 用演示账号已预设好的样例
5. **隐藏入口要显式提示**，比如"该功能仅在连接蓝牙设备后出现"

**通用原则**：
- 假设 reviewer 是 5 分钟前刚下载你 App 的陌生人——什么都要讲清楚
- 不要写"see screenshot"，直接把步骤写成可执行的 1/2/3
- 中英都写（中国区 reviewer 偶尔不读英文）

**Pro tip**：把 Review Notes 当成给"懒得探索的新用户写的快速上手指南"，过审率立即提升。这条规则同样适用于演示视频里的解说。

### Q: macOS App 公证（notarize）和 App Store 审核是同一件事吗？
不是。
- **公证**：本地分发 / 自有网站下载的 `.app` 才需要，目的是 Apple 系统知道这是可信开发者签的
- **App Store 审核**：上 Mac App Store 需要的人工审核
- Mac App Store 上架的 App **既要**走 App Store 审核，**也要**用 Mac 专属的分发证书签名（不是公证证书）
