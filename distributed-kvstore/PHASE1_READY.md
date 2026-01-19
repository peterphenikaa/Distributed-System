# 🐍 Distributed Key-Value Store - Phase 1 Setup

## ✅ Phase 1 Complete - Ready to Code

### 📦 Đã Setup:

1. **Proto Definitions** ✅
   - `src/proto/kvstore.proto` - gRPC service definitions
2. **Generated gRPC Code** ✅
   - `src/kvstore_pb2.py` - Message classes
   - `src/kvstore_pb2_grpc.py` - Service stubs

3. **Dependencies** ✅
   - `requirements.txt` - Python packages
   - All installed với `pip install -r requirements.txt`

4. **Tools** ✅
   - `generate_grpc.py` - Script để re-generate gRPC code

5. **Config Files** ✅
   - `config/cluster.json` - 3 nodes configuration
   - `config/redis-*.conf` - Redis configs (for later)

---

## 📝 Files Cần Code (Phase 2):

### 1. `src/storage/storage_engine.py`

Implement storage engine với:

- `__init__()` - Initialize storage (dict hoặc Redis)
- `put(key, value)` - Lưu key-value
- `get(key)` - Lấy value
- `delete(key)` - Xóa key
- Thread-safe operations

### 2. `src/server.py`

Implement gRPC server:

- Import `kvstore_pb2` và `kvstore_pb2_grpc`
- Class kế thừa `kvstore_pb2_grpc.KeyValueStoreServicer`
- Implement methods: `Put()`, `Get()`, `Delete()`, `ListKeys()`
- Start server với `grpc.server()`

### 3. `src/client.py`

Implement test client:

- Connect đến server: `grpc.insecure_channel()`
- Create stub: `kvstore_pb2_grpc.KeyValueStoreStub(channel)`
- Test các operations: PUT, GET, DELETE

---

## 🚀 Commands:

**Re-generate gRPC code (nếu sửa proto):**

```bash
python generate_grpc.py
```

**Run server (sau khi code xong):**

```bash
python src/server.py 8001
```

**Run client (sau khi code xong):**

```bash
python src/client.py 8001
```

---

## 📚 Reference gRPC Imports:

```python
import grpc
from concurrent import futures
import kvstore_pb2
import kvstore_pb2_grpc
```

**Server class template:**

```python
class KVStoreServicer(kvstore_pb2_grpc.KeyValueStoreServicer):
    def Put(self, request, context):
        # request.key, request.value
        # return kvstore_pb2.PutResponse(...)
        pass
```

**Client template:**

```python
channel = grpc.insecure_channel('localhost:8001')
stub = kvstore_pb2_grpc.KeyValueStoreStub(channel)
response = stub.Put(kvstore_pb2.PutRequest(key="k", value="v"))
```

---

**🎯 Giờ bạn có thể tự code implementation vào 3 files trên!**
