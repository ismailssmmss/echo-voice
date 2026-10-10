# Echo Voice architecture notes

## Database model overview
- Users
- UserProfiles
- VoiceModels
- VoiceConsents
- AudioAssets
- Projects
- GenerationJobs
- JobEvents
- CreditWallets
- CreditTransactions
- SubscriptionRecords
- PurchaseRecords
- ModerationReports
- AuditLogs
- AdminUsers
- ModelRegistry
- UsageMetrics

## API and worker separation
The backend is responsible for user management, storage, and orchestration. The AI worker is responsible for the expensive cloning and generation tasks, which are scheduled asynchronously through Redis + Celery.

## Security primitives
- Signed URLs for storage access
- Strict least-privilege IAM roles
- Sensitive values stored as environment variables
- User consent tracking before voice cloning
- Audit logs for admin actions
