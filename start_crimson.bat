@echo off
TITLE CRIMSON Intelligence Platform Launcher
COLOR 0C

echo ========================================================
echo         CRIMSON INTELLIGENCE PLATFORM v0.5.0
echo ========================================================
echo Starting local full-stack intelligence application...
echo.

echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "CRIMSON Backend (FastAPI)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 >nul

echo [2/2] Launching Vite Frontend on http://127.0.0.1:5173 ...
start "CRIMSON Frontend (React)" cmd /k "cd /d %~dp0frontend && npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo ========================================================
echo CRIMSON is running!
echo Access Web UI at:  http://127.0.0.1:5173
echo API Documentation: http://127.0.0.1:8000/docs
echo ========================================================
echo Demo Credentials:
echo   - Admin:   admin@crimson.intel   / crimson2026
echo   - Analyst: analyst@crimson.intel / crimson2026
echo   - Viewer:  viewer@crimson.intel  / crimson2026
echo ========================================================
pause
