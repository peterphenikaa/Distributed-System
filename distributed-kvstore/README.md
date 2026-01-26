# 🚀 Distributed Key-Value Store System1

## 📝 Tổng Quan Dự Án

Hệ thống lưu trữ key-value phân tán với khả năng chịu lỗi, sử dụng **gRPC** + **Python** + **Redis**. Hệ thống cho phép nhiều nodes hoạt động cùng nhau, tự động phân phối dữ liệu và đảm bảo tính sẵn sàng khi có node bị lỗi.

### 🎯 Mục Tiêu Chính5

- Xây dựng distributed key-value store từ đầu
- Học và apply các concepts: gRPC, Consistent Hashing, Replication, Failure Detection
- Tạo hệ thống có khả năng scale và fault-tolerant

---

## 📦 Codebase Ban Đầu

```
distributed-kvstore/
├── src/
│   ├── proto/
│   │   └── kvstore.proto           # gRPC service definitions
│   ├── storage/
│   │   └── __init__.py
│   ├── server.py                   # (empty - cần implement)
│   ├── client.py                   # (empty - cần implement)
│   └── __init__.py
├── config/
│   ├── cluster.json                # Config cho 3 nodes
│   └── redis-*.conf                # Redis configs
├── scripts/
│   └── start-*.bat/sh              # Scripts để start cluster
├── requirements.txt                # Python dependencies
├── generate_grpc.py                # Script để generate gRPC code
└── README.md                       # File này
```

### ✅ Đã Setup Sẵn:

1. **Proto Definitions** (`src/proto/kvstore.proto`)
   - Services: `KeyValueStore`, `NodeService`
   - Messages: PUT/GET/DELETE requests & responses
   - Inter-node communication messages

2. **Dependencies** (`requirements.txt`)
   - gRPC + Protobuf
   - Redis client

3. **Config Files**
   - Cluster config cho 3 nodes (ports 8001, 8002, 8003)
   - Redis configs cho 3 instances (ports 6379, 6380, 6381)

---

## 🏗️ Kiến Trúc Hệ Thống

```
       CLIENT
          │
          ▼ gRPC
    ┌─────────────┐
    │   Node 1    │◄──────┐
    │  (Port 8001)│       │
    └──────┬──────┘       │ gRPC P2P
           │              │ (Replication,
    ┌──────▼──────┐       │  Heartbeat)
    │   Redis 1   │       │
    │ (Port 6379) │       │
    └─────────────┘       │
                          │
    ┌─────────────┐       │
    │   Node 2    │◄──────┤
    │  (Port 8002)│       │
    └──────┬──────┘       │
           │              │
    ┌──────▼──────┐       │
    │   Redis 2   │       │
    │ (Port 6380) │       │
    └─────────────┘       │
                          │
    ┌─────────────┐       │
    │   Node 3    │◄──────┘
    │  (Port 8003)│
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │   Redis 3   │
    │ (Port 6381) │
    └─────────────┘
```

---

## 📅 Development Plan - Chia Tasks cho Team

### 👥 Team Members

- **Linh**: Junior Developer (implement basic features trước)
- **Bình**: Senior Developer (implement core features, integrate & test)

### 🔄 Workflow

1. **Linh** code xong → commit code
2. **Bình** review, implement phần quan trọng, integrate với code của Linh
3. **Bình** test đầy đủ theo document
4. ✅ Test pass → Move to next phase
5. ❌ Test fail → Fix bugs → Re-test

---

## 📋 Phase 1: Setup & Basic gRPC (1 ngày)

**Goal**: Generate gRPC code, tạo server/client template

### 🔧 Tasks

| Task                               | Owner    | Time  | Description                                     |
| ---------------------------------- | -------- | ----- | ----------------------------------------------- |
| 1.1: Generate gRPC code            | **Linh** | 30min | Chạy `python generate_grpc.py` và verify        |
| 1.2: Create basic server structure | **Linh** | 1h    | Tạo `server.py` với class kế thừa gRPC Servicer |
| 1.3: Create basic client           | **Linh** | 1h    | Tạo `client.py` với connect & stub              |
| 1.4: Test server startup           | **Bình** | 30min | Verify server start không error                 |

