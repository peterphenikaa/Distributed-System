# Distributed Key-Value Store - Python Version

## 🐍 Python Implementation

Hệ thống lưu trữ key-value phân tán sử dụng Python + gRPC + Redis

## 📦 Requirements

- Python 3.8+
- Redis 7.x
- gRPC Python

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate gRPC code from proto

```bash
python -m grpc_tools.protoc -I./src/proto --python_out=./src --grpc_python_out=./src ./src/proto/kvstore.proto
```

### 3. Start Redis (Optional - Phase 2A dùng in-memory)

```bash
redis-server config/redis-6379.conf
```

### 4. Start Server
    
```bash
python src/server.py
```

### 5. Run Client

```bash
python src/client.py
```

## 📁 Project Structure

```
distributed-kvstore/
├── src/
│   ├── proto/
│   │   └── kvstore.proto           # gRPC definitions
│   ├── storage/
│   │   └── storage_engine.py       # Storage implementation
│   ├── server.py                   # gRPC server
│   └── client.py                   # Test client
├── config/
│   └── cluster.json                # Cluster configuration
├── requirements.txt                # Python dependencies
└── README_PYTHON.md               # This file
```

## 🎯 Phase 2: Single Node

### Implementation Order:

1. ✅ `storage_engine.py` - In-memory storage (dict)
2. ✅ `server.py` - gRPC server + service implementation
3. ✅ `client.py` - Test client
4. ⏳ Testing PUT/GET/DELETE operations
