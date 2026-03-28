# Rule: Test Or Staging Domain

Guideline: Release quality and submission readiness  
Severity: warning  
Category: metadata

## What to check

Check whether the APK references:

- `.test` domains
- staging hosts
- internal, sandbox, or pre-release environments
- privacy-policy or agreement URLs that still point to test infrastructure

## Why it matters

Test-domain leakage is a common release-readiness problem and weakens reviewer confidence in the package.

## How to detect

Look at:

- network indicators from the analyzer
- privacy prompt config files
- bundled web assets

## How to report

Prefer:

- `warning: release package still references test or staging infrastructure`

## Resolution

- switch policy and agreement links to production URLs
- confirm all visible web assets and APIs use release domains

## Example rejection framing

- `Submission package appears to reference non-production links or materials.`
