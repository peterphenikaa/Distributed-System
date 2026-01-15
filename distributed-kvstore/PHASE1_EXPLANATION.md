# 📚 GIẢI THÍCH CHI TIẾT PHASE 1

## 🎯 Mục Tiêu Phase 1

Setup toàn bộ infrastructure và chuẩn bị cho việc coding. Đây là nền tảng để build các phases tiếp theo.

---

## 📦 1. POM.XML - Maven Configuration

### Là Gì?

`pom.xml` (Project Object Model) là file cấu hình chính của Maven project. Nó định nghĩa:

- Metadata của project (group, artifact, version)
- Dependencies (thư viện cần dùng)
- Build plugins (công cụ build project)

### Dependencies Quan Trọng

#### **gRPC Dependencies**

```xml
<dependency>
    <groupId>io.grpc</groupId>
    <artifactId>grpc-netty-shaded</artifactId>
</dependency>
```

**Tại sao?**

- gRPC là framework để các services giao tiếp với nhau qua network
- Netty: High-performance networking library
- "shaded": Đóng gói dependencies để tránh conflicts

#### **Protocol Buffers**

```xml
<dependency>
    <groupId>com.google.protobuf</groupId>
    <artifactId>protobuf-java</artifactId>
</dependency>
```

**Tại sao?**

- Protobuf là format để serialize data (chuyển đổi objects thành bytes)
- Nhỏ gọn hơn JSON, nhanh hơn JSON
- Strongly typed (có kiểu dữ liệu rõ ràng)

#### **Jedis - Redis Client**

```xml
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
</dependency>
```

**Tại sao?**

- Jedis là Java client để connect và interact với Redis
- Thread-safe với connection pooling
- Simple API giống Redis commands

#### **Logging (SLF4J + Logback)**

```xml
<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-api</artifactId>
</dependency>
<dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-classic</artifactId>
</dependency>
```

**Tại sao?**

- SLF4J: Interface cho logging (không phụ thuộc implementation cụ thể)
- Logback: Implementation thực tế, nhanh và flexible
- Giúp debug, monitor hệ thống

### Build Plugins

#### **Protobuf Maven Plugin**

```xml
<plugin>
    <artifactId>protobuf-maven-plugin</artifactId>
</plugin>
```

**Chức năng:**

- Đọc file `.proto`
- Generate Java code tự động
- Tạo classes: Request/Response messages, Service interfaces

**Ví dụ:**

```proto
message PutRequest {
  string key = 1;
  string value = 2;
}
```

→ Generate class `PutRequest.java` với methods: `getKey()`, `getValue()`, `newBuilder()`, etc.

#### **Maven Shade Plugin**

```xml
<plugin>
    <artifactId>maven-shade-plugin</artifactId>
</plugin>
```

**Chức năng:**

- Tạo "fat JAR" (uber JAR)
- Đóng gói tất cả dependencies vào 1 file JAR
- Có thể chạy trực tiếp: `java -jar kvstore.jar`

---

## 📋 2. PROTO FILE - gRPC Definitions

### File: `kvstore.proto`

### Cấu Trúc

#### **Services**

Định nghĩa các RPC methods (Remote Procedure Calls)

```proto
service KeyValueStore {
  rpc Put(PutRequest) returns (PutResponse);
  rpc Get(GetRequest) returns (GetResponse);
}
```

**Giải thích:**

- `service KeyValueStore`: Tên service
- `rpc Put`: Method name
- `PutRequest`: Input parameter type
- `PutResponse`: Return type

**Tương đương Java interface:**

```java
interface KeyValueStore {
    PutResponse put(PutRequest request);
    GetResponse get(GetRequest request);
}
```

#### **Messages**

Định nghĩa data structures

```proto
message PutRequest {
  string key = 1;      // Field name và field number
  string value = 2;
  int64 timestamp = 3;
}
```

**Giải thích:**

