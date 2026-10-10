# Security and release gates

Before production or public testing:

- Replace wildcard CORS and development credentials; keep secrets in a managed secret store.
- Add authentication to all private routes, server-side authorization/ownership checks, rate limiting, and abuse monitoring.
- Record timestamped consent statements and link them to user, voice model, and source asset.
- Require private storage, short-lived signed URLs, size/type limits, malware/content validation where appropriate, and lifecycle deletion.
- Implement idempotent credits and billing verification server-side; never trust client-supplied balances or subscription states.
- Restrict admin access with strong authentication, role-based permissions, and audit logs.
- Provide account/data deletion and retention controls.
- Run dependency, secret, container, API authorization, and load scans.
- Confirm Google Play Billing, AdMob, privacy disclosures, and applicable legal requirements against current official policies before release.
- Complete voice consent/abuse tests and test on physical Android devices.

The current scaffold has not passed these gates.
