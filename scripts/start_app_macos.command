#!/bin/bash

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/local_outputs/launcher_logs"
PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
MODEL_FILE="$PROJECT_ROOT/local_weights/best.pt"

cd "$PROJECT_ROOT" || exit 1

echo "YOLOv8 Vehicle and Pedestrian Detection"
echo "Project root: $PROJECT_ROOT"
echo

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Missing Python environment: .venv"
  echo "Ask the project maintainer to create .venv before launching this app."
  echo "Press Enter to close."
  read -r _
  exit 1
fi

if [ ! -f "$MODEL_FILE" ]; then
  echo "Missing model weight: local_weights/best.pt"
  echo "Ask the project maintainer to put best.pt in local_weights/."
  echo "Do not move or delete local_weights/best.pt after setup."
  echo "Press Enter to close."
  read -r _
  exit 1
fi

mkdir -p "$LOG_DIR"
export MODEL_PATH="$MODEL_FILE"

echo "Starting FastAPI at http://localhost:8000"
"$PYTHON_BIN" -m uvicorn src.api:app --host 127.0.0.1 --port 8000 \
  > "$LOG_DIR/fastapi.log" 2>&1 &
FASTAPI_PID=$!

echo "Starting Streamlit at http://localhost:8501"
"$PYTHON_BIN" -m streamlit run app.py \
  > "$LOG_DIR/streamlit.log" 2>&1 &
STREAMLIT_PID=$!

REACT_PID=""
if [ -d "$PROJECT_ROOT/frontend/node_modules" ]; then
  echo "Starting React frontend at http://localhost:5173"
  (
    cd "$PROJECT_ROOT/frontend" || exit 1
    npm run dev -- --host 127.0.0.1
  ) > "$LOG_DIR/react.log" 2>&1 &
  REACT_PID=$!
else
  echo "React frontend not started because frontend/node_modules is missing."
  echo "The main app still opens in Streamlit."
fi

cleanup() {
  echo
  echo "Stopping local services..."
  kill "$FASTAPI_PID" "$STREAMLIT_PID" ${REACT_PID:+"$REACT_PID"} 2>/dev/null || true
}
trap cleanup INT TERM EXIT

sleep 4
open "http://localhost:8501" >/dev/null 2>&1 || true
if [ -n "$REACT_PID" ]; then
  open "http://localhost:5173" >/dev/null 2>&1 || true
fi

echo
echo "Apps are starting:"
echo "- Streamlit: http://localhost:8501"
echo "- FastAPI:   http://localhost:8000"
if [ -n "$REACT_PID" ]; then
  echo "- React:     http://localhost:5173"
fi
echo
echo "Put local videos under local_videos/source/ or use a full file path in the UI."
echo "Results are written under local_outputs/ and are not committed to Git."
echo "To stop all services, press Control-C in this Terminal window."
echo "Logs: $LOG_DIR"
echo

wait