### ✅ Success Criteria (Phase 1)

- [ ] `kvstore_pb2.py` và `kvstore_pb2_grpc.py` generated thành công
- [ ] Server start được và listen trên port 8001
- [ ] Client connect được đến server (chưa cần PUT/GET hoạt động)
- [ ] Không có import errors

---

## 📋 Phase 2: Single Node Storage (2 ngày)

**Goal**: Implement 1 node với in-memory storage hoạt động đầy đủ

### 🔧 Tasks - Day 1

| Task                          | Owner    | Time | Description                                              |
| ----------------------------- | -------- | ---- | -------------------------------------------------------- |
| 2.1: StorageEngine với dict   | **Linh** | 2h   | Implement `storage_engine.py` với dict + threading.RLock |
| 2.2: Implement Put handler    | **Linh** | 1h   | Handler `Put()` trong server                             |
| 2.3: Implement Get handler    | **Linh** | 1h   | Handler `Get()` trong server                             |
| 2.4: Implement Delete handler | **Linh** | 1h   | Handler `Delete()` trong server                          |

### 🔧 Tasks - Day 2

| Task                     | Owner    | Time | Description                                         |
| ------------------------ | -------- | ---- | --------------------------------------------------- |
| 2.5: Client test methods | **Linh** | 2h   | Implement `put()`, `get()`, `delete()` trong client |
| 2.6: Add error handling  | **Bình** | 1h   | Try-catch trong server handlers                     |
| 2.7: Add logging         | **Bình** | 1h   | Setup logging cho debug                             |
| 2.8: Integration test    | **Bình** | 2h   | Test đầy đủ PUT/GET/DELETE workflow                 |

### ✅ Success Criteria (Phase 2)

- [ ] PUT key-value thành công
- [ ] GET key trả về đúng value
- [ ] DELETE key thành công
- [ ] GET key đã delete → NOT FOUND
- [ ] Multiple clients connect cùng lúc không bị race condition
- [ ] Logs rõ ràng mỗi operation

---

## 📋 Phase 3: Multiple Nodes + Consistent Hashing (3 ngày)

**Goal**: 3 nodes phân chia data theo Consistent Hashing

### 🔧 Tasks - Day 1

| Task                               | Owner    | Time | Description                            |
| ---------------------------------- | -------- | ---- | -------------------------------------- |
| 3.1: ConsistentHash implementation | **Linh** | 3h   | Implement consistent hashing algorithm |
| 3.2: Hash ring với virtual nodes   | **Linh** | 2h   | Add virtual nodes để balance tốt hơn   |
| 3.3: Unit test ConsistentHash      | **Linh** | 1h   | Test hash distribution                 |

### 🔧 Tasks - Day 2

| Task                              | Owner    | Time | Description                           |
| --------------------------------- | -------- | ---- | ------------------------------------- |
| 3.4: MembershipManager            | **Linh** | 2h   | Load cluster config, manage node list |
| 3.5: Determine owner node         | **Bình** | 2h   | Logic xác định key thuộc node nào     |
| 3.6: Implement request forwarding | **Bình** | 3h   | Forward request đến đúng node         |

### 🔧 Tasks - Day 3

| Task                      | Owner    | Time | Description                          |
| ------------------------- | -------- | ---- | ------------------------------------ |
| 3.7: NodeService handlers | **Bình** | 2h   | Implement ForwardPut/Get/Delete      |
| 3.8: Start 3 nodes script | **Linh** | 1h   | Script để start 3 nodes dễ dàng      |
| 3.9: Test distribution    | **Bình** | 3h   | Test data phân chia đều giữa 3 nodes |

### ✅ Success Criteria (Phase 3)

- [ ] Start 3 nodes thành công
- [ ] Client connect đến bất kỳ node nào
- [ ] PUT key → Data lưu vào đúng owner node
- [ ] GET key từ node khác → Forward và trả về đúng
- [ ] Data distribution tương đối đều (~33% mỗi node)

---

## 📋 Phase 4: Replication (2 ngày)

**Goal**: Mỗi key có 2 copies (primary + 1 replica)

### 🔧 Tasks - Day 1

