# Security and release gates

Before production or public beta:

- Replace development secrets with a secret manager; fail startup when required production secrets are missing.
- Enforce authentication, server-side resource ownership, rate limiting, and abuse monitoring on private APIs.
- Record timestamped consent linked to user, source asset, and model.
- Use private object storage and short-lived signed URLs; enforce upload size/type limits and retention/deletion lifecycle.
- Make credit accounting idempotent and verify Google Play purchases server-side; never trust client balances or subscription status.
- Protect admin access with strong authentication, role-based permissions, and audit logging.
- Offer account and data deletion/retention controls.
- Run dependency, secret, container, API-authorization, and load testing.
- Confirm current Google Play Billing, AdMob, privacy disclosure, and applicable legal requirements before release.
- Complete voice consent/abuse tests and physical-device tests.

The current code has not passed these gates.
