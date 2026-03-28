# Rule: Cleartext Traffic

Guideline: Release transport safety  
Severity: warning  
Category: network

## What to check

Check:

- `usesCleartextTraffic`
- `networkSecurityConfig`
- any test or internal domains that suggest non-production transport setup

## Why it matters

Cleartext traffic raises review and security concerns, especially for login, payment, profile, order, or health-related data.

## How to detect

Look at package metadata and network indicators from the analyzer.

## How to report

Prefer:

- `warning: cleartext traffic enabled in release package`
- `needs transport-security justification or configuration hardening`

## Resolution

- disable cleartext traffic where possible
- define a stricter network security config
- confirm privacy-policy and API links use production HTTPS endpoints

## Example rejection framing

- `App transport settings appear weaker than expected for the declared user-data flows.`
