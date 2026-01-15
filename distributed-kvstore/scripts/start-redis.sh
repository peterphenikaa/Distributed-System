#!/bin/bash
# Script để start 3 Redis instances cho cluster (Linux/Mac)

echo "Starting Redis instances..."

# Tạo directories nếu chưa tồn tại
mkdir -p data/redis1 data/redis2 data/redis3 logs

echo "Starting Redis on port 6379..."
redis-server config/redis-6379.conf &
sleep 2

echo "Starting Redis on port 6380..."
redis-server config/redis-6380.conf &
sleep 2

echo "Starting Redis on port 6381..."
redis-server config/redis-6381.conf &
sleep 2

echo ""
echo "All Redis instances started!"
echo "- Redis 1: localhost:6379"
echo "- Redis 2: localhost:6380"
echo "- Redis 3: localhost:6381"
echo ""
