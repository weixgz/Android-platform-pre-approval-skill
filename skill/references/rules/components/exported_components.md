# Rule: Exported Components

Guideline: Attack surface minimization  
Severity: warning  
Category: components

## What to check

Check exported:

- activities
- services
- receivers
- providers

## Why it matters

Exposed components should be intentional, minimal, and aligned with visible user-facing flows or trusted SDK callbacks.

## How to detect

Use the analyzer component report and verify whether exported items are:

- main launcher activity
- payment callback activity
- profile installer receiver
- other SDK components that are common and low-risk

## How to report

Prefer:

- `info: exported payment callback components appear intentional`
- `warning: exported components need manual confirmation if purpose is unclear`

## Resolution

- remove unnecessary exported state
- protect risky components where possible
- document any exported SDK callback components in the review rationale

## Example rejection framing

- `Component exposure appears broader than necessary for the declared app behavior.`
