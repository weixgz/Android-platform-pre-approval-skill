---
name: android-app-prescreen
description: analyze uploaded android apk files and generate a pre-review report for common app-store submission risks. use when the user uploads an .apk and wants prescreen feedback on package metadata, permission risk, component exposure, privacy/compliance hints, resource and copy checks, or store-specific review preparation for google play, huawei appgallery, xiaomi, yingyongbao, vivo, or oppo.
---

# 国内安卓平台预审skill

对上传的 `.apk` 做提审前“静态预审 + 动态运行验证（可选）”，输出可落地的风险提示报告。

输出属于“预审信号”，不能替代最终的市场审核/法务判断。

## 工作流（静态预审）

1. Confirm the user uploaded an `.apk` file.
2. Run `scripts/apk_review.py` on the APK to extract package metadata and static review signals.
3. Always load `references/guidelines/by-app-type/all_apps.md`.
4. Infer one or more app types from the package name, app label, bundled assets, feature modules, or user context, then load the matching app-type guide when relevant:
   - `references/guidelines/by-app-type/ecommerce.md`
   - `references/guidelines/by-app-type/health_fitness.md`
   - `references/guidelines/by-app-type/utilities.md`
5. Load only the rule cards triggered by the findings or materials. Typical mapping:
   - package install permission -> `references/rules/permissions/request_install_packages.md`
   - cleartext transport -> `references/rules/network/cleartext_traffic.md`
   - privacy prompt or agreement evidence -> `references/rules/privacy/privacy_entry.md`
   - no deletion or rights signal -> `references/rules/privacy/account_deletion.md`
   - test or staging URL -> `references/rules/metadata/test_or_staging_domain.md`
   - exported components -> `references/rules/components/exported_components.md`
   - domestic storefront material consistency -> `references/rules/storefront/china_material_consistency.md`
6. Use `references/platform-deltas.md` for Google Play and the domestic-store-specific pass/fail framing.
7. Be explicit about what was verified from the APK and what still requires screenshots, runtime testing, store listing text, privacy policy pages, developer-entity information, or backend behavior.

## 工作流（动态运行验证，可选）

当用户明确提出“能不能运行复现/视频是否加载/权限弹窗是否合理/注销入口是否存在”等问题时，补一段动态验证，用于把“需要人工核验”的点尽可能变成可复核证据。

1. 确认已连接真机或模拟器：`adb devices -l` 能看到 `device` 状态。
2. 使用 `scripts/runtime_smoke.py` 做标准化准备：
   - `prep`：安装、启动、清空 logcat
   - `collect`：截图、dump logcat、提取网络/播放器错误与视频 URL 证据
3. 把动态验证拆成两层，不要把“没法登录”误写成“功能不存在”：
   - 登录前动态验证：首启弹窗、常驻隐私政策/用户协议入口、首页与一级导航页可达性、公开内容是否可用、是否存在测试数据/占位数据/报错页
   - 登录后动态验证：账号资料、注销/删除账号、投诉建议/上传图片、视频/直播/支付/下单/积分等需要账号态的功能
4. 如果没有账号/验证码/测试环境，不要跳过动态验证，而是：
   - 先做登录前覆盖
   - 把“受登录限制未验证”的页面单列出来
   - 明确说明需要用户提供测试账号、验证码协助或已登录会话后才能继续
5. 动态验证默认要做“页面覆盖”，不是只测一个点。至少覆盖：
   - 一级导航页或首页主要入口
   - 每个一级页下最关键的 1 到 3 个二级功能
   - 你们定义的经典必测项：注销功能、常驻隐私政策/用户协议、核心功能可用性、测试数据/占位数据检查
6. 把动态结果写入“动态运行验证”段落：通过/不通过点、证据、仍需补充的材料（真机/弱网/多机型等）。

## Report Rules

