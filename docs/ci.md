# CI notes

Basic checks should include:
- backend unit tests
- linting for Python
- build verification for admin web
- optional Android Gradle configuration validation when Android SDK is available

Suggested commands:
```bash
cd backend && pytest
cd admin-web && npm install && npm run build
```
