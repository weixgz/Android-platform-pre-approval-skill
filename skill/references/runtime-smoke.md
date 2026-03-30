# Dynamic Runtime Smoke Checks (Optional)

This note is for the **dynamic** part of the prescreen workflow. Use it when the user asks:

- can you run it / reproduce it
- video cannot load
- permission prompts are wrong
- privacy entry is missing
- account deletion /注销 cannot be found

Pair this file with `runtime-must-test.md`, which defines the default dynamic coverage matrix.

## What Dynamic Can Prove

Dynamic checks can produce evidence that static APK inspection cannot:

- a specific page exists and is reachable from a given path
- a video/ad player actually loads and plays (or fails with a concrete error)
- consent prompts appear (or do not) on first run
- privacy policy / user agreement entries are accessible in-app
- account deletion path is present and the UI can reach the confirmation page
- whether the major top-level pages actually open and show plausible content
- whether obvious test/demo/mock data is leaking into the release build

## Evidence To Collect

Prefer collecting at least one item per finding:

- screenshot of the target page
- a short screen recording (if available)
- `logcat` lines that show network/player errors or the actual video URL

## Common Failure Signatures

When users report "video cannot load", look for:

- DNS: `UnknownHostException`
- TLS: `SSLHandshake`, `CertPath`
- timeout: `timed out`, `timeout`
- HTTP errors: `403`, `404`, `5xx`
- player errors: `ExoPlayer`, `MediaCodec`, `OMX`, `IJKMEDIA`

## Suggested Process

1. `runtime_smoke.py prep` to install/launch and clear logcat
2. If login is not available, complete the pre-login page sweep first
3. If login is available, continue the post-login must-test checklist
4. `runtime_smoke.py collect` to capture a screenshot and the logcat highlights
5. Write the report with a dedicated **dynamic** section so static and runtime facts do not mix
