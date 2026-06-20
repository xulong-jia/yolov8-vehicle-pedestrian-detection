# FastAPI Usage

## Purpose

The FastAPI service exposes basic image inference endpoints for local and
integration use. It follows the project rule that the API layer does not call
YOLO directly: model loading is isolated in `src/core/model_loader.py`, and image
decoding plus inference live in `src/services/image_inference_service.py`.

## Run Locally

```bash
.venv/bin/uvicorn src.api:app --host 0.0.0.0 --port 8000
```

The app can also be imported as `src.api:app` by Uvicorn. Importing `src.api`
does not load model weights and does not import Ultralytics.

## Configuration

Defaults come from `src/core/config.py` and can be overridden with environment
variables:

- `MODEL_PATH`
- `YOLO_DEVICE`
- `YOLO_CONF`
- `YOLO_IMGSZ`

Model weights must be local or mounted. They are not committed to Git.

## Endpoints

### GET /health

```bash
curl http://localhost:8000/health
```

Example response:

```json
{
  "status": "ok",
  "service": "yolov8-vehicle-pedestrian-api"
}
```

### GET /config

```bash
curl http://localhost:8000/config
```

Example response:

```json
{
  "project_name": "YOLOv8 Vehicle and Pedestrian Detection System",
  "model_path": "local_weights/yolov8s_640_50epochs/best.pt",
  "device": "cpu",
  "confidence_threshold": 0.25,
  "image_size": 640,
  "supported_image_types": ["jpg", "jpeg", "png", "bmp", "webp"]
}
```

### GET /model-status

```bash
curl http://localhost:8000/model-status
```

This endpoint checks path existence and loader cache status. It does not load
YOLO.

Example response:

```json
{
  "model_path": "local_weights/yolov8s_640_50epochs/best.pt",
  "exists": false,
  "loaded": false,
  "device": "cpu",
  "confidence_threshold": 0.25,
  "image_size": 640
}
```

### POST /predict

```bash
curl -X POST "http://localhost:8000/predict?conf=0.25&imgsz=640&device=cpu" \
  -F "file=@sample.jpg"
```

Optional query parameters:

- `model_path`
- `conf`
- `imgsz`
- `device`

Example response:

```json
{
  "image_name": "sample.jpg",
  "image_size": {
    "width": 1280,
    "height": 720
  },
  "model_path": "local_weights/yolov8s_640_50epochs/best.pt",
  "confidence_threshold": 0.25,
  "image_size_requested": 640,
  "device": "cpu",
  "num_detections": 1,
  "detections": [
    {
      "class_id": 1,
      "class_name": "Car",
      "confidence": 0.91,
      "bbox": {
        "xmin": 1.0,
        "ymin": 2.0,
        "xmax": 3.0,
        "ymax": 4.0
      }
    }
  ]
}
```

No detections are returned as:

```json
{
  "num_detections": 0,
  "detections": []
}
```

### POST /api/videos/analyze

```bash
curl -X POST http://localhost:8000/api/videos/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "demo",
    "run_name": "demo_run",
    "run_dir": "/tmp/yolov8_real_smoke/video_analysis/demo_run"
  }'
```

`v0.13.1` implements this as a video job/result query skeleton. It creates an
in-memory job record and can attach that record to an existing
VideoAnalysisCenter run directory. It does not run YOLO, ByteTrack, DeepSORT,
analytics, or video rendering.

Example response:

```json
{
  "job_id": "job_000001",
  "status": "attached",
  "video_id": "demo",
  "run_name": "demo_run",
  "run_dir": "/tmp/yolov8_real_smoke/video_analysis/demo_run",
  "created_at": "2026-06-20T00:00:00Z",
  "message": "Attached to existing VideoAnalysisCenter artifacts."
}
```

When `run_dir` is omitted, the job is created with `status="created"` only.
Real async execution is planned later.

### GET /api/videos/jobs/{job_id}

```bash
curl http://localhost:8000/api/videos/jobs/job_000001
```

Returns the in-memory job record. Unknown jobs return `404`.

### GET /api/videos/jobs/{job_id}/detections

```bash
curl "http://localhost:8000/api/videos/jobs/job_000001/detections?max_rows=100"
```

Reads an existing `detections.csv` from the attached run directory.

### GET /api/videos/jobs/{job_id}/tracks

```bash
curl "http://localhost:8000/api/videos/jobs/job_000001/tracks?max_rows=100"
```

Reads an existing `tracks.csv` from the attached run directory.

### GET /api/videos/jobs/{job_id}/analytics

```bash
curl "http://localhost:8000/api/videos/jobs/job_000001/analytics?max_rows=100"
```

Reads existing VideoAnalysisCenter analytics artifacts:

- `video_analysis_summary.json`
- `count_events.csv`
- `roi_frame_counts.csv`

### GET /api/videos/jobs/{job_id}/events

```bash
curl "http://localhost:8000/api/videos/jobs/job_000001/events?max_rows=100"
```

Reads an existing `events.jsonl` from the attached run directory.

## Runtime Behavior

- The model is lazy-loaded on the first valid `/predict` call.
- `/health`, `/config`, and `/model-status` do not load YOLO.
- Uploads are read and decoded in memory.
- Uploaded images are not written to the repository.
- The image API does not write `runs/`, `local_outputs/`, CSV, JSON, or image outputs.
- The video job skeleton uses an in-memory registry and reads existing artifacts
  only; it does not write files or start background work.
- Error responses are short and point to the failed input or runtime condition.

## Out of Scope for v0.13.1

The following are planned later and are not part of the basic service
acceptance or video job skeleton steps:

- actual video analyze async execution
- YOLO/ByteTrack execution from API requests
- analytics execution from API requests
- tracked video rendering from API requests
- database integration
- Docker production validation
- React frontend
- Streamlit job launching

## Tests

```bash
PYTHONPYCACHEPREFIX=/private/tmp/yolov8_pycache .venv/bin/python -m pytest tests/test_api.py tests/test_api_video_jobs.py -q
```

Tests use FastAPI `TestClient`, in-memory images, and monkeypatched services.
They do not load real YOLO weights, run real inference, run trackers, execute
analytics, or render videos.

## Related Files

- `src/api.py`
- `src/core/config.py`
- `src/core/model_loader.py`
- `src/core/schemas.py`
- `src/services/image_inference_service.py`
- `src/services/video_job_service.py`
- `tests/test_api.py`
- `tests/test_api_video_jobs.py`
