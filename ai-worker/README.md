# Echo Voice AI Worker

The AI worker is a dedicated service for model execution, generation jobs, and orchestration.

## Run locally

```bash
cd ai-worker
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
