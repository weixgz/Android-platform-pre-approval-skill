---
name: android-app-prescreen
description: analyze uploaded android apk files and generate a pre-review report for common app-store submission risks. use when the user uploads an .apk and wants prescreen feedback on package metadata, permission risk, component exposure, privacy/compliance hints, resource and copy checks, or store-specific review preparation for google play, huawei appgallery, xiaomi, yingyongbao, vivo, or oppo.
---

# 国内安卓平台预审skill

Inspect an uploaded `.apk` and produce a practical pre-review report before marketplace submission. Focus on fast, explainable checks that can be derived from the package contents. Treat the output as a heuristic prescreen, not a final legal or store-policy determination.

## Workflow

1. Confirm the user uploaded an `.apk` file.
2. Run `scripts/apk_review.py` on the APK to extract package metadata and static review signals.
3. Read `references/review-checklist.md` for cross-store and Google Play interpretation.
4. Read `references/china-baseline.md` for a unified domestic Android-store baseline.
5. Read `references/platform-deltas.md` to tailor the domestic section for huawei appgallery, xiaomi, yingyongbao, vivo, and oppo.
6. Produce a report that clearly separates:
   - basic package information
   - cross-store baseline findings
   - google play
   - domestic baseline
   - huawei appgallery
   - xiaomi
   - yingyongbao
   - vivo
   - oppo
   - manual verification needed
   - overall risk summary
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

## Severity Model

Use this severity model:

- `blocking issue`: strong static evidence of a high-risk configuration or a likely rejection trigger.
- `warning`: plausible review risk that may be acceptable with justification, correct UX, or proper disclosure.
- `manual verification needed`: cannot be determined from static APK inspection alone.
- `info`: noteworthy but not risky.

## What To Check

### 1. Basic package information

Summarize:
- application id / package name
- version code and version name
- min sdk, target sdk, compile sdk if available
- app label
- debuggable/test-only/profileable flags when detectable
- whether network security config is declared
- whether cleartext traffic is permitted

### 2. Cross-store baseline

Summarize reusable findings that matter across most stores:
- debug or test packaging
- cleartext traffic and network config exposure
- sensitive permissions and whether they plausibly fit core features
- risky components or exported surfaces
- placeholder copy, staging endpoints, and obvious deceptive-update wording

### 3. Google Play

Use `references/review-checklist.md` to focus on:
- sensitive permissions and special access
- device or network abuse hints
- transparency gaps around privacy, consent, and deletion signals

### 4. Domestic baseline

Use `references/china-baseline.md` to focus on:
- privacy notice and explicit choice hints
- permission necessity and proportionality
- user-rights hints such as account deletion, revoke authorization, complaint/contact channels
- release-quality issues that often trigger manual review

### 5. Store-specific deltas

Use `references/platform-deltas.md` and only add differences beyond the domestic baseline:
- `huawei appgallery`: privacy-policy url readiness, listing/package consistency, higher burden of explanation materials
- `xiaomi`: contextual permission requests, denial handling, separate permission declarations or proofs
- `yingyongbao`: privacy-policy accessibility, developer-entity/privacy-policy consistency, conservative evidence threshold
- `vivo`: conservative review of sensitive permissions, privacy entry points, and listing/runtime consistency
- `oppo`: minimum-necessary permissions, privacy-policy url quality, and high-risk capabilities such as vpn, accessibility, overlay, device admin, install packages, or broad package visibility

### 6. Manual verification needed

Always include manual-review items for anything that static APK inspection cannot prove, especially:
- first-launch privacy dialog correctness
- whether permissions are requested only in context
- whether refusal of a permission still allows reasonable app use
- store-listing text, screenshots, category, and declared feature descriptions
- privacy-policy url validity and ownership
- account deletion flow and user-rights response paths

## Output Format

Use this template:

```markdown
# android app prescreen report

## basic package information
- ...

## cross-store baseline findings
- ...

## google play
- ...

## domestic baseline
- ...

## huawei appgallery
- ...

## xiaomi
- ...

## yingyongbao
- ...

## vivo
- ...

## oppo
- ...

## manual verification needed
- ...

## overall risk summary
- overall assessment: low / medium / high
- google play readiness: low / medium / high risk
- domestic stores readiness: low / medium / high risk
- rationale: ...
- recommended next actions: ...
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
- `references/review-checklist.md`: cross-store and Google Play-oriented review checklist.
- `references/china-baseline.md`: shared domestic Android-store baseline.
- `references/platform-deltas.md`: store-specific differences for huawei appgallery, xiaomi, yingyongbao, vivo, and oppo.
