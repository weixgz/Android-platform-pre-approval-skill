Run the Android APK prescreen workflow on the APK path supplied by the user.

Steps:
1. Confirm the path exists and points to an `.apk`.
2. Run:
   `python ../skill/scripts/apk_review.py <path-to-apk>`
3. Review:
   - `../skill/references/review-checklist.md`
   - `../skill/references/china-baseline.md`
   - `../skill/references/platform-deltas.md`
4. Return the report using these sections:
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

Rules:
- Separate static findings from manual-review items.
- Use severity labels: blocking issue, warning, manual verification needed.
- Do not overstate certainty.
