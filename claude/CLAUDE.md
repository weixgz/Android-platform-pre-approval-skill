# Android App Prescreen for Claude Code

This directory adapts the APK prescreen workflow for Claude Code.

## Recommended usage

Use the subagent in `.claude/agents/android-app-prescreen.md` when you want Claude Code to:
- inspect an uploaded APK
- run static package checks
- summarize likely store-review risks
- separate static findings from manual-review items

## Scope

The workflow is designed to review:
- basic package information
- permission risk
- component exposure
- privacy/compliance hints
- resource and copy checks
- overall risk summary

## Important limitation

Treat the result as a prescreen report, not a final market approval decision.
APK-only analysis cannot verify store listing metadata, hosted privacy pages, screenshots, real consent flows, or account-deletion behavior.

## File map

- `.claude/agents/android-app-prescreen.md` — reusable APK review subagent prompt
- `.claude/commands/apk-prescreen.md` — slash-command style entrypoint
- `../skill/scripts/apk_review.py` — deterministic static analysis script
- `../skill/references/` — review baselines and market-specific delta checklists