- `message PutRequest`: Tên class
- `string key = 1`: Field type, name, và number
- Field numbers (1, 2, 3): Dùng để serialize, KHÔNG BAO GIỜ thay đổi

**Tương đương Java class:**

```java
class PutRequest {
    private String key;
    private String value;
    private long timestamp;
    // + getters, setters, builder
}
```

#### **Enums**

Định nghĩa constants

```proto
enum NodeStatus {
  ACTIVE = 0;
  SUSPECTED = 1;
  FAILED = 2;
}
```

### Tại Sao Dùng Protobuf?

**So sánh với JSON:**

**JSON:**

```json
{ "key": "user:1", "value": "John", "timestamp": 1234567890 }
```

Size: ~60 bytes (text)

**Protobuf:**

```
Binary: [0a 06 75 73 65 72 3a 31 12 04 4a 6f 68 6e 18 d2 85 d8 f4 04]
```

Size: ~20 bytes (binary)

**Lợi ích:**

- ✅ Nhỏ hơn 2-3 lần
- ✅ Parse nhanh hơn 5-10 lần
- ✅ Strongly typed
- ✅ Backward/forward compatibility

---

## ⚙️ 3. CONFIGURATION FILES

### A. cluster.json

**Mục đích:** Cấu hình toàn bộ cluster

```json
{
  "nodes": [
    {
      "id": "node1",
      "host": "localhost",
      "port": 8001,
      "redis_port": 6379
    }
  ],
  "replication_factor": 2
}
```

**Giải thích:**

- `nodes`: Danh sách tất cả nodes trong cluster
- `id`: Unique identifier cho mỗi node
- `port`: gRPC server port (cho client connections)
- `redis_port`: Redis instance port
- `replication_factor`: Số copies của mỗi key (2 = primary + 1 replica)

**Cách dùng:**

```java
// Trong code:
ClusterConfig config = loadConfig("config/cluster.json");
List<NodeInfo> nodes = config.getNodes();
// → Biết được tất cả nodes trong cluster
```

### B. redis-\*.conf

**Mục đích:** Cấu hình Redis instances

**Các settings quan trọng:**

#### **Port**

```conf
port 6379
```

Redis sẽ listen trên port này

#### **Persistence - RDB**

```conf
save 900 1      # Sau 15 phút nếu có ≥1 key thay đổi
save 300 10     # Sau 5 phút nếu có ≥10 keys thay đổi
save 60 10000   # Sau 1 phút nếu có ≥10000 keys thay đổi
```

**Giải thích:**

- Redis lưu snapshot vào disk theo các điều kiện trên
- File: `dump.rdb`
- Trade-off: Frequent saves = safer nhưng slower

#### **Persistence - AOF (Append Only File)**

```conf
appendonly yes
appendfsync everysec
```

**Giải thích:**

- AOF: Log mọi write operations
- `everysec`: Sync to disk mỗi giây
- Safer than RDB (ít mất data hơn)
- File: `appendonly.aof`

**RDB vs AOF:**

- RDB: Snapshot, compact, nhanh restore, có thể mất data
- AOF: Log, an toàn hơn, chậm restore, file lớn hơn
- **Best practice**: Dùng cả hai

#### **Memory Management**

```conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

**Giải thích:**

- Giới hạn memory Redis được dùng
- `allkeys-lru`: Khi full, xóa keys ít dùng nhất (Least Recently Used)
- Prevent OOM (Out Of Memory)

---

## 📝 4. LOGGING CONFIGURATION

### File: `logback.xml`

**Mục đích:** Cấu hình logging cho application

### Appenders

#### **Console Appender**

```xml
<appender name="CONSOLE">
    <encoder>
        <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
    </encoder>
