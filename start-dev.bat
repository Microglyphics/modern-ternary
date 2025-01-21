@echo off
REM start-dev.bat - Development startup script

echo Starting Cloud SQL Proxy...
start "Cloud SQL Proxy" cloud_sql_proxy_x64.exe -instances=modernity-worldview:us-central1:modernity-db=tcp:3307

echo Waiting for proxy to initialize...
timeout /t 5

echo Starting FastAPI server...
cd server
start "FastAPI Server" cmd /k "python -m uvicorn main:app --reload"

echo Starting frontend development server...
cd ../frontend
start "Frontend Dev Server" cmd /k "npm run dev"

echo Development environment started!
echo - Cloud SQL Proxy: Running on port 3307
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:5173