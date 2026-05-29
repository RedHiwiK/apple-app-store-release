# Stage: Export Compliance（加密合规）

## 三档判定（90% 的 App 落在前两档）

**1. 没用加密 或 只用了 Apple 提供的加密（HTTPS / Keychain / CryptoKit）**
```xml
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```
不需要额外申报。

**2. 用了加密但符合豁免条款**（典型：仅用于认证、版权保护、或 OS 标准算法）
```xml
<key>ITSAppUsesNonExemptEncryption</key>
<true/>
<key>ITSEncryptionExportComplianceCode</key>
<string>YOUR_ERN_CODE</string>
```
ASC 网页问卷会问 5 题左右，根据回答确定豁免。

**3. 真的用了非豁免加密**
- 向美国 BIS 提交 Encryption Registration Number (ERN) 申请
- 每年 2 月 1 日前提交 Annual Self-Classification Report

## 步骤
1. 扫描代码：
   ```bash
   grep -rE 'CommonCrypto|CryptoKit|CC_SHA|SecKey|kSecAttr' --include='*.swift' --include='*.m'
   ```
2. 根据匹配结果给档位建议
3. 用 `plutil -insert` 写入 Info.plist
4. 档位 3：输出 BIS 申请表填写指引

## 脚本
本阶段无预置脚本，AI 现场实现即可：
- 扫描加密用法：上方"步骤"里的 `grep` 命令直接用
- 写入 Info.plist：`plutil -insert ITSAppUsesNonExemptEncryption -bool false Info.plist`

## 参考
- https://developer.apple.com/documentation/security/complying_with_encryption_export_regulations
- BIS: https://www.bis.doc.gov/index.php/policy-guidance/encryption
