# Stage: IAP（内购配置）

## 四类商品

| 类型 | 适用 | 例子 |
| --- | --- | --- |
| Consumable | 一次性消耗 | 游戏金币、批量算力 |
| Non-Consumable | 永久解锁 | 去广告、Pro 解锁 |
| Auto-Renewable Subscription | 自动续期订阅 | 月会员、年会员 |
| Non-Renewing Subscription | 固定时长订阅 | 季度课程 |

订阅必须放进一个 **Subscription Group**；同组内商品互斥（用户同时只能持有一个，可升降级）。

## 每个商品必填项
- Reference Name（内部用）
- Product ID（`com.foo.app.pro_monthly` 风格，**永久不可改**）
- Price tier（Apple 全球定价表 0–93 档；订阅可按地区单独定价）
- Localization（每语言一份）：Display Name（30 字符）+ Description（45 字符，订阅是 80）
- Review Information：Review Notes（说明如何在 App 内触发购买）+ Review Screenshot（**可选**，1024×1024+，详见下方"审核截图规则"）

## 审核截图规则（订阅类必看）

虽然 ASC 后台标记为"可选"，但**如果上传，必须满足以下两条**，否则会被拒：

1. **截图本身要能"看出"对应的是哪个订阅商品**
   - 月度订阅的截图里必须明显有"月"/"monthly"/"per month"等指示
   - 年度订阅必须能看出"年"/"yearly"/"annual"
   - 终身解锁要能看出"lifetime"/"一次买断"
   - reviewer **真的会看这个细节**——只放一张通用 paywall 全景图，看不出特定 SKU 信息，会被打回

2. **不同订阅商品不能用同一张图**
   - 月度 + 年度两个 SKU 各自的审核截图必须**视觉上有区别**
   - 最简单做法：截图就截 paywall 上对应 SKU 那一行被高亮选中的状态

**实操建议**：
- 没把握就**不传**（毕竟是可选的），把演示视频做扎实即可
- 要传就批量截 paywall 上每个 SKU 被选中的不同状态，文件命名 `pro_monthly_selected.png` / `pro_yearly_selected.png` 一一对应

## 步骤
1. 询问要创建的商品列表（类型 + Product ID + 价格档位）
2. 询问支持的语言，逐商品×语言生成本地化文案草稿
3. 生成 `<项目名>-appstoreconnect/iap-config.yaml`（约定见 SKILL.md 顶部"项目目录约定"）：
   ```yaml
   products:
     - product_id: com.foo.app.pro_monthly
       type: auto_renewable_subscription
       group: pro
       price_tier: 9
       localizations:
         en-US: { name: "Pro Monthly", desc: "Unlock all features" }
         zh-Hans: { name: "Pro 月会员", desc: "解锁全部功能" }
       review_notes: |
         登录测试账号 -> 设置 -> 升级 Pro
       review_screenshot: <项目名>-appstoreconnect/iap-screenshots/pro_monthly_selected.png
   ```
4. 通过 ASC API 创建/更新：
   - 一次性商品：`POST /v2/inAppPurchases`
   - 订阅：先 `POST /v1/subscriptionGroups` 建组，再 `POST /v1/subscriptions` 建订阅（订阅端点是 **v1**，没有 v2/subscriptions）
5. 校验：每商品是否有审核截图、每语言是否齐全

## 脚本
本阶段无预置脚本，AI 现场实现即可（都是读/写 yaml + 几个 API 调用，token 用 `../scripts/asc_mint_jwt.py` 签）：
- 推 yaml 到 ASC：按上方 step 4 的端点逐商品创建/更新
- 本地完整性校验：检查每商品是否有审核截图、每语言是否齐全
- 从 ASC 拉现有配置 → yaml：接管已有 App 时 `GET /v2/inAppPurchases` / `GET /v1/subscriptions`

## App 端联动提醒
- StoreKit 2 测试：`Configuration.storekit` 文件在 Xcode 本地模拟
- 务必处理：购买恢复、订阅过期、家庭共享

## 参考
- https://developer.apple.com/documentation/appstoreconnectapi/in-app_purchase
