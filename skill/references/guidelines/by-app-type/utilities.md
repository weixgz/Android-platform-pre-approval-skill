# Utilities And Tools

Use this guide for file tools, device tools, helper apps, scanners, or system-adjacent utilities.

## Higher-scrutiny areas

Check:

- whether the app requests package-install, overlay, accessibility, or device-admin-style permissions
- whether storage access scope is broader than the visible tool value
- whether the app suggests hidden behavior, silent install, patching, or non-store distribution

## Risk patterns

Flag:

- `REQUEST_INSTALL_PACKAGES` in a general-purpose utility without strong justification
- cleartext traffic combined with update or install flows
- vague value proposition with very broad device access

## Manual verification prompts

Ask for manual confirmation of:

- exact user-facing scenario for each high-risk permission
- whether permission denial still allows limited but reasonable use
- whether store listing and screenshots clearly explain device-impacting behavior
