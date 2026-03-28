# Review Checklist

Use this checklist to translate static APK signals into practical prescreen findings.

## 1. Cross-store baseline

These checks are broadly useful across Google Play and major Android app stores:

- The package should expose clear package identity: package name, version, target sdk, app label.
- Debug or test packaging should not be submitted.
- Sensitive permissions should align with real, user-facing core features.
- Permission prompts should be contextual and incremental when the user reaches the relevant feature.
- Exported components should be intentional and minimally exposed.
- The app should not suggest silent install, forced update, hidden behavior, or abuse of the device or network.
- Privacy-related user data handling should be disclosed outside the APK as needed; static package evidence can only hint at gaps.
- Placeholder text, staging endpoints, and test environments should be removed from release builds.

## 2. Google Play-oriented checks

Map package evidence to these common review questions:

### Permissions and sensitive APIs
- Does the APK request sensitive access that is necessary for the app's promoted core functionality?
- Are there high-scrutiny permissions such as accessibility, all-files access, installed-app visibility, overlay, notification listener, sms, call log, contacts, exact alarms, or background location?
- If the permission is high-scrutiny, is there at least a plausible feature match visible in package names, strings, or components?

### Device and network abuse
- Does the APK contain strings or behavior hints suggesting self-update, silent install, executable code loading, cheating, proxying for third parties, or disruptive full-screen behavior?
- Does the manifest or strings suggest cleartext use with sensitive web content or risky webview/javascript interface patterns?

### User data and transparency
- If sensitive permissions are present, are there visible consent, rationale, privacy policy, or account deletion hints?
- If not, mark the case for manual verification rather than assuming compliance.

## 3. Mainland China / major Android app-store-oriented checks

Use these checks for stores that emphasize privacy-compliance review:

### Privacy notice and consent
- Look for strings that suggest an independent privacy policy, first-launch privacy dialog, and explicit agree/reject choices.
- Watch for wording that implies bundled or default consent.
- If the app requests sensitive permissions but no privacy-related strings are found, flag a warning.

### Necessary collection and permissions
- Sensitive personal data access should appear necessary for the feature.
- Repeated or broad permission use without visible feature justification should be flagged.
- Reject-like risks often include access to contacts, sms, call log, location, audio, camera, installed apps, device identifiers, or storage without obvious business need.

### User rights and account controls
- Look for strings indicating account deletion, permission management, revoke authorization, complaint/contact channels, or personal-data management.
- Absence of these strings is not proof of non-compliance, but it increases the need for manual review.

## 4. Severity heuristics

Use these defaults unless stronger evidence suggests otherwise:

### Blocking issue
- `android:debuggable="true"`
- `android:testOnly="true"`
- clear evidence of silent install / self-update / download executable code from outside a trusted store
- highly risky exported provider or service with no obvious protection and an attack-prone purpose

### Warning
- sensitive permissions without a clear feature match
- broad package visibility or storage access needing policy justification
- exported components that may be intentional but deserve confirmation
- cleartext traffic enabled without an obvious reason
- staging domains or placeholder strings in release resources

### Manual verification needed
- privacy policy presence in store listing or in-app web page
- explicit consent flow correctness
- account deletion flow and response time
- whether rejected permissions are gracefully handled
- whether permission prompts are contextual instead of front-loaded

## 5. Practical report language

Prefer:
- `possible review risk`
- `requires store-listing justification`
- `needs manual verification`
- `static APK evidence suggests`

Avoid:
- `will definitely be rejected`
- `fully compliant`
- legal conclusions that cannot be proven from the APK alone
