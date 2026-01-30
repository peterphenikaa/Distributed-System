@echo off
REM Script để start cluster (3 nodes) - Python version

echo ========================================
echo Starting Distributed KV Store Cluster
echo ========================================

cd /d %~dp0\..

REM Kill existing Python processes to avoid port conflicts
echo Stopping existing servers...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting cluster nodes...
echo.

REM Start Node 1
echo Starting Node 1 (port 8001)...
start "Node-1" cmd /k "python src\server.py 8001 node1"

timeout /t 2 /nobreak >nul

REM Start Node 2
echo Starting Node 2 (port 8002)...
start "Node-2" cmd /k "python src\server.py 8002 node2"

timeout /t 2 /nobreak >nul

REM Start Node 3
echo Starting Node 3 (port 8003)...
start "Node-3" cmd /k "python src\server.py 8003 node3"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo All nodes started!
echo - Node 1: localhost:8001
echo - Node 2: localhost:8002
echo - Node 3: localhost:8003
echo ========================================
echo.
echo Press any key to stop all nodes...
pause >nul

REM Stop all nodes
echo Stopping cluster...
taskkill /F /FI "WindowTitle eq Node-1*" 2>nul
taskkill /F /FI "WindowTitle eq Node-2*" 2>nul
taskkill /F /FI "WindowTitle eq Node-3*" 2>nul

echo Cluster stopped.

