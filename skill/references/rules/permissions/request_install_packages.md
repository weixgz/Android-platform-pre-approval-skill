# Rule: Request Install Packages

Guideline: High-scrutiny permission review  
Severity: rejection risk  
Category: permissions

## What to check

Check whether the APK requests:

- `android.permission.REQUEST_INSTALL_PACKAGES`
- `android.permission.INSTALL_PACKAGES`

## Why it matters

These permissions are heavily scrutinized because they can enable sideloading or non-store distribution behavior.

## How to detect

Use the analyzer permission list or inspect the manifest directly.

Relevant evidence examples:

- manifest permissions
- strings mentioning install, update, patch, or package download
- visible feature descriptions that may justify enterprise or device-management behavior

## How to report

Prefer:

- `possible rejection risk: package-install permission declared`
- `requires strong business justification or removal before submission`

## Resolution

- remove the permission if it is not essential
- if it is essential, prepare store-specific explanation, screenshots, and scenario proof
- verify no hidden install, self-update, or download-and-run flow exists

## Example rejection framing

- `App requests install-package capability without sufficiently clear user-facing justification.`
