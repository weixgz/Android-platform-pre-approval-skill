# 国内安卓平台预审skill

一个面向 Android 应用提审前检查场景的技能仓库，用于对 `.apk` 安装包进行 **静态预审**，并在需要时追加 **动态运行验证（可选）**，输出适用于多应用市场的风险提示报告。

该项目的目标不是替代人工审核、法务判断或市场终审，而是在提交前尽早发现明显风险，帮助研发、产品、合规或运营团队更高效地完成自查。

## 项目定位

本仓库聚焦于 APK 静态分析与审核准备，适合以下场景：

- 在提交 Google Play 或国内 Android 应用市场前做一次快速预检查
- 对权限、组件暴露、网络配置、文案资源等做基础风险排查
- 为人工审核提供结构化的预审报告与核查清单
- 作为 OpenAI / Codex 技能包或 Claude Code 适配工程持续维护

## 核心能力

当前支持的预审范围包括：

- 基础包信息提取（包名/版本/SDK/主入口等）
- 敏感权限与特殊能力识别
- Activity / Service / Receiver / Provider 暴露面检查
- 隐私、授权、账号注销等合规相关静态信号识别
- 测试文案、占位文案、可疑域名、明文传输等发布质量问题提示
- 面向 Google Play 与国内主流 Android 市场的差异化预审建议

动态运行验证（可选）会覆盖更偏“运行态”的问题定位，例如：

- “看视频得积分/激励视频”是否能加载、是否能播放完成
- 隐私政策/用户协议是否常驻可访问（应用内入口）
- 账号注销/删除功能是否可达且可完成
- 权限是否按场景弹出、拒绝后是否有降级路径（需要录屏或日志辅助）

预审输出通常会覆盖以下维度：

- 跨市场通用风险
- Google Play 相关风险
- 国内应用市场通用基线
- 华为应用市场、Xiaomi、应用宝、vivo、OPPO 的差异化要点
- 需要人工继续核验的事项
- 总体风险结论与后续建议

## 能力边界

本项目基于 APK 静态内容进行分析，结论应视为“预审信号”而非最终审核结论。以下内容通常无法仅凭 APK 静态分析完全确认：

- 商店页文案、截图、分类与声明信息
- 隐私政策页面的可访问性、真实性与归属关系
- 首次启动时的授权弹窗与真实交互流程
- 权限拒绝后的降级体验
- 账号注销、投诉反馈、用户权利响应链路
- 服务端行为、远程开关、动态下发逻辑

因此，建议将本项目输出与人工测试、合规审查、提审材料核对结合使用。

## 两段式交付（推荐）

为了降低“静态推断”和“运行事实”混在一起导致的误读，建议输出按两段组织：

1. **静态预审（APK）**：基于 Manifest/资源/DEX 字符串的可证事实与风险信号。
2. **动态验证（运行态，可选）**：基于真机/模拟器的截图与 logcat 证据，验证“能不能跑、能不能加载、权限/隐私/注销路径是否可达”。

## 仓库结构

```text
.
├── README.md
├── skill/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── scripts/apk_review.py
│   ├── scripts/runtime_smoke.py
│   └── references/
│       ├── README.md
│       ├── guidelines/
│       │   └── by-app-type/
│       ├── rules/
│       ├── review-checklist.md
│       ├── china-baseline.md
│       └── platform-deltas.md
└── claude/
    ├── CLAUDE.md
    └── .claude/
        ├── agents/android-app-prescreen.md
        └── commands/apk-prescreen.md
```

各目录职责如下：

- `skill/`: 面向 OpenAI / Codex / OpenClaw 风格技能体系的主工作目录
- `skill/SKILL.md`: 技能触发条件、工作流、输出格式与审查规则
- `skill/scripts/apk_review.py`: APK 静态分析脚本，负责提取结构化事实
- `skill/references/guidelines/`: 按应用类型组织的审核清单
- `skill/references/rules/`: 按风险主题拆分的独立规则卡片
- `skill/references/README.md`: 引导如何组合使用清单与规则
- `claude/`: 面向 Claude Code 的适配层，复用同一套分析脚本与规则

## 设计思路

当前 skill 已经从“单份提示词 + 几份说明文档”升级为更容易扩展的分层结构：

