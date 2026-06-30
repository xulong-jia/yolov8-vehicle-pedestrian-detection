#!/bin/bash

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/local_outputs/launcher_logs"
PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
MODEL_FILE="$PROJECT_ROOT/local_weights/best.pt"
FASTAPI_PORT=8010
STREAMLIT_PORT=8511
REACT_PORT=5178

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
export CORS_ALLOW_ORIGINS="http://localhost:$REACT_PORT,http://127.0.0.1:$REACT_PORT,http://localhost:$STREAMLIT_PORT,http://127.0.0.1:$STREAMLIT_PORT"

require_port_free() {
  local port="$1"
  local owner
  owner="$(lsof -nP -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [ -n "$owner" ]; then
    echo "Port $port is already in use:"
    echo "$owner"
    echo "Stop that service first, then run this launcher again."
    exit 1
  fi
}

require_port_free "$FASTAPI_PORT"
require_port_free "$STREAMLIT_PORT"
if [ -d "$PROJECT_ROOT/frontend/node_modules" ]; then
  require_port_free "$REACT_PORT"
fi

echo "Starting FastAPI"
echo "- URL:   http://localhost:$FASTAPI_PORT"
echo "- Entry: src.api:app"
"$PYTHON_BIN" -m uvicorn src.api:app --host 127.0.0.1 --port "$FASTAPI_PORT" \
  > "$LOG_DIR/fastapi.log" 2>&1 &
FASTAPI_PID=$!
echo "- PID:   $FASTAPI_PID"

echo "Starting Streamlit"
echo "- URL:   http://localhost:$STREAMLIT_PORT"
echo "- Entry: app.py"
"$PYTHON_BIN" -m streamlit run app.py --server.address 127.0.0.1 --server.port "$STREAMLIT_PORT" \
  > "$LOG_DIR/streamlit.log" 2>&1 &
STREAMLIT_PID=$!
echo "- PID:   $STREAMLIT_PID"

REACT_PID=""
if [ -d "$PROJECT_ROOT/frontend/node_modules" ]; then
  echo "Starting React frontend"
  echo "- URL:   http://localhost:$REACT_PORT"
  echo "- Entry: frontend/index.html"
  (
    cd "$PROJECT_ROOT/frontend" || exit 1
    VITE_API_BASE_URL="http://localhost:$FASTAPI_PORT" npm run dev -- --host 127.0.0.1 --port "$REACT_PORT" --strictPort
  ) > "$LOG_DIR/react.log" 2>&1 &
  REACT_PID=$!
  echo "- PID:   $REACT_PID"
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
open "http://localhost:$STREAMLIT_PORT" >/dev/null 2>&1 || true
if [ -n "$REACT_PID" ] && kill -0 "$REACT_PID" 2>/dev/null; then
  open "http://localhost:$REACT_PORT" >/dev/null 2>&1 || true
fi

echo
echo "Apps are starting:"
echo "- Streamlit: http://localhost:$STREAMLIT_PORT"
echo "- FastAPI:   http://localhost:$FASTAPI_PORT"
if [ -n "$REACT_PID" ]; then
  echo "- React:     http://localhost:$REACT_PORT"
fi
echo
echo "Put local videos under local_videos/source/ or use a full file path in the UI."
echo "Results are written under local_outputs/ and are not committed to Git."
echo "To stop all services, press Control-C in this Terminal window."
echo "Logs: $LOG_DIR"
echo

wait
