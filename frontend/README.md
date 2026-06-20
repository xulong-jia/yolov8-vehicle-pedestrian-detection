# React Video Job Frontend

This is a minimal optional React frontend for the YOLOv8 FastAPI service. It is
intended as a small front/backend separation demo, not a production dashboard.

## Scope

The frontend supports:

- `GET /health`
- `GET /model-status`
- `POST /api/videos/analyze`
- `GET /api/videos/jobs/{job_id}`
- registered artifact download links
- `POST /api/bad-cases`
- `GET /api/bad-cases`
- optional `X-API-Key`
- `X-Request-ID` input and response display

It does not include:

- video playback
- multi-user auth
- production permissions
- DeepSORT
- complex routing
- a production dashboard

## Configuration

Default API base URL:

```bash
http://localhost:8000
```

Optional environment override:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

If FastAPI API key auth is enabled, enter the key in the UI. Requests then send:

```text
X-API-Key: <your-secret>
```

## Run

```bash
cd frontend
npm install
npm run dev
```

Build check:

```bash
npm run build
```

The FastAPI backend must be running separately, for example:

```bash
uvicorn src.api:app --host 127.0.0.1 --port 8000
```
