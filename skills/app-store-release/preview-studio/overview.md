# Preview Studio — App Store 营销预览图引导式制作

> 本文档是 `app-store-release` skill 内部的子区，不是独立 skill。
> 触发条件由父 SKILL.md 的路由表负责（"做 App Store 截图 / 营销图 / AI 出图 / App Icon 设计"）。

## 设计哲学

**这个子区定义"做营销图"的流程，不绑定任何特定的 AI 工具去执行。**

流程的产物是一套**自包含的 prompt 包**（`style.yaml` + `copy.yaml` + `screenshots/base/` + `prompts/final/`）。**谁来驱动这个流程，取决于用户用什么 AI 工具跑这个 skill**：

| 驱动者 | 出图能力 | 能跑到哪一步 | 用户要做什么 |
| --- | --- | --- | --- |
| **Claude Code**（CLI） | ❌ 原生无图像生成 | Phase 1 → 6，**到 prompt 包齐为止** | 第 6 步完成后，用户自己把 `prompts/final/*.prompt.md` 内容粘到 Codex / ChatGPT 图片模式里出图，再把成品存回 `screenshots/final/` |
| **Codex 应用 / ChatGPT** | ✅ 原生支持出图 | Phase 1 → 6 → **直接出图** → 自动归档 | 端到端跑完，包括最终图像生成 |

无论哪种驱动者：
- 都按本文档六阶段流程走
- 都把过程数据写到 `<项目名>-appstoreconnect/` 项目目录
- 都**不需要 OpenAI API Key**——出图能力来自工具本身（ChatGPT Plus / Pro 订阅自带），不走 OpenAI API
- 都**不预置风格预设、不提供 prompt 模板**——每个 App 的风格和 prompt 都跟用户**现场谈出来**

> 本文档下面写"Claude" / "AI" 时，指的是当前在驱动这个流程的那个 AI（可能是 Claude Code，也可能是 Codex / ChatGPT，行为一致）。

## 项目目录约定（重要）

本子区的所有产物**统一写到项目专属目录**（默认 `<项目名>-appstoreconnect/`，具体见父 `../SKILL.md` 顶部"项目目录约定"段——会话开始时已跟用户确认过位置）。具体子目录：

```
<项目名>-appstoreconnect/
├── screenshots/
│   ├── base/                  ← Phase 4 收集的 App 真实 UI 截图
│   └── final/                 ← 用户拿 prompt 到 Codex 出完图后的归档地（per-platform per-locale）
├── prompts/
│   ├── _skeleton/             ← Phase 3 的骨架（带占位符）
│   └── final/                 ← Phase 6 已填好变量、可直接粘进 Codex 的版本
├── style.yaml                 ← Phase 2 的 Style DNA
└── copy.yaml                  ← Phase 5 的每张图文案
```

**这是持续维护的底账，不是 throw-away 输出**：下次更新 App 截图时，旧的 `style.yaml` / `copy.yaml` / `screenshots/base/` 大部分可复用，只改增量。

---

## 六阶段流程

### Phase 1 — 项目理解（Claude 主动）

读以下信息建立 App 画像：
- 项目根 `README.md`
- Xcode 项目的 `Info.plist`（App 名、Bundle ID、版本）
- 已准备的 ASC 元信息 `<项目名>-appstoreconnect/metadata/<locale>/description.txt`、`subtitle.txt`、`keywords.txt`（**若该目录不存在**——用户还没跑过 metadata 阶段——直接让用户口述 App 定位即可，不强制要求先有这些文件）
- 用户在对话中口述的 App 定位

输出一段 ≤ 100 字的 App 画像，让用户确认或修正。**画像确认后才进入下一步。**

### Phase 2 — 风格讨论（现场生成候选，不查预设）

**基于 App 画像现场提议 3–5 个风格候选**——这是给"这个 App"度身定制的方案，不查任何预设清单。每个候选必须包含：

- **风格名**：自己起，比如"森林清晨"、"霓虹深夜"、"纸质杂志"
- **主色 / 辅色**：具体到 6 位 hex（例如 `#FFB4A2`）
- **背景调性**：渐变 / 纯色 / 摄影 / 插画 / 抽象图形
- **设备摆放**：手持 / 漂浮 / 倾斜角度 / 投影方向
- **标题字重 & 字体方向**：粗体无衬线 / 衬线优雅 / 等宽科技感
- **整体 mood**：一句话情绪描述

