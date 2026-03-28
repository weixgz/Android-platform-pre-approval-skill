# Rule: Privacy Entry And Consent

Guideline: Privacy notice baseline  
Severity: warning  
Category: privacy

## What to check

Check for static signals of:

- privacy policy entry
- user agreement entry
- explicit agree / refuse buttons
- first-launch privacy prompt files or strings

## Why it matters

Many domestic Android stores expect visible privacy notice and meaningful user choice before sensitive data collection begins.

## How to detect

Look for:

- privacy-related strings
- config files such as `androidPrivacy.json`
- web assets or bundled HTML pages that reference privacy or agreement text

## How to report

Prefer:

- `info: privacy prompt signals are present in the package`
- `warning: privacy prompt is present but supporting links still need verification`

## Resolution

- make sure the privacy entry is easy to find
- ensure agree / refuse wording is explicit
- verify the prompt appears before sensitive data flows and SDK initialization

## Example rejection framing

- `Privacy notice or consent flow appears incomplete or not clearly verifiable from the submission package.`
