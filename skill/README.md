# Skill 内部说明

这个目录是仓库的主工作区，面向实际的技能使用、规则维护和脚本执行。

## 目录职责

- `SKILL.md`：技能触发条件、工作流、输出模板、动态与静态的边界
- `scripts/apk_review.py`：APK 静态分析脚本
- `scripts/runtime_smoke.py`：运行态验证的准备与证据收集脚本
- `scripts/review_runner.py`：总控脚本，串起静态分析、动态准备、证据收集和中文报告生成
- `references/`：规则、清单、平台差异、动态验证矩阵
- `agents/`：技能接入配置

## 使用顺序

1. 先看 [`SKILL.md`](/Users/geekdance8888/Desktop/GPT/android-app-prescreen-repo/skill/SKILL.md)，确认当前任务属于静态预审、动态验证，还是两者都要做。
2. 做静态分析时，运行 `scripts/apk_review.py`，再结合 `references/` 内的规则与平台差异输出报告。
3. 做动态验证时，优先参考：
   - [`runtime-smoke.md`](/Users/geekdance8888/Desktop/GPT/android-app-prescreen-repo/skill/references/runtime-smoke.md)
   - [`runtime-must-test.md`](/Users/geekdance8888/Desktop/GPT/android-app-prescreen-repo/skill/references/runtime-must-test.md)
4. 如果希望一条命令落盘完整任务目录，优先用 `scripts/review_runner.py`。
5. 输出时把静态与动态分开写，避免把“未验证”误写成“没有问题”。

## 推荐命令

新建一个检查任务（静态分析 + 报告骨架）：

```bash
python scripts/review_runner.py start /path/to/app.apk
```

如果设备已经连接，也可以一起做动态准备：

```bash
python scripts/review_runner.py start /path/to/app.apk --dynamic-prep
```

在你配合登录、复现关键路径后，收集运行态证据并更新报告：

```bash
python scripts/review_runner.py collect-runtime /path/to/task-dir
```

如果手工修改了 `notes.json`，可以重新生成报告：

```bash
python scripts/review_runner.py render-report /path/to/task-dir
```

## 文档分层

为了让仓库首页保持简洁，具体细节放在这里和 `references/` 下维护：

- 根目录 `README.md`：项目概览和快速入口
- `skill/README.md`：skill 目录说明和使用顺序
- `references/README.md`：规则与参考资料的索引

## 适合放在这里维护的内容

- 具体规则
- 动态必测项
- 登录前 / 登录后覆盖策略
- 报告模板
- 平台差异说明
