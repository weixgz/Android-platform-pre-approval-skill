# Rule: Account Deletion And User Rights

Guideline: User-rights baseline  
Severity: warning  
Category: privacy

## What to check

Check for static signals of:

- account deletion / 注销
- revoke authorization
- personal-data management
- complaint or privacy contact channels

## Why it matters

For account-based apps, missing rights-management signals often lead to extra reviewer questions and manual verification.

## How to detect

Search bundle strings and resources for:

- `delete account`
- `account cancellation`
- `注销`
- `撤回授权`
- complaint or privacy contact wording

## How to report

Prefer:

- `needs manual verification: no clear account-deletion signal found in static resources`

## Resolution

- add or expose a visible account-deletion path
- document complaint/contact channels
- align store listing, screenshots, and in-app rights entry

## Example rejection framing

- `User-rights or account-deletion path is not sufficiently evident for an account-based app.`
