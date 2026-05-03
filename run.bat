@echo off
REM Organic Roots - Windows Startup Script
REM Starts both backend and frontend services

setlocal EnableDelayedExpansion

REM Colors for output (limited in Windows batch)
set "INFO=[INFO]"
set "WARN=[WARN]"
set "ERROR=[ERROR]"

echo ========================================
echo   Organic Roots Startup Script (Windows)
echo ========================================
echo.

REM Function to print status
:print_status
echo %INFO% %~1
goto :eof

:print_warning
echo %WARN% %~1
goto :eof

:print_error
echo %ERROR% %~1
goto :eof

REM Check if Python is installed
call :print_status "Checking Python installation..."
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python is not installed or not in PATH"
    exit /b 1
)
call :print_status "Python found"

REM Check if Node.js is installed
call :print_status "Checking Node.js installation..."
node --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Node.js is not installed or not in PATH"
    exit /b 1
)
call :print_status "Node.js found"

REM Check if we're in the right directory
if not exist "backend\main.py" (
    call :print_error "backend\main.py not found. Please run this script from the project root."
    exit /b 1
)

if not exist "frontend\package.json" (
    call :print_error "frontend\package.json not found. Please run this script from the project root."
    exit /b 1
)

REM Check if ports are in use
call :print_status "Checking if ports are available..."

REM Check port 8000 (backend)
netstat -an | findstr "8000" | findstr "LISTENING" >nul
if not errorlevel 1 (
    call :print_warning "Port 8000 is in use. Attempting to close existing process..."
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

REM Check port 5173 (frontend)
netstat -an | findstr "5173" | findstr "LISTENING" >nul
if not errorlevel 1 (
    call :print_warning "Port 5173 is in use. Attempting to close existing process..."
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

REM Install backend dependencies
call :print_status "Installing backend dependencies..."
cd backend
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    call :print_error "Failed to install backend dependencies"
    cd ..
    exit /b 1
)
call :print_status "Backend dependencies installed"
cd ..

REM Start backend in background
call :print_status "Starting FastAPI backend server..."
cd backend
start "Organic Roots Backend" cmd /k "uvicorn main:app --reload --port 8000"
cd ..
call :print_status "Backend server starting on http://localhost:8000"

REM Wait for backend to be ready
call :print_status "Waiting for backend to be ready..."
timeout /t 5 /nobreak >nul

REM Install frontend dependencies
call :print_status "Installing frontend dependencies..."
cd frontend
npm install >nul 2>&1
if errorlevel 1 (
    call :print_error "Failed to install frontend dependencies"
    cd ..
    exit /b 1
)
call :print_status "Frontend dependencies installed"
cd ..

REM Start frontend in background
call :print_status "Starting Vite frontend server..."
cd frontend
start "Organic Roots Frontend" cmd /k "npm run dev"
cd ..
call :print_status "Frontend server starting on http://localhost:5173"

REM Wait for frontend to be ready
call :print_status "Waiting for frontend to be ready..."
timeout /t 5 /nobreak >nul

echo.
echo ========================================
call :print_status "Both services started successfully!"
echo.
echo   Frontend: http://localhost:5173
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo   Use 'run.bat stop' to stop all services
echo   Use 'run.bat status' to check service status
echo ========================================
goto :end

:stop
echo.
call :print_status "Stopping services..."
taskkill /FI "WINDOWTITLE eq Organic Roots Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Organic Roots Frontend*" /F >nul 2>&1
taskkill /F /IM uvicorn.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
call :print_status "All services stopped"
goto :end

:status
echo.
call :print_status "Checking service status..."
netstat -an | findstr "8000" | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo   [RUNNING] Backend on port 8000
) else (
    echo   [STOPPED] Backend on port 8000
)
netstat -an | findstr "5173" | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo   [RUNNING] Frontend on port 5173
) else (
    echo   [STOPPED] Frontend on port 5173
)
goto :end

:help
echo.
echo Usage: run.bat [command]
echo.
echo Commands:
echo   start     Start both backend and frontend services (default)
echo   stop      Stop all services
echo   status    Check service status
echo   help      Show this help message
echo.
echo Examples:
echo   run.bat        ^(same as run.bat start^)
echo   run.bat stop   ^(stop all services^)
echo   run.bat status ^(check service status^)
goto :end

:end
endlocal
