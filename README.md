# Android App Prescreen

A GitHub-friendly repository layout for an APK prescreen skill that reviews uploaded Android APKs and produces a multi-market pre-review report.

## What this repo contains

- `skill/` — the OpenAI/Codex/OpenClaw-oriented skill bundle
- `README.md` — repository overview and usage notes

Inside `skill/`:

- `SKILL.md` — trigger conditions and workflow instructions
- `agents/openai.yaml` — OpenAI skill UI metadata
- `scripts/apk_review.py` — static APK analysis script
- `references/` — review checklists and market-specific guidance

## Supported review scopes

The skill is designed to check:

- basic package information
- permission risk
- component exposure
- privacy/compliance hints
- resource and copy checks
- overall risk summary

It outputs:
- cross-store findings
- Google Play findings
- China domestic baseline findings
- per-store deltas for Huawei, Xiaomi, Yingyongbao, vivo, and OPPO
- manual verification items

## Repository usage

### Option 1: Use as an OpenAI/Codex skill
Zip the contents of `skill/` (not the repository root) into `skill.zip`, then upload that package where Skills are supported.

### Option 2: Store and iterate in GitHub
Use this repo as the source of truth:
- edit `skill/SKILL.md`
- update scripts under `skill/scripts/`
- update rules under `skill/references/`
- re-package `skill/` when you want a distributable `skill.zip`

## Suggested Git workflow

```bash
git init
git add .
git commit -m "Initial Android app prescreen skill"
```

When you update review logic:

```bash
git add .
git commit -m "Refine APK prescreen rules"
```

## Cross-platform note

- **OpenAI / Codex**: use `skill/` directly as the packaged skill source
- **OpenClaw**: usually compatible with the same skill layout, but validate any frontmatter formatting constraints in that environment
- **Claude Code**: this repo does not yet include a native Claude layout; add a separate `CLAUDE.md` / `.claude/agents/` adapter if needed

## Maintenance tips

- keep trigger conditions in `skill/SKILL.md` frontmatter description
- keep deterministic parsing logic in `skill/scripts/`
- keep long-form policy/checklist content in `skill/references/`
- treat static APK findings as prescreen signals, not final store decisions

## License / policy sources

This repository packages a workflow and checklists derived from publicly documented store policies and review guidance, plus static APK inspection logic. Some policy checks require manual verification because APK-only inspection cannot confirm storefront metadata, hosted privacy pages, screenshots, or runtime consent flows.

## Claude Code adapter

This repository now includes a Claude Code-oriented adapter under `claude/`.

Files:
- `claude/CLAUDE.md`
- `claude/.claude/agents/android-app-prescreen.md`
- `claude/.claude/commands/apk-prescreen.md`

Suggested use:
- open the `claude/` directory as the working project in Claude Code
- let the subagent or command call the shared script at `../skill/scripts/apk_review.py`
- keep the policy checklists shared under `skill/references/`

This keeps one repository with:
- `skill/` for OpenAI / Codex / OpenClaw style packaging
- `claude/` for Claude Code style entrypoints