| Task                        | Owner    | Time | Description                         |
| --------------------------- | -------- | ---- | ----------------------------------- |
| 4.1: ReplicationManager     | **Linh** | 2h   | Class quản lý replication           |
| 4.2: Determine replica node | **Linh** | 2h   | Logic chọn replica node (successor) |
| 4.3: Replicate RPC call     | **Linh** | 2h   | Gửi ReplicateRequest đến replica    |

### 🔧 Tasks - Day 2

| Task                          | Owner    | Time | Description                              |
| ----------------------------- | -------- | ---- | ---------------------------------------- |
| 4.4: Handle Replicate request | **Bình** | 2h   | Xử lý ReplicateRequest trong NodeService |
| 4.5: Update PUT flow          | **Bình** | 2h   | PUT → Save local + Replicate             |
| 4.6: Update DELETE flow       | **Bình** | 1h   | DELETE → Delete local + Replicate delete |
| 4.7: Test replication         | **Bình** | 2h   | Verify mỗi key có 2 copies               |

### ✅ Success Criteria (Phase 4)

- [ ] PUT key → 2 nodes có data (primary + replica)
- [ ] Verify data tồn tại trên cả 2 nodes
- [ ] DELETE key → Xóa trên cả 2 nodes
- [ ] Replication không block client (async nếu có thể)

---

## 📋 Phase 5: Failure Detection (2 ngày)

**Goal**: Phát hiện node failure và redirect requests

**Note**: Phase phức tạp, cần senior handle toàn bộ

### 🔧 Tasks - Day 1

| Task                    | Owner    | Time | Description                              |
| ----------------------- | -------- | ---- | ---------------------------------------- |
| 5.1: Heartbeat sender   | **Bình** | 2h   | Thread gửi heartbeat mỗi 5 giây          |
| 5.2: Heartbeat receiver | **Bình** | 2h   | Handler nhận heartbeat, update timestamp |
| 5.3: Failure detector   | **Bình** | 2h   | Check timeout (15 giây)                  |

### 🔧 Tasks - Day 2

| Task                       | Owner    | Time | Description                     |
| -------------------------- | -------- | ---- | ------------------------------- |
| 5.4: Update hash ring      | **Bình** | 2h   | Remove failed node khỏi ring    |
| 5.5: Redirect to replica   | **Bình** | 2h   | GET từ replica khi primary fail |
| 5.6: Test failure scenario | **Bình** | 3h   | Kill 1 node → Verify reads work |

### ✅ Success Criteria (Phase 5)

- [ ] Nodes gửi heartbeat thành công
- [ ] Kill node 1 → Hệ thống detect trong 15 giây
- [ ] GET key của node 1 → Đọc từ replica
- [ ] PUT requests redirect đến available nodes

---

## 📋 Phase 6: Data Recovery (2 ngày)

**Goal**: Node restart có thể recover data

**Note**: Phase quan trọng, cần senior handle toàn bộ

### 🔧 Tasks - Day 1

| Task                        | Owner    | Time | Description                      |
| --------------------------- | -------- | ---- | -------------------------------- |
| 6.1: GetSnapshot handler    | **Bình** | 2h   | Handler trả về all data          |
| 6.2: Snapshot serialization | **Bình** | 2h   | Efficient batch transfer         |
| 6.3: Recovery on startup    | **Bình** | 2h   | Detect restart, request snapshot |

### 🔧 Tasks - Day 2

| Task                           | Owner    | Time | Description                                |
| ------------------------------ | -------- | ---- | ------------------------------------------ |
| 6.4: Load snapshot to storage  | **Bình** | 2h   | Parse và load data vào storage             |
| 6.5: Test recovery             | **Bình** | 3h   | Stop node → Delete data → Restart → Verify |
| 6.6: Handle concurrent updates | **Bình** | 2h   | Conflict resolution (last-write-wins)      |

### ✅ Success Criteria (Phase 6)

- [ ] Stop node → Delete storage
- [ ] Restart node → Auto request snapshot
- [ ] Data recovered hoàn toàn
- [ ] Node rejoin cluster và hoạt động bình thường

---

