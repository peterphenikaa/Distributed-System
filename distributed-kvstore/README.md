# Hệ Thống Phân Tán Key-Value Store

## 📋 Mục Lục

- [Tổng Quan](#tổng-quan)
- [Kiến Trúc Hệ Thống](#kiến-trúc-hệ-thống)
- [Công Nghệ Sử Dụng](#công-nghệ-sử-dụng)
- [Cấu Trúc Project](#cấu-trúc-project)
- [Kế Hoạch Phát Triển](#kế-hoạch-phát-triển)
- [Hướng Dẫn Cài Đặt](#hướng-dẫn-cài-đặt)
- [Hướng Dẫn Chạy](#hướng-dẫn-chạy)
- [Testing](#testing)
- [Tài Liệu Kỹ Thuật](#tài-liệu-kỹ-thuật)

---

## 🎯 Tổng Quan

Dự án xây dựng hệ thống lưu trữ key-value phân tán, hoạt động trên nhiều nodes. Mỗi node lưu trữ một phần dữ liệu và phối hợp với các nodes khác để đảm bảo tính nhất quán và khả năng chịu lỗi.

### Tính Năng Chính

- ✅ **Phân tán dữ liệu** sử dụng Consistent Hashing
- ✅ **Replication** với replication factor = 2 (mỗi key có 2 copies)
- ✅ **Failure Detection** qua heartbeat mechanism
- ✅ **Data Recovery** khi node restart
- ✅ **Request Forwarding** tự động đến node đúng
- ✅ **Redis** làm storage backend (persistent + high performance)

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────┐
│                        CLIENTS                          │
│              (PUT/GET/DELETE operations)                │
└─────────────────────────────────────────────────────────┘
                          │
              gRPC over TCP/IP (Protobuf)
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    ┌───▼───┐         ┌───▼───┐         ┌───▼───┐
    │ Node1 │◄────────►Node2 │◄────────►Node3 │
    │Port   │  gRPC   │Port   │  gRPC   │Port   │
    │ 8001  │ P2P     │ 8002  │ P2P     │ 8003  │
    └───┬───┘         └───┬───┘         └───┬───┘
        │                 │                 │
        │                 │                 │
    ┌───▼───┐         ┌───▼───┐         ┌───▼───┐
    │Redis 1│         │Redis 2│         │Redis 3│
    │ 6379  │         │ 6380  │         │ 6381  │
    └───────┘         └───────┘         └───────┘
```

### Các Thành Phần

#### 1. **Node (Storage Node)**

- **Chức năng**:
  - Lưu trữ dữ liệu trong Redis
  - Xử lý client requests (PUT/GET/DELETE)
  - Giao tiếp với nodes khác (replication, forwarding)
  - Tham gia failure detection (heartbeat)
- **Thành phần con**:
  - `StorageEngine`: Interface với Redis
  - `KVStoreService`: gRPC service cho clients
  - `NodeService`: gRPC service cho inter-node communication
  - `ConsistentHash`: Xác định key thuộc node nào
  - `MembershipManager`: Quản lý danh sách nodes
  - `FailureDetector`: Phát hiện node failure
  - `ReplicationManager`: Quản lý replication

#### 2. **Client**

- Console application
- Connect đến bất kỳ node nào
- Thực hiện PUT/GET/DELETE operations
- Retry logic khi node failure

#### 3. **Redis**

- Mỗi node có Redis instance riêng
- Lưu trữ persistent data
- High performance (in-memory with disk persistence)

---

## 🛠️ Công Nghệ Sử Dụng

| Công nghệ            | Phiên bản | Mục đích                        |
| -------------------- | --------- | ------------------------------- |
| **Java**             | 11+       | Ngôn ngữ lập trình chính        |
| **gRPC**             | 1.60.0    | RPC framework cho communication |
| **Protocol Buffers** | 3.25.1    | Serialization format            |
| **Redis**            | 7.x       | Storage backend                 |
| **Jedis**            | 5.1.0     | Java client cho Redis           |
| **Maven**            | 3.8+      | Build tool                      |
| **SLF4J + Logback**  | 2.0.9     | Logging framework               |
| **JUnit 5**          | 5.10.1    | Testing framework               |

### Tại Sao Chọn Các Công Nghệ Này?

**gRPC + Protobuf:**

- High performance (binary protocol)
- Strong typing với .proto definitions
- Built-in support cho streaming
- Cross-language compatibility
- HTTP/2 multiplexing

**Redis:**

- In-memory performance với disk persistence
- Atomic operations
- Simple key-value API
- Mature và reliable
- Dễ deploy và scale

---

## 📁 Cấu Trúc Project

```
distributed-kvstore/
│
├── pom.xml                          # Maven configuration
├── README.md                        # File này
├── docs/                            # Tài liệu chi tiết
│   ├── architecture.md
│   ├── protocol.md
│   └── deployment.md
│
├── config/                          # Configuration files
│   ├── node1.json
│   ├── node2.json
│   ├── node3.json
│   └── cluster.json
│
├── scripts/                         # Scripts tiện ích
│   ├── start-redis.sh              # Start Redis instances
│   ├── start-cluster.sh            # Start tất cả nodes
│   └── test-client.sh              # Run test client
│
└── src/
    ├── main/
    │   ├── java/com/distributed/kvstore/
    │   │   ├── server/
    │   │   │   ├── Node.java                    # Main entry point
    │   │   │   ├── StorageEngine.java           # Redis interface
    │   │   │   ├── KVStoreServiceImpl.java      # Client-facing gRPC service
    │   │   │   └── NodeServiceImpl.java         # Inter-node gRPC service
    │   │   │
    │   │   ├── client/
    │   │   │   ├── KVStoreClient.java           # Client application
    │   │   │   └── ClientCLI.java               # Command-line interface
    │   │   │
    │   │   ├── cluster/
    │   │   │   ├── ConsistentHash.java          # Consistent hashing algorithm
    │   │   │   ├── MembershipManager.java       # Quản lý nodes trong cluster
    │   │   │   └── FailureDetector.java         # Heartbeat & failure detection
    │   │   │
    │   │   ├── replication/
    │   │   │   ├── ReplicationManager.java      # Quản lý replication
    │   │   │   └── ReplicationStrategy.java     # Chiến lược replication
    │   │   │
    │   │   ├── config/
    │   │   │   ├── NodeConfig.java              # Node configuration
    │   │   │   └── ClusterConfig.java           # Cluster configuration
    │   │   │
    │   │   └── util/
    │   │       ├── HashUtil.java                # Hashing utilities
    │   │       └── TimestampUtil.java           # Timestamp handling
    │   │
    │   ├── proto/
    │   │   └── kvstore.proto                    # gRPC service definitions
    │   │
    │   └── resources/
    │       ├── logback.xml                      # Logging configuration
    │       └── application.properties           # Default properties
    │
    └── test/
        └── java/com/distributed/kvstore/
            ├── ConsistentHashTest.java
            ├── StorageEngineTest.java
            ├── ReplicationTest.java
            └── IntegrationTest.java
```

---

## 📅 Kế Hoạch Phát Triển

### **Phase 1: Setup & Basic Infrastructure (3-4 ngày)** ✅ ĐANG LÀM

#### Tuần 1 - Ngày 1-2:

- [x] Tạo Maven project structure
- [x] Cấu hình pom.xml với dependencies
- [x] Định nghĩa .proto files cho gRPC
- [ ] Generate Java code từ proto files
- [ ] Setup Redis (3 instances trên ports 6379, 6380, 6381)

#### Tuần 1 - Ngày 3-4:

- [ ] Implement `StorageEngine.java` - Redis client wrapper
  - Connect đến Redis
  - Implement PUT/GET/DELETE operations
  - Error handling
- [ ] Implement basic `Node.java` - main entry point
  - Parse command-line arguments
  - Initialize gRPC server
  - Connect to Redis
- [ ] Implement `KVStoreServiceImpl.java` - basic version
  - Handle PUT request → save to Redis
  - Handle GET request → read from Redis
  - Handle DELETE request → delete from Redis

**Deliverable:** 1 node chạy được, client có thể PUT/GET/DELETE

---

### **Phase 2: Distributed Architecture (4-5 ngày)**

#### Tuần 2 - Ngày 1-2:

- [ ] Implement `ConsistentHash.java`
  - Consistent hashing algorithm
  - Virtual nodes (vnodes) để balance tốt hơn
  - Xác định node nào chịu trách nhiệm key nào
- [ ] Implement `MembershipManager.java`
  - Load cluster configuration
  - Maintain list of nodes (node_id, host, port)
  - Update hash ring khi node join/leave

#### Tuần 2 - Ngày 3-4:

- [ ] Implement request forwarding
  - Trong `KVStoreServiceImpl`: Check hash ring
  - Nếu key không thuộc node này → forward đến node đúng
  - Use `ForwardPut/Get/Delete` RPC calls
- [ ] Implement `NodeServiceImpl.java` - forwarding methods
  - Handle ForwardPut/Get/Delete requests
  - Execute operation và return result

#### Tuần 2 - Ngày 5:

- [ ] Testing với 3 nodes
  - Start 3 nodes với Redis instances khác nhau
  - Client connect đến random node
  - Verify data được route đến node đúng

**Deliverable:** 3 nodes phân chia dữ liệu theo consistent hashing

---

### **Phase 3: Replication (4-5 ngày)**

#### Tuần 3 - Ngày 1-2:

- [ ] Design replication strategy
  - Replication factor = 2
  - Primary node + 1 successor node (theo hash ring)
- [ ] Implement `ReplicationManager.java`
  - Xác định replica nodes
  - Send ReplicateRequest đến replica
  - Wait for acknowledgment

#### Tuần 3 - Ngày 3-4:

- [ ] Update `KVStoreServiceImpl.java` cho replication
  - PUT operation: Save to local + replicate
  - DELETE operation: Delete local + replicate delete
- [ ] Implement `NodeServiceImpl.Replicate()`
  - Handle ReplicateRequest
  - Save/delete data trong Redis
  - Return acknowledgment

#### Tuần 3 - Ngày 5:

- [ ] Testing replication
  - PUT key → verify 2 copies tồn tại
  - Check data consistency giữa primary và replica
  - Test read từ replica

**Deliverable:** Mỗi key có 2 copies, read hoạt động với replica

---

### **Phase 4: Failure Detection & Handling (3-4 ngày)**

#### Tuần 4 - Ngày 1-2:

- [ ] Implement `FailureDetector.java`
  - Heartbeat sender: Gửi heartbeat mỗi 5 giây
  - Heartbeat receiver: Update last-seen timestamp
  - Failure detector: Check timeout (15 giây)
- [ ] Implement `NodeServiceImpl.Heartbeat()`
  - Receive heartbeat
  - Update membership table

#### Tuần 4 - Ngày 3-4:

- [ ] Handle node failure
  - Update hash ring (remove failed node)
  - Redirect requests đến replica
  - Update client connections
- [ ] Testing failure scenarios
  - Kill 1 node → verify reads still work từ replica
  - Verify writes redirect đến available nodes

**Deliverable:** Hệ thống hoạt động khi 1 node failed

---

### **Phase 5: Data Recovery (3-4 ngày)**

#### Tuần 5 - Ngày 1-2:

- [ ] Implement snapshot mechanism
  - `NodeServiceImpl.GetSnapshot()`: Return all data
  - Efficient serialization (batch transfer)
- [ ] Implement recovery protocol trong `Node.java`
  - Detect startup after failure
  - Request snapshot từ peer nodes
  - Load data vào Redis

#### Tuần 5 - Ngày 3-4:

- [ ] Anti-entropy mechanism (optional)
  - Compare checksums giữa nodes
  - Sync missing/outdated data
- [ ] Testing recovery
  - Stop node → delete Redis data
  - Restart node → verify data recovery

**Deliverable:** Node recover được data sau restart

---

### **Phase 6: Client & CLI (2-3 ngày)**

#### Tuần 6 - Ngày 1-2:

- [ ] Implement `KVStoreClient.java`
  - Connect đến multiple nodes (load balancing)
  - Retry logic
  - Timeout handling
- [ ] Implement `ClientCLI.java`
  - Interactive command-line
  - Commands: PUT, GET, DELETE, LIST
  - Pretty output

**Deliverable:** User-friendly client application

---

### **Phase 7: Testing & Documentation (4-5 ngày)**

#### Tuần 7 - Ngày 1-2:

- [ ] Unit tests
  - ConsistentHashTest
  - StorageEngineTest
  - ReplicationManagerTest
- [ ] Integration tests
  - Full cluster test
  - Failure scenarios
  - Recovery scenarios

#### Tuần 7 - Ngày 3-5:

- [ ] Viết báo cáo (8-10 trang):
  - Kiến trúc tổng thể
  - Giao thức truyền thông (gRPC + Protobuf)
  - Consistent hashing algorithm
  - Replication strategy
  - Failure detection mechanism
  - Recovery protocol
  - Limitations & future improvements
- [ ] Tạo diagrams:
  - Architecture diagram
  - Sequence diagrams (PUT/GET flow)
  - State diagrams (node lifecycle)

**Deliverable:** Complete documentation & test suite

---

### **Phase 8: Demo Preparation (2 ngày)**

- [ ] Prepare demo script
- [ ] Test scenarios:
  1. Normal operations (PUT/GET/DELETE)
  2. Node failure handling
  3. Data recovery
  4. Load distribution
- [ ] Prepare presentation slides
- [ ] Record demo video (backup)

---

## ⚙️ Hướng Dẫn Cài Đặt

### Prerequisites

1. **Java Development Kit (JDK) 11+**

   ```bash
   # Check Java version
   java -version
   javac -version
   ```

2. **Apache Maven 3.8+**

   ```bash
   # Check Maven version
   mvn -version
   ```

3. **Redis Server 7.x**

   ```bash
   # Windows: Download từ https://redis.io/download
   # hoặc dùng WSL/Docker

   # Linux/Mac:
   sudo apt-get install redis-server
   # hoặc
   brew install redis
   ```

4. **Git** (để clone project)

### Build Project

```bash
# 1. Clone repository
git clone <repository-url>
cd distributed-kvstore

# 2. Build project
mvn clean install

# Build sẽ:
# - Download tất cả dependencies
# - Generate Java code từ .proto files
# - Compile Java source
# - Run unit tests
# - Package thành executable JAR
```

### Setup Redis Instances

Tạo 3 Redis instances cho 3 nodes:

**Option 1: Dùng Redis config files**

```bash
# Tạo 3 config files
# config/redis-6379.conf
port 6379
dir ./data/redis1
dbfilename dump1.rdb

# config/redis-6380.conf
port 6380
dir ./data/redis2
dbfilename dump2.rdb

# config/redis-6381.conf
port 6381
dir ./data/redis3
dbfilename dump3.rdb

# Start Redis instances
redis-server config/redis-6379.conf
redis-server config/redis-6380.conf
redis-server config/redis-6381.conf
```

**Option 2: Dùng Docker**

```bash
# docker-compose.yml
version: '3'
services:
  redis1:
    image: redis:7
    ports:
      - "6379:6379"
  redis2:
    image: redis:7
    ports:
      - "6380:6379"
  redis3:
    image: redis:7
    ports:
      - "6381:6379"

# Start
docker-compose up -d
```

---

## 🚀 Hướng Dẫn Chạy

### Start Cluster (3 Nodes)

**Terminal 1 - Node 1:**

```bash
java -jar target/kvstore-1.0.0.jar \
  --node-id=node1 \
  --port=8001 \
  --redis-host=localhost \
  --redis-port=6379 \
  --config=config/cluster.json
```

**Terminal 2 - Node 2:**

```bash
java -jar target/kvstore-1.0.0.jar \
  --node-id=node2 \
  --port=8002 \
  --redis-host=localhost \
  --redis-port=6380 \
  --config=config/cluster.json
```

**Terminal 3 - Node 3:**

```bash
java -jar target/kvstore-1.0.0.jar \
  --node-id=node3 \
  --port=8003 \
  --redis-host=localhost \
  --redis-port=6381 \
  --config=config/cluster.json
```

### Run Client

```bash
# Interactive mode
java -cp target/kvstore-1.0.0.jar \
  com.distributed.kvstore.client.ClientCLI \
  --nodes=localhost:8001,localhost:8002,localhost:8003

# Commands trong CLI:
> PUT user:1 {"name":"John","age":30}
> GET user:1
> DELETE user:1
> LIST
> EXIT
```

### Configuration Files

**config/cluster.json:**

```json
{
  "cluster_name": "kvstore-cluster",
  "nodes": [
    {
      "id": "node1",
      "host": "localhost",
      "port": 8001
    },
    {
      "id": "node2",
      "host": "localhost",
      "port": 8002
    },
    {
      "id": "node3",
      "host": "localhost",
      "port": 8003
    }
  ],
  "replication_factor": 2,
  "heartbeat_interval_ms": 5000,
  "failure_timeout_ms": 15000
}
```

---

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
mvn test

# Run specific test
mvn test -Dtest=ConsistentHashTest
```

### Integration Test

```bash
# Start cluster và run integration tests
mvn verify
```

### Manual Testing Scenarios

**Scenario 1: Normal Operations**

```bash
# PUT 10 keys
PUT key1 value1
PUT key2 value2
...

# Verify distribution across nodes
# Check Redis instances:
redis-cli -p 6379 KEYS "*"
redis-cli -p 6380 KEYS "*"
redis-cli -p 6381 KEYS "*"
```

**Scenario 2: Node Failure**

```bash
# 1. PUT keys
PUT test_key test_value

# 2. Kill node1 (Ctrl+C trong terminal 1)

# 3. GET key từ client
GET test_key  # Should still work (từ replica)
```

**Scenario 3: Data Recovery**

```bash
# 1. Stop node1
# 2. Flush Redis: redis-cli -p 6379 FLUSHALL
# 3. Restart node1
# 4. Check data recovered: GET các keys
```

---

## 📚 Tài Liệu Kỹ Thuật

### gRPC Protocol

- **Client → Node**: `KeyValueStore` service
- **Node → Node**: `NodeService` service
- **Serialization**: Protocol Buffers (binary, efficient)
- **Transport**: HTTP/2 over TCP

### Consistent Hashing

```
Hash Ring (0 - 2^32):
                    Node1 (hash=100)
                   /
    Node3 --------●-----------● Node2
   (hash=300)                (hash=200)

Key "user:1" → hash = 150 → Node2 (first node >= 150)
Replica → Node3 (next node in ring)
```

### Replication Flow

```
Client → PUT(key, value)
   ↓
Node1 (receives request)
   ↓
1. Check hash → This node is primary? YES
2. Save to local Redis
3. Determine replica node (Node2)
4. RPC: Node2.Replicate(key, value)
5. Wait for ACK from Node2
6. Return success to client
```

### Failure Detection

```
Every 5 seconds:
Node1 → Heartbeat → Node2
Node1 → Heartbeat → Node3
Node2 → Heartbeat → Node1
Node2 → Heartbeat → Node3
...

If no heartbeat from NodeX > 15 seconds:
→ Mark NodeX as FAILED
→ Update hash ring
→ Redirect requests
```

---

## 🔧 Troubleshooting

### Issue: Cannot connect to Redis

```bash
# Check Redis is running
redis-cli -p 6379 PING
# Should return: PONG

# Check Redis logs
tail -f /var/log/redis/redis-server.log
```

### Issue: gRPC connection refused

```bash
# Check port is listening
netstat -an | grep 8001

# Check firewall
# Windows: Windows Defender Firewall
# Linux: sudo ufw status
```

### Issue: Port already in use

```bash
# Find process using port
# Windows:
netstat -ano | findstr :8001
taskkill /PID <pid> /F

# Linux:
lsof -i :8001
kill -9 <pid>
```

---

## 👥 Team Members

- Member 1: [Tên] - [Vai trò]
- Member 2: [Tên] - [Vai trò]
- Member 3: [Tên] - [Vai trò]

---

## 📖 References

- [gRPC Java Documentation](https://grpc.io/docs/languages/java/)
- [Protocol Buffers Guide](https://protobuf.dev/getting-started/javatutorial/)
- [Redis Documentation](https://redis.io/docs/)
- [Jedis GitHub](https://github.com/redis/jedis)
- [Consistent Hashing](https://en.wikipedia.org/wiki/Consistent_hashing)

---

## 📝 License

MIT License - Free for educational purposes

---

**Last Updated**: Phase 1 - January 15, 2026
