# Stage: ASC Auth（App Store Connect API 鉴权）

> 本 stage 是其他 ASC API 相关 stage（upload / submit / watch）的前置。

## 凭据约定
```
~/.appstoreconnect/
├── AuthKey_ABCD123456.p8       # 从 ASC → Users and Access → Integrations 下载（只能下载一次）
└── config.json
```

`config.json`:
```json
{
  "key_id":    "ABCD123456",
  "issuer_id": "57246542-96fe-1a63-e053-0824d011072a",
  "key_path":  "~/.appstoreconnect/AuthKey_ABCD123456.p8"
}
```

## JWT 规范（Apple 要求）
- alg: **ES256**
- header: `{"alg":"ES256","kid":"<key_id>","typ":"JWT"}`
- payload:
  ```json
  {
    "iss": "<issuer_id>",
    "iat": <now>,
    "exp": <now + 1200>,
    "aud": "appstoreconnect-v1"
  }
  ```
- 用 `.p8`（PKCS#8 EC 私钥）签名
- **最长 20 分钟**，过期重签
- ⚠️ **不要加 `scope` 字段**：它是可选的限权字段，一旦填了，token 就只能调被列出的接口，其他请求一律 401。通用 token 不带 scope。
- `config.json` 里 `key_path` 若用 `~`，读取时记得展开（`asc_mint_jwt.py` 已处理）

## 步骤（首次配置 — AI 现场引导即可）
1. 引导用户到 ASC → Users and Access → Integrations → Keys，生成 Key
2. 下载 `.p8`（只能下载一次）
3. 询问 Key ID 和 Issuer ID
4. AI 直接帮用户写 `~/.appstoreconnect/config.json`（结构见上）
5. 验证：用下方脚本签 token 后 `curl .../v1/apps`

## 脚本
- `../scripts/asc_mint_jwt.py` — 读 config + .p8，签 ES256 JWT 输出到 stdout（**已收录**）。其他步骤通过 shell out 拿 token：
  ```bash
  TOKEN=$(../scripts/asc_mint_jwt.py)
  curl -H "Authorization: Bearer $TOKEN" https://api.appstoreconnect.apple.com/v1/apps
  ```
  > 依赖 `cryptography`（ES256 签名必需）：`pip install cryptography`
- 首次配置（写 config.json）无需脚本，AI 现场问几句直接写文件即可。

## 参考
- https://developer.apple.com/documentation/appstoreconnectapi/generating-tokens-for-api-requests
