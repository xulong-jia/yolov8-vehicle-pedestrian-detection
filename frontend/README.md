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

The FastAPI backend allows the local React dev server by default through CORS:

```text
http://localhost:5173
http://127.0.0.1:5173
```

If the frontend runs from a different origin, start FastAPI with an explicit
allow-list:

```bash
CORS_ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173 \
  uvicorn src.api:app --host 127.0.0.1 --port 8000
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

## npm Audit Note

At the `v1.8.1-final-polish-and-frontend-audit-note` documentation pass,
`npm audit` reports:

- 1 moderate finding
- 1 high finding
- affected path: Vite/esbuild development/build dependency chain

The npm suggested fix requires a semver-major upgrade to Vite 8. This project
does not run `npm audit fix --force` in the final polish scope because that
would be a dependency-major migration rather than a documentation-only freeze
step.

Production deployment should review and upgrade frontend dependencies in a
separate controlled dependency-refresh phase.
