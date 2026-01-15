@echo off
REM Script để start 3 Redis instances cho cluster

echo Starting Redis instances...

REM Tạo directories nếu chưa tồn tại
if not exist "data\redis1" mkdir data\redis1
if not exist "data\redis2" mkdir data\redis2
if not exist "data\redis3" mkdir data\redis3
if not exist "logs" mkdir logs

echo Starting Redis on port 6379...
start "Redis-6379" redis-server config\redis-6379.conf

timeout /t 2 /nobreak > nul

echo Starting Redis on port 6380...
start "Redis-6380" redis-server config\redis-6380.conf

timeout /t 2 /nobreak > nul

echo Starting Redis on port 6381...
start "Redis-6381" redis-server config\redis-6381.conf

echo.
echo All Redis instances started!
echo - Redis 1: localhost:6379
echo - Redis 2: localhost:6380
echo - Redis 3: localhost:6381
echo.
echo Press any key to continue...
pause > nul
