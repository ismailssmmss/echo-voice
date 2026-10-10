# Database schema

The schema should be created using Alembic/Migrations. The following tables are required:

- users
- user_profiles
- voice_models
- voice_consents
- audio_assets
- projects
- generation_jobs
- job_events
- credit_wallets
- credit_transactions
- subscription_records
- purchase_records
- moderation_reports
- audit_logs
- admin_users
- model_registry
- usage_metrics

Implementation should also include indexes on user_id, voice_model_id, project_id, job_id, subscription_status, and updated_at timestamps.
