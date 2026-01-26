# 📖 Phase 1 Complete Guide

## 🎯 Hiểu Đơn Giản Từng File Làm Gì

### 1. `kvstore.proto` (File Gốc)

**Làm gì**: Định nghĩa "hợp đồng" giữa client và server

- Giống như menu nhà hàng: liệt kê các món (PUT, GET, DELETE)
- Định nghĩa input/output của mỗi món
- **Không phải code** - chỉ là file mô tả

---

### 2. `kvstore_pb2.py` (Generated - Messages)

**Làm gì**: Chứa các "hộp đựng dữ liệu"

- Tự động generate từ file `.proto`
- Ví dụ: `PutRequest(key="user1", value="Alice")`
- Giống như form đơn hàng với các ô cần điền
- **Không cần đọc file này** - chỉ cần biết cách dùng

---

### 3. `kvstore_pb2_grpc.py` (Generated - Services)

**Làm gì**: Chứa "khuôn mẫu" cho server và client

- `KeyValueStoreServicer`: Class mẫu cho **server** (kế thừa để implement)
- `KeyValueStoreStub`: Class để **client** gọi server
- **Không cần đọc file này** - chỉ import và dùng

---

### 4. `server.py` (Your Code)

**Làm gì**: Máy chủ nhận requests và xử lý

```
Client gửi PUT → Server nhận → Lưu data → Trả response
```

- Kế thừa `KeyValueStoreServicer`
- Implement các methods: Put(), Get(), Delete()
- Chạy liên tục, chờ requests

**Hiện tại**: Chỉ nhận request và in ra log (chưa lưu data thật)

---

### 5. `client.py` (Your Code)

**Làm gì**: Người gửi requests đến server

```
Client tạo request → Gửi qua network → Nhận response
```

- Dùng `KeyValueStoreStub` để gọi remote methods
- Giống như app trên điện thoại gọi đến server

---

### 6. `generate_grpc.py` (Tool Script)

**Làm gì**: Công cụ để generate code từ `.proto`

- Đọc `kvstore.proto`
- Tạo ra `kvstore_pb2.py` và `kvstore_pb2_grpc.py`
- Chỉ chạy 1 lần khi có thay đổi proto file

---

## 🧪 Cách Test Phase 1 (Task 1.4)

### Bước 1: Start Server

```powershell
# Terminal 1 - Chạy server
python src/server.py 8001
```

**Kết quả mong đợi:**

```
✅ KeyValueStoreServicer initialized
🎯 Starting server on port 8001...
🚀 Server started on port 8001
📡 Listening on [::]:8001
Press Ctrl+C to stop
```

✅ **Test pass nếu**: Thấy dòng "Server started" và không có error

---

### Bước 2: Test Client Connect

```powershell
# Terminal 2 - Chạy client (giữ server chạy)
python src/client.py
```

**Kết quả mong đợi:**

```
✅ Connected to server at localhost:8001

🧪 Testing basic operations...

📤 Sending PUT: user:1 = Alice
✅ PUT successful
📥 Sending GET: user:1
✅ GET successful
🗑️ Sending DELETE: user:1
✅ DELETE successful
📋 Sending ListKeys
✅ ListKeys successful
🔌 Connection closed

✅ All tests completed!
```

**Server terminal sẽ hiển thị:**

```
📥 Received PUT request: key=user:1
📤 Received GET request: key=user:1
🗑️ Received DELETE request: key=user:1
📋 Received ListKeys request
```

✅ **Test pass nếu**:

- Client connect thành công
- Server nhận được 4 requests
- Không có error/exception

---

### Bước 3: Stop Server

Quay lại Terminal 1, nhấn `Ctrl+C`:

```
^C
⏹️ Server stopping...
✅ Server stopped
```

---

## ✅ Phase 1 Success Criteria

- [x] `kvstore_pb2.py` và `kvstore_pb2_grpc.py` generated thành công
- [x] Server start được và listen trên port 8001
- [x] Client connect được đến server
- [x] Client gửi requests thành công
- [x] Server nhận và xử lý requests (in log)
- [x] Không có import errors
- [x] Không có runtime errors

---

## 🎓 Tóm Tắt Luồng Hoạt Động

```
1. Proto File (.proto)
   ↓ (generate_grpc.py)
2. Generated Files (_pb2.py, _pb2_grpc.py)
   ↓
3. Server (server.py) - Listen và chờ requests
   ↑
   | gRPC (qua network)
   ↓
4. Client (client.py) - Gửi requests
```

**Hiện tại (Phase 1)**:

- ✅ Kết nối hoạt động
- ✅ Requests được gửi/nhận
- ❌ Chưa lưu data thật (Phase 2 mới làm)

---

## 🚀 Next Steps

**Phase 2** sẽ thêm:

- Storage engine (dict để lưu data)
- Logic thật cho Put/Get/Delete
- Error handling
- Logging system

**Bây giờ**: Tập trung hiểu luồng hoạt động, chạy test thành công là được!
