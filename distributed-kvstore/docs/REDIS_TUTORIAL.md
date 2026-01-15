# 🔴 Redis Tutorial - Hướng Dẫn Chi Tiết

## 📚 Redis Là Gì?

**Redis** = **RE**mote **DI**ctionary **S**erver

- In-memory data store (lưu trữ trong RAM)
- Key-value database
- Nhanh (microsecond latency)
- Hỗ trợ nhiều data structures
- Có persistence (lưu xuống disk)

---

## 🚀 Cài Đặt Redis

### Windows

**Option 1: Windows Subsystem for Linux (WSL)**

```bash
# Install WSL
wsl --install

# Trong WSL:
sudo apt update
sudo apt install redis-server
redis-server --version
```

**Option 2: Download Binary**

- Tải từ: https://github.com/microsoftarchive/redis/releases
- Extract và chạy `redis-server.exe`

**Option 3: Docker**

```bash
docker run -d -p 6379:6379 redis:7
```

### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# CentOS/RHEL
sudo yum install redis
```

### Mac

```bash
brew install redis
brew services start redis
```

---

## 🎯 Redis Basics

### 1. Start Redis Server

```bash
# Default port 6379
redis-server

# With config file
redis-server /path/to/redis.conf

# Specific port
redis-server --port 6380
```

### 2. Connect với redis-cli

```bash
# Connect to default (localhost:6379)
redis-cli

# Connect to specific host/port
redis-cli -h localhost -p 6380

# Test connection
redis-cli PING
# Output: PONG
```

---

## 💾 Redis Data Types & Commands

### 1. Strings (Key-Value)

**SET - Lưu value:**

```bash
SET key value
SET name "John"
SET age 30
SET user:1:email "john@example.com"

# With expiration (TTL - Time To Live)
SET session:abc123 "user_data" EX 3600  # Expire sau 3600 giây (1 giờ)
SETEX session:xyz789 1800 "user_data"   # Tương tự
```

**GET - Lấy value:**

```bash
GET name
# Output: "John"

GET nonexistent
# Output: (nil)
```

**MSET/MGET - Multiple keys:**

```bash
# Set nhiều keys cùng lúc
MSET key1 "value1" key2 "value2" key3 "value3"

# Get nhiều keys cùng lúc
MGET key1 key2 key3
# Output:
# 1) "value1"
# 2) "value2"
# 3) "value3"
```

**INCR/DECR - Tăng/giảm số:**

```bash
SET counter 0
INCR counter      # counter = 1
INCR counter      # counter = 2
INCRBY counter 5  # counter = 7
DECR counter      # counter = 6
```

### 2. Keys Management

**EXISTS - Check key tồn tại:**

```bash
EXISTS name
# Output: 1 (exists) hoặc 0 (not exists)
```

**DEL - Xóa key:**

```bash
DEL name
DEL key1 key2 key3  # Xóa nhiều keys
```

**KEYS - Tìm keys theo pattern:**

```bash
KEYS *              # All keys
KEYS user:*         # Keys bắt đầu với "user:"
KEYS *:email        # Keys kết thúc với ":email"
KEYS user:?:email   # user:1:email, user:2:email, etc.

# ⚠️ WARNING: KEYS * trên production = CHẬM!
# Dùng SCAN thay thế cho production
```

**SCAN - Iterate keys (safe for production):**

```bash
SCAN 0 MATCH user:* COUNT 100
# Returns: cursor và list of keys
```

**EXPIRE - Set TTL:**

```bash
SET temp_data "some_value"
EXPIRE temp_data 300    # Expire sau 300 giây
TTL temp_data          # Check còn bao nhiêu giây
# Output: 295, 294, ... , 0, -2 (expired)

PERSIST temp_data      # Remove expiration
```

**RENAME - Đổi tên key:**

```bash
SET old_name "value"
RENAME old_name new_name
GET new_name
# Output: "value"
```

**TYPE - Check data type:**

```bash
TYPE name
# Output: string
```

### 3. Hashes (Objects)

**Lưu objects với fields:**

```bash
# HSET - Set field
HSET user:1 name "John"
HSET user:1 age 30
HSET user:1 email "john@example.com"