</appender>
```

**Output example:**

```
14:23:45.123 [main] INFO  c.d.kvstore.server.Node - Node started on port 8001
14:23:45.456 [grpc-1] DEBUG c.d.kvstore.server.KVStore - PUT key=user:1 value=John
```

**Pattern giải thích:**

- `%d{HH:mm:ss.SSS}`: Timestamp với milliseconds
- `[%thread]`: Thread name
- `%-5level`: Log level (INFO, DEBUG, ERROR) - 5 chars wide
- `%logger{36}`: Logger name (class name) - max 36 chars
- `%msg`: Log message
- `%n`: Newline

#### **File Appender**

```xml
<appender name="FILE">
    <file>logs/kvstore.log</file>
    <rollingPolicy>
        <fileNamePattern>logs/kvstore.%d{yyyy-MM-dd}.log</fileNamePattern>
        <maxHistory>30</maxHistory>
    </rollingPolicy>
</appender>
```

**Chức năng:**

- Ghi logs vào file `logs/kvstore.log`
- Rotate daily: Mỗi ngày tạo file mới
- Keep 30 days: Tự động xóa logs cũ hơn 30 ngày
- Prevent disk full

### Logger Levels

```xml
<logger name="com.distributed.kvstore" level="DEBUG" />
<logger name="io.grpc" level="INFO" />
```

**Levels (từ ít → nhiều):**

1. **TRACE**: Very detailed, mọi thứ
2. **DEBUG**: Debug information, development mode
3. **INFO**: Thông tin quan trọng, production mode
4. **WARN**: Cảnh báo, có vấn đề nhưng không critical
5. **ERROR**: Lỗi nghiêm trọng

**Example:**

```java
logger.debug("Processing PUT request: key={}", key);  // Only in DEBUG mode
logger.info("Node started successfully");             // Always show
logger.error("Failed to connect to Redis", exception); // Errors
```

---

## 🔧 5. SCRIPTS

### start-redis.bat/sh

**Mục đích:** Start 3 Redis instances

**Windows version (bat):**

```batch
start "Redis-6379" redis-server config\redis-6379.conf
start "Redis-6380" redis-server config\redis-6380.conf
start "Redis-6381" redis-server config\redis-6381.conf
```

**Giải thích:**

- `start "Name"`: Mở terminal mới với title
- `redis-server config.conf`: Start Redis với config file
- Chạy parallel (3 processes cùng lúc)

### start-cluster.bat

**Mục đích:** Build và start tất cả nodes

**Flow:**

1. `mvn clean package`: Build project → tạo JAR
2. Start Node 1 với args: `--node-id=node1 --port=8001`
3. Wait 3 seconds (để node khởi động)
4. Start Node 2, Node 3 tương tự

**Tại sao cần wait?**

- Nodes cần thời gian khởi động
- Connect Redis, initialize gRPC server
- Nếu start quá nhanh → có thể conflict

---

## 🏗️ 6. PROJECT STRUCTURE

### Tổ Chức Packages

```
com.distributed.kvstore/
├── server/          # Server-side components
│   ├── Node.java                  # Main entry point
│   ├── StorageEngine.java         # Redis interface
│   ├── KVStoreServiceImpl.java    # gRPC service implementation
│   └── NodeServiceImpl.java       # Inter-node communication
│
├── client/          # Client application
│   ├── KVStoreClient.java         # gRPC client
│   └── ClientCLI.java             # Command-line interface
│
├── cluster/         # Cluster management
│   ├── ConsistentHash.java        # Hash ring
│   ├── MembershipManager.java     # Node membership
│   └── FailureDetector.java       # Heartbeat & detection
│
├── replication/     # Replication logic
│   ├── ReplicationManager.java
│   └── ReplicationStrategy.java
│
├── config/          # Configuration
│   ├── NodeConfig.java
│   └── ClusterConfig.java
│
└── util/            # Utilities
    ├── HashUtil.java
    └── TimestampUtil.java
