# Rule: China Storefront Material Consistency

Guideline: Domestic storefront submission quality  
Severity: warning  
Category: storefront

## What to check

For domestic Android stores, manually verify consistency across:

- app name
- developer entity
- privacy-policy主体
- screenshots and listing text
- declared feature descriptions

## Why it matters

Domestic storefront review often focuses on whether the submission materials tell the same story as the package behavior.

## How to detect

From the APK alone, only collect hints:

- package name
- app label
- integrated SDKs
- visible feature modules in bundled web assets

Everything else requires submission-material review.

## How to report

Prefer:

- `needs manual verification: storefront materials must be checked for name, entity, and privacy-policy consistency`

## Resolution

- align listing text, screenshots, and privacy-policy主体 with the real package behavior
- remove or explain permissions and features that are not clearly represented in the materials

## Example rejection framing

- `Storefront materials and package behavior may not be sufficiently aligned for review.`
