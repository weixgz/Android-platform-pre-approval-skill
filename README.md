# 国内安卓平台预审skill

一个面向 Android 应用提审前检查场景的技能仓库，用于对 `.apk` 安装包进行预审分析，并在需要时补充运行态验证。

项目目标是帮助研发、测试、产品、运营或合规团队在提审前更早发现明显风险，减少来回打回，而不是替代最终的市场审核或法务判断。

## 仓库包含什么

- `skill/`：主技能目录，包含规则、脚本和输出约定
- `claude/`：Claude Code 适配层

## 建议入口

- 使用方式、工作流和输出格式：[`skill/SKILL.md`](/Users/geekdance8888/Desktop/GPT/android-app-prescreen-repo/skill/SKILL.md)
- skill 内部说明：[`skill/README.md`](/Users/geekdance8888/Desktop/GPT/android-app-prescreen-repo/skill/README.md)
- 参考资料索引：[`skill/references/README.md`](/Users/geekdance8888/Desktop/GPT/android-app-prescreen-repo/skill/references/README.md)

## 快速开始

安装依赖：

```bash
python -m pip install androguard
```

静态分析：

```bash
python skill/scripts/apk_review.py /path/to/app.apk --output /tmp/apk_review.json
```

动态验证准备与收集：

```bash
python skill/scripts/runtime_smoke.py prep /path/to/app.apk
python skill/scripts/runtime_smoke.py collect --package <package.name>
```

## 说明

仓库首页只保留概览信息。更具体的规则、动态必测矩阵、目录职责和报告约定，统一放在 `skill/` 目录内维护，避免根目录 README 过长、过细。