**用 AskUserQuestion + preview 字段**做并排对比，让用户选定或在某个基础上改。

确认风格后，落到 `<项目名>-appstoreconnect/style.yaml`，结构示例：
```yaml
name: "森林清晨"
palette:
  primary: "#5B8A72"
  secondary: "#E8D5B7"
  background: "#F5F0E1"
text:
  font_family: "SF Pro Display"
  title_weight: "Heavy"
device: "iPhone 16 Pro Max, tilted 5° right, soft top-down shadow"
mood: "calm, organic, productive morning"
```

字段命名 / 内容可以根据该 App 的特性灵活调整——这只是结构示例，不是模板。

### Phase 3 — 生成基础 prompt 套件（现场写，不套模板）

根据 ASC 截图数量建议（通常 5–8 张），跟用户讨论：
- 每张图主打哪个**功能模块**（首页、核心交互、亮点功能、设置…）
- 每张图的**叙事顺序**（第一张通常是 App 的 hero feature）

确认后，**Claude 为每张图现场写一份 prompt 骨架**（**先不填具体文案、不带 base 截图引用**），写入 `<项目名>-appstoreconnect/prompts/_skeleton/01_home.prompt.md` 等。

骨架里**必须包含**以下 6 块内容（顺序可调，措辞自由发挥）：

1. **任务说明**：要为 `<App名>` 做一张 App Store 营销截图
2. **风格描述**：从 `style.yaml` 把视觉风格自然语言化展开
3. **构图指令**：把提供的 UI 截图嵌进 `{{DEVICE_FRAME}}`，设备的摆放角度 / 阴影 / 背景
4. **标题文字**：`{{TITLE_TEXT}}` 占位符，注明语言、位置、字重
5. **🔴 关键约束（不可省略，否则拒审）**：
   - "Use the provided UI screenshot EXACTLY as-is. Do not modify any screen content."
   - "Do not draw fake buttons, text, or UI elements inside the screen."
   - "Output in sRGB color space, no alpha channel."
6. **输出规格**：目标尺寸（如 1320×2868 for iPhone 6.9"）

骨架文件用 markdown，占位符用 `{{VAR}}` 形式标记。

### Phase 4 — 收集 base 截图

两条路径让用户选：

**路径 A — 用户手动截图**
- 在真机 / 模拟器里跑 App，逐个功能页面截图
- 命名 + 放进 `<项目名>-appstoreconnect/screenshots/base/01_home.png`、`02_focus.png`…

**路径 B — Claude 用 simctl 自动截**
- 前提：用户已在 Xcode 模拟器跑起 App
- 用户每切到一个目标页面，发指令 "截这一张为 home"
- Claude 跑：
  ```bash
  xcrun simctl io booted screenshot <项目名>-appstoreconnect/screenshots/base/01_home.png
  ```
- 用户继续切到下一个页面，重复

**simctl 之前先确认模拟器型号**：`xcrun simctl list devices | grep Booted` 看是 iPhone 16 Pro Max 还是别的——不同型号截图尺寸不同，影响后续 Codex 出图比例。

路径 B 的好处：截图分辨率天然就是 Apple 标准的 device pixel（如 iPhone 16 Pro Max 模拟器出图就是 1320×2868），后续不用做缩放。

### Phase 5 — 文案 & 重点确认（逐张过）

每张 base 截图，跟用户讨论：
- 想突出什么卖点（用一句话写下来）
- 标题文案（多语言）
- 副标题 / 角标（如果需要）
- 这张图是否要 base 截图本身完整可见、还是允许 AI 裁切/再构图

落到 `<项目名>-appstoreconnect/copy.yaml`：
```yaml
screenshots:
  - id: 01_home
    base: <项目名>-appstoreconnect/screenshots/base/01_home.png
    highlight: "10 秒规划全天 — App 的核心 hero feature"
    text:
      en-US: { title: "Plan your day in 10s", subtitle: "" }
      zh-Hans: { title: "10 秒规划全天", subtitle: "" }
      ja: { title: "10秒で1日を計画", subtitle: "" }
    framing: "keep full UI visible, place device tilted 5° right"
  - id: 02_focus
    ...
```

