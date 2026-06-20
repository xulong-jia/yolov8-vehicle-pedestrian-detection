@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%.." >nul
set "PROJECT_ROOT=%CD%"
set "PYTHON_BIN=%PROJECT_ROOT%\.venv\Scripts\python.exe"
set "MODEL_FILE=%PROJECT_ROOT%\local_weights\best.pt"

echo YOLOv8 Vehicle and Pedestrian Detection
echo Project root: %PROJECT_ROOT%
echo.

if not exist "%PYTHON_BIN%" (
  echo Missing Python environment: .venv
  echo Ask the project maintainer to create .venv before launching this app.
  pause
  popd >nul
  exit /b 1
)

if not exist "%MODEL_FILE%" (
  echo Missing model weight: local_weights\best.pt
  echo Ask the project maintainer to put best.pt in local_weights.
  echo Do not move or delete local_weights\best.pt after setup.
  pause
  popd >nul
  exit /b 1
)

if not exist "%PROJECT_ROOT%\local_outputs\launcher_logs" (
  mkdir "%PROJECT_ROOT%\local_outputs\launcher_logs"
)

set "MODEL_PATH=%MODEL_FILE%"

echo Starting FastAPI at http://localhost:8000
start "YOLOv8 FastAPI" /D "%PROJECT_ROOT%" cmd /k call "%PYTHON_BIN%" -m uvicorn src.api:app --host 127.0.0.1 --port 8000

echo Starting Streamlit at http://localhost:8501
start "YOLOv8 Streamlit" /D "%PROJECT_ROOT%" cmd /k call "%PYTHON_BIN%" -m streamlit run app.py

echo.
echo React frontend is optional on Windows. If Node is installed, run:
echo   cd frontend
echo   npm run dev
echo Then open http://localhost:5173
echo.

timeout /t 4 /nobreak >nul
start "" "http://localhost:8501"
start "" "http://localhost:8000/health"

echo Apps are starting:
echo - Streamlit: http://localhost:8501
echo - FastAPI:   http://localhost:8000
echo.
echo Put local videos under local_videos\source\ or use a full file path in the UI.
echo Results are written under local_outputs\ and are not committed to Git.
echo To stop services, close the FastAPI and Streamlit command windows.
echo.
pause
popd >nul
endlocal
