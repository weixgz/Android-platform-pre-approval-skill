# Domestic China Android-store baseline

Use this baseline for huawei appgallery, xiaomi, yingyongbao, vivo, and oppo before applying store-specific differences.

## 1. Privacy and consent baseline

Treat these as common domestic review expectations:
- provide a standalone privacy policy and make it reachable from the store listing and the app
- present privacy notice and user choice clearly on first relevant use; do not assume bundled or default consent
- do not collect sensitive personal information before the user has had a meaningful chance to review and accept the privacy terms
- when requesting runtime permissions, explain the purpose in the feature context instead of front-loading all requests

## 2. Permission necessity baseline

For sensitive permissions or data classes, ask:
- is there an obvious core-feature match visible in app strings, components, or package naming?
- does the app appear to request broad access before the relevant feature is reached?
- does the requested scope look broader than the likely user value?

Pay extra attention to:
- location
- contacts
- call log / phone state / sms
- camera / microphone
- installed apps / package visibility
- device identifiers
- storage and media access

## 3. User-rights baseline

Mark manual verification for these unless clear in-app evidence exists:
- account deletion / 注销
- permission-management or revoke-authorization paths
- complaint / contact channels for privacy requests
- deletion, correction, export, or account-close wording

## 4. Release-quality baseline

Flag warnings when the release package contains:
- placeholder or unfinished strings
- staging, intranet, localhost, or test endpoints
- debug or test-only packaging
- update, install, hot-update, or patch wording that suggests bypassing store distribution controls

## 5. Reporting rule

For domestic stores, always split findings into:
- domestic baseline findings
- store-specific differences
- manual verification items requiring store listing, screenshots, privacy-policy page, or runtime checks