# HMSET - Set multiple fields
HMSET user:2 name "Alice" age 25 email "alice@example.com"

# HGET - Get field
HGET user:1 name
# Output: "John"

# HGETALL - Get all fields
HGETALL user:1
# Output:
# 1) "name"
# 2) "John"
# 3) "age"
# 4) "30"
# 5) "email"
# 6) "john@example.com"

# HDEL - Delete field
HDEL user:1 email

# HEXISTS - Check field exists
HEXISTS user:1 name
# Output: 1

# HINCRBY - Increment field
HINCRBY user:1 age 1  # Tăng age lên 1
```

### 4. Lists

**Push/Pop operations:**

```bash
# LPUSH - Push to left (head)
LPUSH mylist "item1"
LPUSH mylist "item2"
LPUSH mylist "item3"
# List: ["item3", "item2", "item1"]

# RPUSH - Push to right (tail)
RPUSH mylist "item4"
# List: ["item3", "item2", "item1", "item4"]

# LPOP - Pop from left
LPOP mylist
# Output: "item3"

# RPOP - Pop from right
RPOP mylist
# Output: "item4"

# LRANGE - Get range
LRANGE mylist 0 -1  # Get all
# Output:
# 1) "item2"
# 2) "item1"

# LLEN - Get length
LLEN mylist
# Output: 2
```

### 5. Sets

**Unordered collection (unique items):**

```bash
# SADD - Add members
SADD myset "apple"
SADD myset "banana"
SADD myset "apple"  # Duplicate ignored

# SMEMBERS - Get all members
SMEMBERS myset
# Output:
# 1) "apple"
# 2) "banana"

# SISMEMBER - Check membership
SISMEMBER myset "apple"
# Output: 1 (yes)

# SREM - Remove member
SREM myset "banana"

# SCARD - Count members
SCARD myset
# Output: 1

# Set operations
SADD set1 "a" "b" "c"
SADD set2 "b" "c" "d"

SINTER set1 set2     # Intersection: ["b", "c"]
SUNION set1 set2     # Union: ["a", "b", "c", "d"]
SDIFF set1 set2      # Difference: ["a"]
```

### 6. Sorted Sets (ZSETs)

**Sorted by score:**

```bash
# ZADD - Add with score
ZADD leaderboard 100 "player1"
ZADD leaderboard 250 "player2"
ZADD leaderboard 150 "player3"

# ZRANGE - Get by rank (ascending)
ZRANGE leaderboard 0 -1 WITHSCORES
# Output:
# 1) "player1"
# 2) "100"
# 3) "player3"
# 4) "150"
# 5) "player2"
# 6) "250"

# ZREVRANGE - Get by rank (descending)
ZREVRANGE leaderboard 0 2 WITHSCORES
# Top 3 players

# ZSCORE - Get score
ZSCORE leaderboard "player2"
# Output: "250"

# ZINCRBY - Increase score
ZINCRBY leaderboard 50 "player1"  # player1 score = 150
```

---

## 🔧 Redis với Java (Jedis)

### 1. Add Dependency

```xml
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
    <version>5.1.0</version>
</dependency>
```

### 2. Basic Usage

```java
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

public class RedisExample {
    public static void main(String[] args) {
        // Option 1: Simple connection (not recommended for production)
        Jedis jedis = new Jedis("localhost", 6379);

        // SET
        jedis.set("name", "John");

        // GET
        String name = jedis.get("name");
        System.out.println(name);  // Output: John

        // DELETE
        jedis.del("name");

        jedis.close();
    }
}
```

### 3. Connection Pooling (Recommended)

```java
public class RedisConnection {
    private static JedisPool jedisPool;

    static {
        // Pool configuration
        JedisPoolConfig config = new JedisPoolConfig();
        config.setMaxTotal(10);              // Max connections
        config.setMaxIdle(5);                // Max idle connections
        config.setMinIdle(2);                // Min idle connections
        config.setTestOnBorrow(true);        // Test connection

        // Create pool
        jedisPool = new JedisPool(config, "localhost", 6379);
    }

    public static Jedis getConnection() {
        return jedisPool.getResource();
    }