- Keep findings concrete and evidence-based.
- Quote the exact manifest field, permission, component, string, domain, or network setting that triggered the finding.
- Do not claim policy violations unless the package evidence clearly supports it. Prefer phrasing such as `possible review risk`, `needs manual verification`, or `likely acceptable`.
- Distinguish static package facts from policy inferences.
- When permissions appear legitimate for obvious core features, say so.
- When a sensitive permission or broad visibility permission appears without a clearly matching feature signal, flag it for manual review.
- Do not invent privacy-policy contents, consent flows, account deletion flows, or developer-entity relationships from the APK alone. Mark those as manual verification unless explicit evidence exists in strings or assets.
- For domestic stores, always produce one shared baseline section first, then note only the extra store-specific deltas in each store section.
- If a store-specific section adds nothing beyond the domestic baseline, say `no extra static risk beyond the domestic baseline`.
- Prefer app-type-specific reasoning over generic speculation. If the app looks like ecommerce or health, say so and then judge whether the permissions actually fit that profile.
 - 动态验证要明确区分：
   - `已验证`：我在设备上跑到的页面/截图/日志证据支持的结论
   - `未验证`：仍需真机、弱网、多机型或更多路径复现的事项
- 对“账号类应用”，动态验证默认把以下两项视为必测项：
  - 注销/删除账号路径
  - 应用内常驻的隐私政策/用户协议入口
- 对“页面覆盖”，不要笼统写“已测过”。要说明测到了哪些页面、哪些页面因为登录/验证码/服务端条件未测到。

## Severity Model

Use this severity model:

- `blocking issue`: strong static evidence of a high-risk configuration or a likely rejection trigger.
- `warning`: plausible review risk that may be acceptable with justification, correct UX, or proper disclosure.
- `manual verification needed`: cannot be determined from static APK inspection alone.
- `info`: noteworthy but not risky.

## Playbook Strategy

Use the documents like this:

- app-type guides define expected feature-to-permission fit
- rule cards explain how to reason about a specific issue
- platform deltas explain how to phrase the result for each store

Do not load every rule card by default. Load only the ones triggered by the APK findings or uploaded materials.

## Output Format

Use this template:

```markdown
# static prescreen (apk)

## platform results (static)

## google play: likely pass / needs rectification / high risk of rejection
- missing or failing point 1
- missing or failing point 2

## huawei appgallery: likely pass / needs rectification / high risk of rejection
- ...

## xiaomi: likely pass / needs rectification / high risk of rejection
- ...

## yingyongbao: likely pass / needs rectification / high risk of rejection
- ...

## vivo: likely pass / needs rectification / high risk of rejection
- ...

## oppo: likely pass / needs rectification / high risk of rejection
- ...

## shared evidence (static)
- basic package information
- app-type inference
- high-impact permissions
- risky transport or metadata findings
- notable exported components

## missing items (static)
- items that still need manual verification or material review

# dynamic verification (runtime, optional)

## platform results (dynamic)
## google play: likely pass / needs rectification / high risk of rejection
- verified or failing point 1

## huawei appgallery: likely pass / needs rectification / high risk of rejection
- ...

## xiaomi: likely pass / needs rectification / high risk of rejection
- ...

## yingyongbao: likely pass / needs rectification / high risk of rejection
- ...

## vivo: likely pass / needs rectification / high risk of rejection
- ...

## oppo: likely pass / needs rectification / high risk of rejection
- ...

## runtime evidence
- device / emulator information
- verified navigation path (if applicable)
- screenshots (if provided) and key log lines (network/player)
- page coverage summary (tested pages / blocked pages / not reached pages)

## missing items (dynamic)
- items that still need manual verification on real devices / weak networks / more scenarios

## final summary
LIKELY TO PASS / NEEDS RECTIFICATION / HIGH RISK OF REJECTION
TOP RISKS: ...
```

## Running the Analyzer

Run:

```bash
python scripts/apk_review.py /path/to/app.apk --output /tmp/apk_review.json
```

## Running The Runtime Smoke Test (Optional)

Dynamic preparation and evidence collection:

```bash
python scripts/runtime_smoke.py prep /path/to/app.apk
# ... reproduce the issue on device ...
python scripts/runtime_smoke.py collect --package <package.name>
```

If the script reports that `androguard` is missing, install it first:

```bash
python -m pip install androguard
```

Then rerun the analyzer.

## Resources

- `scripts/apk_review.py`: static APK analyzer that extracts metadata, permissions, exported components, strings, and network indicators.
- `references/guidelines/by-app-type/`: layered app-type playbooks.
- `references/rules/`: reusable rule cards for specific issues.
- `references/review-checklist.md`: compatibility index that points to the new structure.
- `references/china-baseline.md`: domestic-store reminder that points to the new structure.
- `references/platform-deltas.md`: store-specific differences for huawei appgallery, xiaomi, yingyongbao, vivo, and oppo.
