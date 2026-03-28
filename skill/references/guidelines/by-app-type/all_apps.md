# All Apps Baseline

Use this checklist for every Android APK before loading any app-type-specific guide.

## Core package identity

Check:

- package name, app label, version name, version code
- min sdk and target sdk
- main activity or main launch surface
- whether the package looks like a release build

Flag:

- debug or test-only packaging
- placeholder package identity
- target sdk that may need store-policy confirmation

## Release safety baseline

Check:

- `usesCleartextTraffic`
- network security config declaration
- staging or test domains in resources
- update, install, hot-update, patch, or dynamic loading wording

Flag:

- release builds that still point to test infrastructure
- cleartext traffic without a strong reason
- risky self-update or install flows

## Sensitive permissions baseline

Check:

- whether sensitive permissions have a visible feature match
- whether broad permissions appear heavier than the likely user value
- whether high-scrutiny permissions need stronger justification

Pay extra attention to:

- location
- camera / microphone
- storage / media access
- phone state
- installed-app visibility
- install packages
- overlay / accessibility / device admin

## Privacy and user-rights baseline

Check:

- privacy policy entry or privacy prompt signals
- explicit agree / refuse choice signals
- account deletion / 注销 signals
- permission-management or revoke-authorization signals

Flag:

- privacy links pointing to staging domains
- sensitive permissions with weak privacy signals
- no visible deletion or rights-management entry for account-based apps

## Component exposure baseline

Check:

- exported activities, services, receivers, and providers
- whether exposed components look intentional
- whether payment callback components are the only clearly exported items

Flag:

- broadly exposed services or providers
- exported components with risky names or unclear protection

## Output rule

Always produce:

1. platform-by-platform pass risk first
2. missing or failing points under each platform
3. shared missing items across stores
4. uppercase final summary
