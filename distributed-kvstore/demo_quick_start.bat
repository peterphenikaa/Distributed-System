@echo off
REM ========================================
REM Quick Start Demo - Distributed KV Store
REM ========================================

echo.
echo ========================================
echo   Distributed Key-Value Store Demo
echo ========================================
echo.

cd /d %~dp0

REM Kill existing processes
echo [1/3] Stopping existing servers...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Start 3 nodes
echo.
echo [2/3] Starting 3-node cluster...
echo.

start /MIN "KVStore-Node1" cmd /c "python src\server.py 8001 node1"
timeout /t 2 /nobreak >nul

start /MIN "KVStore-Node2" cmd /c "python src\server.py 8002 node2"
timeout /t 2 /nobreak >nul

start /MIN "KVStore-Node3" cmd /c "python src\server.py 8003 node3"
timeout /t 3 /nobreak >nul

echo    - Node 1 started on port 8001
echo    - Node 2 started on port 8002
echo    - Node 3 started on port 8003
echo.

REM Run demo
echo [3/3] Running comprehensive demo...
echo.
echo ========================================
echo.

python demo_full_system.py

echo.
echo ========================================
echo   Demo Complete!
echo ========================================
echo.
echo Press any key to stop cluster...
pause >nul

REM Cleanup
echo.
echo Stopping cluster...
taskkill /F /FI "WindowTitle eq KVStore-Node*" 2>nul
taskkill /F /IM python.exe 2>nul

echo.
echo Cluster stopped. Goodbye!
echo.