## 📋 Phase 7: Redis Integration (Optional - 1 ngày)

**Goal**: Chuyển từ in-memory dict sang Redis persistent storage

**Note**: Phase optional, senior tự handle nếu còn thời gian

### 🔧 Tasks

| Task                        | Owner    | Time | Description                                |
| --------------------------- | -------- | ---- | ------------------------------------------ |
| 7.1: Redis connection       | **Bình** | 1h   | Setup Redis connection pool                |
| 7.2: Update StorageEngine   | **Bình** | 2h   | Replace dict operations với Redis commands |
| 7.3: Config Redis instances | **Bình** | 1h   | Start 3 Redis instances                    |
| 7.4: Test persistence       | **Bình** | 2h   | Restart node → Data vẫn còn                |

### ✅ Success Criteria (Phase 7)

- [ ] Data lưu trong Redis thay vì dict
- [ ] Restart node → Data persist (không mất)
- [ ] Performance tốt (Redis in-memory)

---

## 🧪 Testing Checklist

Sau mỗi phase, **Bình** phải test đầy đủ:

### Phase 2 Test:

```bash
# Terminal 1
python src/server.py 8001

# Terminal 2
python src/client.py
# Expected: PUT/GET/DELETE thành công
```

### Phase 3 Test:

```bash
# Start 3 nodes
python src/server.py 8001 &
python src/server.py 8002 &
python src/server.py 8003 &

# Test client connect random node
python src/client.py --node-port 8002
# Expected: Data routing đúng
```

### Phase 4 Test:

```bash
# PUT data
# Check trên 2 nodes có data
# Expected: 2 copies tồn tại
```

### Phase 5 Test:

```bash
# Start 3 nodes
# Kill node 1 (Ctrl+C)
# GET data của node 1
# Expected: Read từ replica thành công
```

### Phase 6 Test:

```bash
# Stop node 2
# Delete node 2 data
# Restart node 2
# Check data
# Expected: Data recovered
```

---

## 📊 Timeline Summary

| Phase     | Duration    | Linh Tasks | Bình Tasks | Total   |
| --------- | ----------- | ---------- | ---------- | ------- |
| Phase 1   | 1 day       | 2.5h       | 0.5h       | 3h      |
| Phase 2   | 2 days      | 7h         | 4h         | 11h     |
| Phase 3   | 3 days      | 8h         | 10h        | 18h     |
| Phase 4   | 2 days      | 6h         | 7h         | 13h     |
| Phase 5   | 2 days      | 0h         | 13h        | 13h     |
| Phase 6   | 2 days      | 0h         | 13h        | 13h     |
| Phase 7   | 1 day (opt) | 0h         | 6h         | 6h      |
| **Total** | **13 days** | **23.5h**  | **53.5h**  | **77h** |

### 📌 Phân Tích Distribution:

**Linh (Junior - 23.5h):**

- Phase 1-4: Setup, basic features, foundation work
- Focus: Learning gRPC, implementing basic storage, testing

**Bình (Senior - 53.5h):**

- Phase 1-4: Integration, advanced features, testing
- Phase 5-7: **100% ownership** - Critical features (failure detection, recovery, Redis)
- Rationale: Phases cuối phức tạp, cần senior experience

---

## 🚀 Quick Start

### 1. Setup Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate gRPC Code

```bash
python generate_grpc.py
```

### 3. Start Server (Phase 2+)

```bash
python src/server.py 8001
```

### 4. Run Client Test

```bash
python src/client.py
```

---

## 📝 Notes

- **Code review**: Bình review code của Linh trước khi integrate
- **Testing**: Không skip testing, phase nào chưa pass không sang phase khác
- **Documentation**: Update README nếu có thay đổi lớn
- **Git workflow**: Mỗi phase tạo 1 branch riêng, merge sau khi test pass

---

## 🎯 Success Metrics

Project hoàn thành khi:

- ✅ All phases test pass
- ✅ 3 nodes hoạt động đồng thời
- ✅ Failure tolerance hoạt động
- ✅ Data recovery hoạt động
- ✅ Code clean, có comments
- ✅ README đầy đủ hướng dẫn

**Good luck team! 🚀**