- 主 `SKILL.md` 只保留工作流和输出规范
- 通用检查与垂类检查下沉到 `guidelines/`
- 具体风险主题拆成独立 `rules/`
- 输出先按平台判断是否可能通过，再列缺失项，最后给出大写汇总结论

这种结构更适合后续继续扩展：

- 电商类应用
- 医疗健康类应用
- 工具类应用
- 更多中国安卓市场差异化要求

## 快速开始

### 方式一：作为本地分析工具使用

1. 安装依赖：

```bash
python -m pip install androguard
```

2. 运行静态分析脚本：

```bash
python skill/scripts/apk_review.py /path/to/app.apk --output /tmp/apk_review.json
```

3. （可选）运行动态验证脚本，生成运行态证据：

```bash
# 安装 + 启动 + 清空 logcat（准备阶段）
python skill/scripts/runtime_smoke.py prep /path/to/app.apk

# 在真机/模拟器里复现目标路径后，收集截图与日志（收集阶段）
python skill/scripts/runtime_smoke.py collect --package <package.name>
```

4. 结合以下资料生成完整预审报告：

- `skill/SKILL.md`
- `skill/references/review-checklist.md`
- `skill/references/china-baseline.md`
- `skill/references/platform-deltas.md`

### 方式二：作为 OpenAI / Codex 技能包使用

如需打包为技能上传使用，请将 `skill/` 目录内容单独打包，而不是打包整个仓库根目录。

示意：

```bash
cd skill
zip -r skill.zip .
```

### 方式三：作为 Claude Code 适配工程使用

如果你的工作环境是 Claude Code，可以直接使用 `claude/` 目录作为入口：

- `claude/.claude/agents/android-app-prescreen.md`：可复用的子代理定义
- `claude/.claude/commands/apk-prescreen.md`：命令式入口
- `../skill/scripts/apk_review.py`：共享静态分析脚本

## 输出内容说明

建议报告至少包含以下模块：

- 基础包信息
- 跨市场通用检查结果
- Google Play 风险提示
- 国内市场通用基线检查结果
- 华为应用市场差异项
- Xiaomi 差异项
- 应用宝差异项
- vivo 差异项
- OPPO 差异项
- 需要人工核验的事项
- 总体风险总结与建议动作

其中需要特别强调两点：

- 结论应尽量基于 APK 中可证实的事实，例如 Manifest 字段、权限名、导出组件、字符串资源、域名或网络配置
- 对无法静态确认的内容，应明确标注为“需要人工核验”，避免给出过度确定的判断

## 当前检查重点

脚本与规则当前重点关注以下风险类型：

- `debuggable`、`testOnly`、备份开关、明文流量等发布配置问题
- 敏感权限与高风险能力声明是否存在
- 组件导出面是否存在潜在暴露风险
- 资源文案中是否出现测试、占位、隐私、授权、账号注销等关键信号
- 是否存在本地地址、测试域名、可疑更新文案、动态更新或静默安装相关信号

## 适用平台

本仓库当前主要覆盖以下平台或工作流：

- OpenAI / Codex
- OpenClaw
- Claude Code
- Google Play 提审前预检查
- 国内 Android 应用市场提审前预检查

国内市场规则目前重点参考以下方向：

- 华为应用市场
- Xiaomi
- 应用宝
- vivo
- OPPO

## 维护建议

为了保持项目清晰、可持续迭代，建议按以下方式维护：

- 将触发规则、输出规范和人工审查原则集中维护在 `skill/SKILL.md`
- 将确定性的 APK 提取与静态判断逻辑维护在 `skill/scripts/`
- 将政策基线、核查清单和平台差异维护在 `skill/references/`
- 每次调整规则后，优先同步更新 README 与技能说明，避免仓库说明与实际逻辑脱节

## 适合谁使用

这个项目尤其适合以下角色作为提审前工具链的一部分：

- Android 开发工程师
- 测试工程师
- 产品经理
- 运营与上架团队
- 隐私合规或审核支持团队

## 说明

本仓库整理的是一套面向 Android APK 的静态预审工作流、规则集合与适配入口。它能够帮助团队更早发现问题、减少反复提审，但不能替代最终的市场审核、法律判断或完整人工验收。

如果你希望将它作为长期维护的仓库使用，推荐把这里作为“规则源仓库”，持续迭代 `skill/` 下的脚本与规则，再按需要打包成分发版本。
