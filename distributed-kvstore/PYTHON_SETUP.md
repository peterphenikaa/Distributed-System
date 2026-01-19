# 🐍 Distributed Key-Value Store - Python

## ✅ Cấu Trúc Project (Cleaned)

```
distributed-kvstore/
├── src/
│   ├── proto/
│   │   └── kvstore.proto           # gRPC service definitions
│   ├── storage/
│   │   ├── __init__.py
│   │   └── storage_engine.py       # In-memory storage engine
│   ├── server.py                   # gRPC server
│   ├── client.py                   # Test client
│   └── __init__.py
├── config/
│   ├── cluster.json                # Cluster config (3 nodes)
│   └── redis-*.conf                # Redis configs
├── scripts/
│   └── start-*.bat/sh              # Start scripts
├── requirements.txt                # Python dependencies
├── generate_grpc.py                # Script để generate gRPC code
└── README_PYTHON.md               # Documentation

❌ Đã xóa: Java code, pom.xml, target/, src/main/, src/test/
```

## 🚀 Setup & Run

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Generate gRPC Code

```bash
python generate_grpc.py
```

Sẽ tạo ra:

- `src/kvstore_pb2.py` - Message classes
- `src/kvstore_pb2_grpc.py` - Service stubs

### 3️⃣ Start Server

```bash
python src/server.py
```

### 4️⃣ Test Client

```bash
python src/client.py
```

## 📋 Phase 2 Status

### ✅ Completed:

- [x] Clean Java codebase
- [x] Setup Python structure
- [x] Create StorageEngine (in-memory, thread-safe)
- [x] Create gRPC server template
- [x] Create test client template
- [x] Generate script cho gRPC code

### ⏳ Next Steps:

1. Chạy `python generate_grpc.py` để generate gRPC code
2. Uncomment import statements trong server.py & client.py
3. Test PUT/GET/DELETE operations
4. (Optional) Chuyển từ dict sang Redis

## 🎯 Features (Phase 2)

- ✅ **StorageEngine**: Dictionary-based, thread-safe với `threading.RLock()`
- ✅ **gRPC Server**: Implement PUT, GET, DELETE
- ✅ **Client**: Test client với error handling
- 🔄 **Next**: Redis integration (Phase 2B)

## 📝 Notes

**Phase 2A**: In-memory storage (ConcurrentHashMap equivalent)

- Nhanh, đơn giản
- Test logic gRPC
- ❌ Data mất khi restart

**Phase 2B**: Redis storage (Later)

- Persistent
- Production-ready
- ✅ Data survive restarts

---

Xem [README.md](README.md) để biết full roadmap (7 phases)
