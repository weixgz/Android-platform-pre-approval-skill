---
name: android-app-prescreen
description: analyze uploaded android apk files and generate a pre-review report for common app-store submission risks. use when the user uploads an .apk and wants prescreen feedback on package metadata, permission risk, component exposure, privacy/compliance hints, resource and copy checks, or store-specific review preparation for google play, huawei appgallery, xiaomi, yingyongbao, vivo, or oppo.
---

# 国内安卓平台预审skill

Inspect an uploaded `.apk` and produce a practical pre-review report before marketplace submission. Focus on fast, explainable checks that can be derived from the package contents, then combine those facts with layered review playbooks and reusable rule cards.

Treat the output as a heuristic prescreen, not a final legal or store-policy determination.

## Workflow

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
# platform results

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

## shared evidence
- basic package information
- app-type inference
- high-impact permissions
- risky transport or metadata findings
- notable exported components

## missing items
- items that still need manual verification or material review

## final summary
LIKELY TO PASS / NEEDS RECTIFICATION / HIGH RISK OF REJECTION
TOP RISKS: ...
```

## Running the Analyzer

Run:

```bash
python scripts/apk_review.py /path/to/app.apk --output /tmp/apk_review.json
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
