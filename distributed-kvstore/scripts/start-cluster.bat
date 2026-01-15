@echo off
REM Script để build và start cluster (3 nodes)

echo Building project...
call mvn clean package -DskipTests
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Starting cluster nodes...
echo.

REM Start Node 1
echo Starting Node 1 (port 8001)...
start "Node-1" java -jar target\kvstore-1.0.0.jar --node-id=node1 --port=8001 --redis-host=localhost --redis-port=6379 --config=config\cluster.json

timeout /t 3 /nobreak > nul

REM Start Node 2
echo Starting Node 2 (port 8002)...
start "Node-2" java -jar target\kvstore-1.0.0.jar --node-id=node2 --port=8002 --redis-host=localhost --redis-port=6380 --config=config\cluster.json

timeout /t 3 /nobreak > nul

REM Start Node 3
echo Starting Node 3 (port 8003)...
start "Node-3" java -jar target\kvstore-1.0.0.jar --node-id=node3 --port=8003 --redis-host=localhost --redis-port=6381 --config=config\cluster.json

echo.
echo All nodes started!
echo - Node 1: localhost:8001 (Redis: 6379)
echo - Node 2: localhost:8002 (Redis: 6380)
echo - Node 3: localhost:8003 (Redis: 6381)
echo.
echo Press any key to continue...
pause > nul
