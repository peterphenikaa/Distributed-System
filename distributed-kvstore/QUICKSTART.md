# Quick Start Guide

## 🚀 Khởi Động Nhanh (5 phút)

### Bước 1: Kiểm Tra Prerequisites

```bash
# Java 11+
java -version

# Maven
mvn -version

# Redis
redis-server --version
```

### Bước 2: Build Project

```bash
cd distributed-kvstore
mvn clean install
```

**Kết quả:** File JAR được tạo tại `target/kvstore-1.0.0.jar`

### Bước 3: Start Redis Instances

**Windows:**

```bash
scripts\start-redis.bat
```

**Linux/Mac:**

```bash
chmod +x scripts/start-redis.sh
./scripts/start-redis.sh
```

**Verify Redis đã chạy:**

```bash
redis-cli -p 6379 PING  # Should return PONG
redis-cli -p 6380 PING
redis-cli -p 6381 PING
```

### Bước 4: Start Cluster

**Mở 3 terminals riêng:**

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

### Bước 5: Test Client

**Terminal 4:**

```bash
java -cp target/kvstore-1.0.0.jar \
  com.distributed.kvstore.client.ClientCLI \
  --nodes=localhost:8001,localhost:8002,localhost:8003
```

**Try commands:**

```
> PUT name John
> GET name
> DELETE name
> EXIT
```

---

## 📝 Phase 1 Checklist

- [x] ✅ Maven project structure
- [x] ✅ pom.xml với dependencies (gRPC, Redis, Logging)
- [x] ✅ Proto file definitions (kvstore.proto)
- [x] ✅ Configuration files (cluster.json, redis configs)
- [x] ✅ Logging configuration (logback.xml)
- [x] ✅ Scripts (start-redis, start-cluster)
- [x] ✅ README.md với kế hoạch chi tiết
- [ ] ⏳ Generate Java code từ proto (chạy `mvn compile`)
- [ ] ⏳ Implement StorageEngine.java
- [ ] ⏳ Implement basic Node.java
- [ ] ⏳ Implement KVStoreServiceImpl.java

---

## 📂 File Structure Created

```
distributed-kvstore/
├── pom.xml                          ✅ Maven config
├── README.md                        ✅ Documentation
├── QUICKSTART.md                    ✅ This file
├── .gitignore                       ✅ Git ignore rules
│
├── config/                          ✅ Configuration
│   ├── cluster.json                 ✅ Cluster config
│   ├── redis-6379.conf              ✅ Redis 1 config
│   ├── redis-6380.conf              ✅ Redis 2 config
│   └── redis-6381.conf              ✅ Redis 3 config
│
├── scripts/                         ✅ Utility scripts
│   ├── start-redis.bat              ✅ Windows script
│   ├── start-redis.sh               ✅ Linux/Mac script
│   └── start-cluster.bat            ✅ Start all nodes
│
└── src/
    ├── main/
    │   ├── java/com/distributed/kvstore/  ⏳ Java source (next)
    │   ├── proto/
    │   │   └── kvstore.proto        ✅ gRPC definitions
    │   └── resources/
    │       ├── logback.xml          ✅ Logging config
    │       └── application.properties ✅ App config
    │
    └── test/                        ⏳ Tests (later)
```

---

## 🎯 Next Steps (Phase 1 continued)

### 1. Generate Java Code từ Proto

```bash
mvn protobuf:compile
mvn protobuf:compile-custom
```

**Hoặc:**

```bash
mvn compile
```

**Kết quả:** Java classes được generate tại:

- `target/generated-sources/protobuf/java/`
- Các classes: `PutRequest`, `GetResponse`, `KeyValueStoreGrpc`, etc.

### 2. Implement StorageEngine.java

**File:** `src/main/java/com/distributed/kvstore/server/StorageEngine.java`

**Chức năng:**

- Connect đến Redis
- PUT operation
- GET operation
- DELETE operation
- LIST keys operation
- Error handling

### 3. Implement Node.java

**File:** `src/main/java/com/distributed/kvstore/server/Node.java`

**Chức năng:**

- Parse command-line arguments
- Load configuration
- Initialize StorageEngine (Redis connection)
- Start gRPC server
- Register shutdown hook

### 4. Implement KVStoreServiceImpl.java

**File:** `src/main/java/com/distributed/kvstore/server/KVStoreServiceImpl.java`

**Chức năng:**

- Implement `KeyValueStore` service từ proto
- Handle PUT requests
- Handle GET requests
- Handle DELETE requests
- Handle LIST requests

---

## 🧪 Testing Phase 1

### Test 1: Single Node Operation

```bash
# Start Redis
redis-server config/redis-6379.conf

# Start Node 1
java -jar target/kvstore-1.0.0.jar --node-id=node1 --port=8001

# Test với client
PUT key1 value1
GET key1  # Should return: value1
DELETE key1
GET key1  # Should return: NOT FOUND
```

### Test 2: Verify Redis Storage

```bash
# Trong terminal khác:
redis-cli -p 6379

# Redis commands:
> KEYS *          # List all keys
> GET key1        # Get specific key
> DEL key1        # Delete key
```

---

## 💡 Tips

### Debug gRPC

Enable verbose logging:

```java
System.setProperty("io.grpc.netty.shaded.io.grpc.netty.NettyServerTransport", "DEBUG");
```

### Debug Redis Connection

Test connection:

```bash
redis-cli -h localhost -p 6379 PING
```

Check Redis logs:

```bash
tail -f logs/redis-6379.log
```

### Build Issues

Clear Maven cache:

```bash
mvn clean
rm -rf ~/.m2/repository/com/distributed/kvstore
mvn install
```

---

## 📞 Help & Support

Nếu gặp vấn đề:

1. Check README.md - Troubleshooting section
2. Check logs: `logs/kvstore.log`
3. Check Redis logs: `logs/redis-*.log`
4. Ask team members
5. Search error message on Google/StackOverflow

---

**Phase 1 Status:** Setup Complete ✅ | Implementation In Progress ⏳
