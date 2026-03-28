# Review Checklist

This file remains as a lightweight compatibility index.

Use the new layered references instead:

- `references/guidelines/by-app-type/all_apps.md`
- `references/guidelines/by-app-type/ecommerce.md`
- `references/guidelines/by-app-type/health_fitness.md`
- `references/guidelines/by-app-type/utilities.md`
- `references/rules/permissions/request_install_packages.md`
- `references/rules/network/cleartext_traffic.md`
- `references/rules/privacy/privacy_entry.md`
- `references/rules/privacy/account_deletion.md`
- `references/rules/metadata/test_or_staging_domain.md`
- `references/rules/components/exported_components.md`
- `references/rules/storefront/china_material_consistency.md`

Workflow summary:

1. Load `all_apps.md`
2. Infer app type and load matching app-type guide
3. Load only the rule cards triggered by the APK findings or materials
4. Output in platform-first format, then missing items, then uppercase final summary
