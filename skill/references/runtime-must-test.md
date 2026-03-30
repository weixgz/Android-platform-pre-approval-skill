# Dynamic Must-Test Matrix

Use this for the **dynamic** part of the review. The goal is not blind "tap every pixel", but a structured page sweep that covers the pages most likely to cause review rejection or obvious functional failure.

## Principle

Dynamic verification should be split into:

1. **pre-login coverage**
2. **post-login coverage**

If login is blocked, do **not** skip runtime entirely. Finish the pre-login sweep first, then mark the blocked pages explicitly.

## Must-Test For Every App

These are the default mandatory checks whenever dynamic verification is requested:

- first-launch behavior and consent prompt
- in-app persistent privacy policy entry
- in-app persistent user agreement entry
- primary navigation pages or equivalent top-level pages
- obvious placeholder / test data / mock content / dead page checks
- core media or content loading path when the app has video/live/feed modules

If the app is account-based, also treat these as mandatory:

- account deletion / 注销 path
- profile / account settings page

## Pre-Login Coverage

Always try to verify:

- splash / launch behavior
- first privacy prompt
- public homepage or landing page
- each primary tab / major entry that does not require login
- whether any page shows test/staging/mock/demo data
- whether public pages fail with blank states, repeated loading, or obvious 4xx/5xx behavior

## Post-Login Coverage

If login is possible, continue with:

- personal center / account center
- privacy policy and user agreement entry inside the app
- account deletion / 注销 entry and confirmation path
- image upload / avatar change / complaint feedback and permission request timing
- video / ad reward / livestream / player pages
- app-type-specific core path

Examples:

- ecommerce: browse -> cart -> settlement / address / order list
- health: home -> article/video -> service booking / profile / records
- utilities: home -> primary tool -> settings -> account

## Placeholder And Test Data Checks

On each tested page, watch for:

- "test", "demo", "mock", "sample", "uat", "staging"
- obviously fake names, phone numbers, addresses, orders, products, or comments
- hard-coded dates or impossible totals
- empty pages that should obviously have content
- buttons that do nothing

## Reporting Rule

In the dynamic report, always separate:

- `tested and verified`
- `tested and failed`
- `blocked by login / account / server state`
- `not tested yet`