    public static void close() {
        if (jedisPool != null) {
            jedisPool.close();
        }
    }
}
```

### 4. Storage Engine Example (For Our Project)

```java
public class StorageEngine {
    private JedisPool jedisPool;

    public StorageEngine(String host, int port) {
        JedisPoolConfig config = new JedisPoolConfig();
        config.setMaxTotal(10);
        this.jedisPool = new JedisPool(config, host, port);
    }

    // PUT operation
    public void put(String key, String value, long timestamp) {
        try (Jedis jedis = jedisPool.getResource()) {
            // Store value
            jedis.set(key, value);

            // Store timestamp (optional, for conflict resolution)
            jedis.hset("timestamps", key, String.valueOf(timestamp));
        }
    }

    // GET operation
    public String get(String key) {
        try (Jedis jedis = jedisPool.getResource()) {
            return jedis.get(key);
        }
    }

    // DELETE operation
    public boolean delete(String key) {
        try (Jedis jedis = jedisPool.getResource()) {
            Long deleted = jedis.del(key);
            jedis.hdel("timestamps", key);
            return deleted > 0;
        }
    }

    // LIST keys
    public Set<String> listKeys(String pattern) {
        try (Jedis jedis = jedisPool.getResource()) {
            return jedis.keys(pattern);
        }
    }

    // Get timestamp
    public long getTimestamp(String key) {
        try (Jedis jedis = jedisPool.getResource()) {
            String ts = jedis.hget("timestamps", key);
            return ts != null ? Long.parseLong(ts) : 0;
        }
    }

    // Cleanup
    public void close() {
        if (jedisPool != null) {
            jedisPool.close();
        }
    }
}
```

### 5. Error Handling

```java
try (Jedis jedis = jedisPool.getResource()) {
    jedis.set("key", "value");
} catch (JedisConnectionException e) {
    // Connection error
    logger.error("Failed to connect to Redis", e);
} catch (JedisDataException e) {
    // Data error (wrong type, etc.)
    logger.error("Redis data error", e);
} catch (Exception e) {
    // Other errors
    logger.error("Unexpected error", e);
}
```

---

## 💾 Persistence

### 1. RDB (Redis Database)

**Snapshot-based persistence:**

```conf
# Save conditions in redis.conf
save 900 1      # After 900s if ≥1 key changed
save 300 10     # After 300s if ≥10 keys changed
save 60 10000   # After 60s if ≥10000 keys changed

# Manual save
SAVE       # Blocking (chờ save xong)
BGSAVE     # Background (không block)

# Files
dbfilename dump.rdb
dir /var/lib/redis/
```

**Pros:**

- Compact single-file
- Faster restart
- Good for backups

**Cons:**

- Can lose data (last few minutes)
- CPU intensive when saving

### 2. AOF (Append Only File)

**Log-based persistence:**

```conf
# Enable AOF
appendonly yes
appendfilename "appendonly.aof"

# Sync strategy
appendfsync always    # Sync after every write (slowest, safest)
appendfsync everysec  # Sync every second (good balance) ✅ RECOMMENDED
appendfsync no        # Let OS decide (fastest, least safe)

# Rewrite AOF when too large
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

**Pros:**

- More durable (less data loss)
- Log file can be replayed
- Automatic rewrite

**Cons:**

- Larger files
- Slower than RDB

**Best Practice:** Dùng cả RDB + AOF ✅

---

## 🔐 Security

### 1. Authentication

```conf
# Set password in redis.conf
requirepass your_strong_password
```

```bash
# Connect với password
redis-cli -a your_strong_password

# Hoặc trong redis-cli:
AUTH your_strong_password
```

```java
// Jedis with password
JedisPool pool = new JedisPool(config, "localhost", 6379, 2000, "your_strong_password");
```

### 2. Network Security

```conf
# Bind to specific IP (redis.conf)
bind 127.0.0.1  # Only localhost
bind 0.0.0.0    # All interfaces (DANGEROUS!)

# Protected mode
protected-mode yes
```

---

## 📊 Monitoring & Debugging

### 1. INFO Command

```bash
INFO              # All info
INFO server       # Server info
INFO clients      # Client connections
INFO memory       # Memory usage
INFO stats        # Statistics
INFO replication  # Replication info
```

### 2. MONITOR Command

