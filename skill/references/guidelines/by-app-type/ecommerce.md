# Ecommerce Apps

Use this guide for shopping, marketplace, retail, live-commerce, coupon, or order-driven apps.

## Feature-match expectations

Permissions and SDKs usually need to map to visible user flows such as:

- browsing goods
- cart and checkout
- payment callback
- address selection or map-based pickup
- product photo upload
- customer support or merchant contact
- livestream or short-video commerce

## Common review focus

Check:

- payment callback activities and OAuth integrations
- address, location, and map usage scope
- camera / media permissions for upload or scanning
- whether phone-state, microphone, or install-package permissions look excessive for a retail app

## Risk patterns

Flag:

- install-package permissions without a very clear business case
- microphone permission when the app shows no visible voice or live feature evidence
- broad storage access when the app only appears to need image upload
- privacy or user-agreement links still pointing to test domains

## Manual verification prompts

Ask for manual confirmation of:

- account deletion path
- order, payment, and invoice privacy disclosures
- whether permission denial still allows basic browsing and account access
- whether live-commerce or scanning features truly exist if they are used to justify sensitive permissions