**多语言文案务必逐条核对**：中日韩文有时会被翻译错位，让用户至少看一眼 ja / ko / 中文繁体的标题。

### Phase 6 — 产出最终 prompt 包 + 出图指引

把 `style.yaml` + `copy.yaml` + base 截图的信息，**逐个填进 Phase 3 写好的骨架**，生成可直接粘进 Codex/ChatGPT 的最终 prompt，写入 `<项目名>-appstoreconnect/prompts/final/`。

每张图 × 每个语言一份文件，命名：`<id>.<locale>.prompt.md`，例如 `01_home.zh-Hans.prompt.md`。

最终目录结构：
```
<项目名>-appstoreconnect/
├── style.yaml
├── copy.yaml
├── screenshots/
│   ├── base/                       # Phase 4 截的 App 真实 UI
│   │   ├── 01_home.png
│   │   └── ...
│   └── final/                      # 用户出完图归档到这
│       ├── iphone-6.9/
│       │   ├── en-US/01_home.png
│       │   └── zh-Hans/01_home.png
│       └── ipad-13/
│           └── ...
├── prompts/
│   ├── _skeleton/                  # Phase 3 的骨架（带占位符）
│   └── final/                      # Phase 6 已填好变量、可直接用
│       ├── 01_home.en-US.prompt.md
│       ├── 01_home.zh-Hans.prompt.md
│       └── ...
└── PREVIEW_README.md               # 给用户的出图操作指引（具体内容看驱动者）
```

### Phase 6 末尾分两种情况收尾

**情况 A — 驱动者无出图能力（如 Claude Code）**
- 写一份 `PREVIEW_README.md` 留给用户：
  > "打开 Codex 应用 / ChatGPT 图片模式 →
  > 对每张图：上传 `screenshots/base/<id>.png` + 粘贴 `prompts/final/<id>.<locale>.prompt.md` →
  > 生成后下载到 `screenshots/final/<platform>/<locale>/<id>.png`"
- 提示用户出完图后回来跑校验

**情况 B — 驱动者自带出图能力（如 Codex / ChatGPT）**
- 直接进入出图阶段，逐张：读 base 截图作为 reference + 用 `prompts/final/<id>.<locale>.prompt.md` 内容生成图
- 把成品写入 `screenshots/final/<platform>/<locale>/<id>.png`
- 全部出完后直接进入校验阶段，不需要 `PREVIEW_README.md`

无论哪种情况，每张图出完后都要切到 `../stages/screenshots.md`，按里面的校验维度（sRGB / 无 alpha / ≤ 8MB / 像素尺寸严格匹配）逐张核对。

---

## 重要约束（Claude 必须遵守）

1. **base 截图里的真实 UI 不能让 AI 改**：每份 prompt 都必须包含"use the provided UI exactly as-is, do not modify the screen content, do not draw fake buttons or text inside the screen"。违反会触发 Guideline 2.3.10 拒审。
2. **每个阶段必须停下来跟用户对齐**，不要一口气把六步全跑完。**Phase 1 画像、Phase 2 风格、Phase 5 文案** 这三步必须等用户确认才能继续。
3. **多语言文案务必逐条核对**：中日韩文标题让用户至少扫一眼。
4. **不查任何"预设清单"**：风格和 prompt 都是现场生成。如果用户问"有什么风格可选"，自己根据 App 画像现编 3–5 个候选，不要回答"参考 xx 文件"。
5. **生成的 prompt 必须是英文**（Codex / ChatGPT 出图对英文 prompt 理解更稳）；prompt 内嵌入的标题文案则保留目标语言。

## 与发版流水线的衔接

出完图后：
1. 切到 `../stages/screenshots.md`，按里面的校验维度（sRGB / 无 alpha / ≤ 8MB / 像素尺寸）逐张核对
2. 切到 `../stages/submit.md` 的"上传截图"段落，通过 ASC API 推到对应版本

## 参考
- 模拟器截图命令：https://developer.apple.com/documentation/xcode/running-your-app-in-simulator
- 常见问题见 `../faq.md` 第九节
