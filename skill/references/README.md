# References Overview

This directory is organized into two layers:

- `guidelines/`: app-type playbooks that describe what to review for a class of app
- `rules/`: reusable rule cards for specific risk themes, permissions, metadata issues, or store expectations
 - `runtime-smoke.md`: optional runtime evidence checklist for dynamic verification

Recommended usage:

1. Always load `guidelines/by-app-type/all_apps.md`
2. Infer the app type, then load one or more matching app-type guides
3. Load only the rule cards that match the static APK findings or the uploaded submission materials
4. Write the report in platform-first form, then list missing items, then end with an uppercase final summary

This layout keeps the top-level skill prompt small while making policy content easier to maintain and extend.