```

### Nguyên Tắc Tổ Chức

1. **Separation of Concerns**: Mỗi package có trách nhiệm riêng
2. **Package by Feature**: Group theo chức năng (server, client, cluster)
3. **Single Responsibility**: Mỗi class làm 1 việc cụ thể

---

## 🎓 KIẾN THỨC NỀN TẢNG

### 1. gRPC Flow

```
Client                    Network                    Server
  |                                                     |
  |-- PutRequest (Protobuf) -->                        |
  |          (Binary over HTTP/2)                      |
  |                                                     |-- Receive request
  |                                                     |-- Deserialize
  |                                                     |-- Process (save to Redis)
  |                                                     |-- Create response
  |                                                     |-- Serialize
  |                        <-- PutResponse (Protobuf)--|
  |-- Receive response                                 |
  |-- Deserialize                                      |
```

### 2. Redis Operations

```java
// PUT
jedis.set("user:1", "John");              // Save key-value
jedis.expire("user:1", 3600);             // Set TTL (optional)

// GET
String value = jedis.get("user:1");       // Returns "John"

// DELETE
jedis.del("user:1");                      // Remove key

// LIST
Set<String> keys = jedis.keys("user:*");  // Get all keys matching pattern
```

### 3. Maven Lifecycle

```
mvn clean          → Xóa target/ directory
    ↓
mvn compile        → Compile source code
    ↓              → Generate code từ .proto
    ↓
mvn test          → Run unit tests
    ↓
mvn package       → Create JAR file
    ↓
mvn install       → Install to local Maven repo
```

---

## ✅ CHECKLIST PHASE 1

### Setup ✅

- [x] Maven project structure
- [x] pom.xml với tất cả dependencies
- [x] .proto file với service definitions
- [x] Configuration files (cluster, redis)
- [x] Logging configuration
- [x] Utility scripts
- [x] Documentation (README, QUICKSTART)

### Next: Implementation ⏳

- [ ] Generate Java code: `mvn compile`
- [ ] Implement StorageEngine
- [ ] Implement Node main class
- [ ] Implement gRPC services
- [ ] Test basic operations

---

## 🚀 NEXT STEPS

### Immediate (Ngày 3-4 của Phase 1):

1. **Generate code:**

   ```bash
   mvn clean compile
   ```

2. **Implement StorageEngine.java:**

   - Constructor: Connect Redis
   - put(key, value): Save to Redis
   - get(key): Read from Redis
   - delete(key): Remove from Redis
   - close(): Cleanup connections

3. **Implement Node.java:**

   - Parse command-line args
   - Load configuration
   - Initialize StorageEngine
   - Start gRPC server
   - Wait for shutdown signal

4. **Implement KVStoreServiceImpl.java:**

   - Override put(), get(), delete() từ generated code
   - Call StorageEngine methods
   - Return appropriate responses

5. **Test:**

   ```bash
   # Start Redis
   redis-server config/redis-6379.conf

   # Start Node
   java -jar target/kvstore-1.0.0.jar --node-id=node1 --port=8001

   # Test với redis-cli
   redis-cli -p 6379 SET test value
   redis-cli -p 6379 GET test
   ```

---

## 💡 TIPS QUAN TRỌNG

### 1. Khi Debug

- Check logs: `logs/kvstore.log`
- Enable DEBUG level cho package của bạn
- Use `logger.debug()` nhiều để trace flow

### 2. Khi Gặp Lỗi Compile

- `mvn clean`: Clear cache
- Check proto syntax: `protoc --java_out=. kvstore.proto`
- Verify Java version: `java -version` (phải ≥ 11)

### 3. Khi Redis Connection Fail

- Check Redis running: `redis-cli PING`
- Check port correct: `netstat -an | grep 6379`
- Check firewall: Allow port 6379

### 4. Best Practices

- Commit thường xuyên với Git
- Write tests cho mỗi class
- Document code với comments
- Review code của nhau

---

**Phase 1 hoàn thành setup! Sẵn sàng cho implementation.** 🎉