```bash
MONITOR
# Real-time stream of all commands
# ⚠️ Don't use in production (performance impact)
```

### 3. SLOWLOG

```bash
# Get slow queries
SLOWLOG GET 10    # Get last 10 slow queries

# Configure threshold
CONFIG SET slowlog-log-slower-than 10000  # 10ms
```

### 4. Memory Analysis

```bash
# Memory usage
INFO memory

# Memory usage per key
MEMORY USAGE key_name

# Analyze all keys
redis-cli --bigkeys
```

---

## ⚡ Performance Tips

### 1. Use Pipelining

**Without pipelining:**

```java
for (int i = 0; i < 1000; i++) {
    jedis.set("key" + i, "value" + i);  // 1000 round trips!
}
```

**With pipelining:**

```java
Pipeline pipeline = jedis.pipelined();
for (int i = 0; i < 1000; i++) {
    pipeline.set("key" + i, "value" + i);
}
pipeline.sync();  // 1 round trip!
```

### 2. Avoid KEYS Command

```bash
# BAD (blocks Redis):
KEYS *

# GOOD:
SCAN 0 MATCH pattern COUNT 100
```

### 3. Use Appropriate Data Structures

**Bad:**

```java
// Storing JSON as string, parsing every time
jedis.set("user:1", "{\"name\":\"John\",\"age\":30}");
String json = jedis.get("user:1");
User user = parseJson(json);  // Slow!
```

**Good:**

```java
// Use hash
jedis.hset("user:1", "name", "John");
jedis.hset("user:1", "age", "30");
String name = jedis.hget("user:1", "name");  // Fast!
```

### 4. Connection Pooling

Always use JedisPool, never create new Jedis() repeatedly!

---

## 🧪 Testing Tips

### 1. Test Connection

```bash
redis-cli PING
# Output: PONG → Redis is running
```

### 2. Monitor Commands

```bash
redis-cli MONITOR
# Then run your app and see all Redis commands
```

### 3. Clear Test Data

```bash
# Delete specific keys
DEL test:*

# Clear ALL data (⚠️ DANGEROUS)
FLUSHDB   # Current database
FLUSHALL  # All databases
```

---

## 🎯 Use Cases trong Project

### 1. Store Key-Value

```java
// Client request: PUT user:1 John
storageEngine.put("user:1", "John", System.currentTimeMillis());

// Redis:
// Key: user:1 → Value: John
// Hash: timestamps → user:1 → 1234567890
```

### 2. Check Existence

```java
String value = storageEngine.get("user:1");
if (value != null) {
    // Key exists
} else {
    // Key not found
}
```

### 3. List All Keys on Node

```java
Set<String> keys = storageEngine.listKeys("*");
// Returns all keys stored on this node
```

### 4. Conflict Resolution (Last-Write-Wins)

```java
public void putWithConflictResolution(String key, String value, long timestamp) {
    long existingTs = getTimestamp(key);

    if (timestamp >= existingTs) {
        // This write is newer
        put(key, value, timestamp);
    } else {
        // This write is older, ignore
        logger.info("Ignoring old write for key: {}", key);
    }
}
```

---

## 📚 Cheat Sheet

### Common Commands

```bash
# Connection
redis-cli
redis-cli -h host -p port -a password

# Basic
PING
SET key value
GET key
DEL key
EXISTS key
KEYS pattern

# Expiration
EXPIRE key seconds
TTL key
PERSIST key

# Info
INFO
DBSIZE
CONFIG GET *
```

### Jedis Basics

```java
// Connection
Jedis jedis = new Jedis("host", port);
JedisPool pool = new JedisPool(config, "host", port);

// Operations
jedis.set(key, value);
jedis.get(key);
jedis.del(key);
jedis.exists(key);

// Cleanup
jedis.close();
pool.close();
```

---

## 🔗 Resources

- [Redis Documentation](https://redis.io/docs/)
- [Redis Commands Reference](https://redis.io/commands/)
- [Jedis GitHub](https://github.com/redis/jedis)
- [Redis University](https://university.redis.com/)
- [Try Redis Online](https://try.redis.io/)

---

**Redis là tool mạnh mẽ cho distributed systems! Hãy master nó! 🚀**
