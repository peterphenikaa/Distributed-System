"""
gRPC Client cho Distributed Key-Value Store.
Test các operations: PUT, GET, DELETE, LISTKEYS
"""

import sys  # Để command line arguments
import os  # Để làm việc với đường dẫn
import grpc  # gRPC library

# Import generated gRPC code
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import kvstore_pb2  # Generated message classes
import kvstore_pb2_grpc  # Generated service stubs

# ============================================================================
# PHẦN 1: Helper Functions
# ============================================================================

def print_header(title):
    """In header với formatting."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_success(message):
    """In thông báo thành công."""
    print(f"✅ {message}")

def print_error(message):
    """In thông báo lỗi."""
    print(f"❌ {message}")

def print_info(message):
    """In thông tin."""
    print(f"ℹ️  {message}")

# ============================================================================
# PHẦN 2: Hàm Test Operations
# ============================================================================

def test_put(stub, key, value):
    """
    Test PUT operation.
    
    Args:
        stub: KeyValueStore stub
        key: Key để lưu
        value: Value tương ứng
    """
    print_header(f"Testing PUT: {key} = {value}")
    
    try:
        request = kvstore_pb2.PutRequest(
            key=key,
            value=value
        )
        response = stub.Put(request)
        
        if response.success:
            print_success(f"PUT successful")
            print_info(f"Node: {response.node_id}")
            print_info(f"Replicas: {response.replicas_count}")
        else:
            print_error(f"PUT failed: {response.message}")
            
    except grpc.RpcError as e:
        print_error(f"RPC Error: {e.code()}")
        print_error(f"Details: {e.details()}")

def test_get(stub, key):
    """
    Test GET operation.
    
    Args:
        stub: KeyValueStore stub
        key: Key để lấy
    """
    print_header(f"Testing GET: {key}")
    
    try:
        request = kvstore_pb2.GetRequest(key=key)
        response = stub.Get(request)
        
        if response.found:
            print_success(f"Key found!")
            print_info(f"Value: {response.value}")
            print_info(f"Node: {response.node_id}")
            print_info(f"Timestamp: {response.timestamp}")
        else:
            print_error(f"Key not found: {key}")
            
    except grpc.RpcError as e:
        print_error(f"RPC Error: {e.code()}")
        print_error(f"Details: {e.details()}")

def test_delete(stub, key):
    """
    Test DELETE operation.
    
    Args:
        stub: KeyValueStore stub
        key: Key để xóa
    """
    print_header(f"Testing DELETE: {key}")
    
    try:
        request = kvstore_pb2.DeleteRequest(key=key)
        response = stub.Delete(request)
        
        if response.success:
            print_success(f"DELETE successful")
            print_info(f"Replicas affected: {response.replicas_count}")
        else:
            print_error(f"DELETE failed")
            
    except grpc.RpcError as e:
        print_error(f"RPC Error: {e.code()}")
        print_error(f"Details: {e.details()}")

def test_list_keys(stub):
    """
    Test LISTKEYS operation.
    
    Args:
        stub: KeyValueStore stub
    """
    print_header("Testing LISTKEYS")
    
    try:
        request = kvstore_pb2.ListKeysRequest()
        response = stub.ListKeys(request)
        
        if response.keys:
            print_success(f"Found {len(response.keys)} keys")
            for key in response.keys:
                print_info(f"  - {key}")
        else:
            print_info(f"No keys found (empty storage)")
            
    except grpc.RpcError as e:
        print_error(f"RPC Error: {e.code()}")
        print_error(f"Details: {e.details()}")

# ============================================================================
# PHẦN 3: Interactive Mode
# ============================================================================

def interactive_mode(stub):
    """
    Interactive command line interface để test client.
    """
    print_header("Interactive Mode")
    print_info("Commands: put key value | get key | delete key | list | quit")
    
    while True:
        try:
            command = input("\n>>> ").strip().split(maxsplit=2)
            
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == "quit":
                print_info("Goodbye!")
                break
            
            elif cmd == "put":
                if len(command) < 3:
                    print_error("Usage: put <key> <value>")
                    continue
                key, value = command[1], command[2]
                test_put(stub, key, value)
            
            elif cmd == "get":
                if len(command) < 2:
                    print_error("Usage: get <key>")
                    continue
                key = command[1]
                test_get(stub, key)
            
            elif cmd == "delete":
                if len(command) < 2:
                    print_error("Usage: delete <key>")
                    continue
                key = command[1]
                test_delete(stub, key)
            
            elif cmd == "list":
                test_list_keys(stub)
            
            else:
                print_error(f"Unknown command: {cmd}")
                
        except KeyboardInterrupt:
            print_info("\nGoodbye!")
            break
        except Exception as e:
            print_error(f"Error: {str(e)}")

# ============================================================================
# PHẦN 4: Demo Mode
# ============================================================================

def demo_mode(stub):
    """
    Demo mode: chạy các test operations tự động.
    """
    print_header("Demo Mode - Automatic Tests")
    
    # Test PUT
    test_put(stub, "user:1", "Alice")
    test_put(stub, "user:2", "Bob")
    test_put(stub, "user:3", "Charlie")
    
    # Test LISTKEYS
    test_list_keys(stub)
    
    # Test GET
    test_get(stub, "user:1")
    test_get(stub, "user:2")
    test_get(stub, "notexist")
    
    # Test DELETE
    test_delete(stub, "user:2")
    
    # Test LISTKEYS again
    test_list_keys(stub)

# ============================================================================
# PHẦN 5: Main Entry Point
# ============================================================================

def main(server_address: str, mode: str = "demo"):
    """
    Main function.
    
    Args:
        server_address: Server address (host:port)
        mode: "demo" hoặc "interactive"
    """
    
    print_header("Distributed Key-Value Store Client")
    print_info(f"Connecting to server: {server_address}")
    
    try:
        # Tạo channel (connection) đến server
        channel = grpc.aio.secure_channel(server_address) if False else grpc.insecure_channel(server_address)
        
        # Nếu dùng async channel, cần thay grpc.aio.secure_channel thành grpc.insecure_channel
        # vì test đơn giản cần synchronous
        channel = grpc.insecure_channel(server_address)
        
        # Tạo stub
        stub = kvstore_pb2_grpc.KeyValueStoreStub(channel)
        
        print_success(f"Connected to {server_address}")
        
        # Chạy mode
        if mode.lower() == "interactive":
            interactive_mode(stub)
        else:
            demo_mode(stub)
        
        # Close channel
        channel.close()
        print_info("Channel closed")
        
    except grpc.RpcError as e:
        print_error(f"Connection failed: {e.code()}")
        print_error(f"Details: {e.details()}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    """
    Script entry point.
    Cách sử dụng:
        python client.py                    # localhost:8001, demo mode
        python client.py localhost:8002     # localhost:8002, demo mode
        python client.py localhost:8001 interactive  # interactive mode
    """
    
    server_address = "localhost:8001"
    mode = "demo"
    
    if len(sys.argv) > 1:
        server_address = sys.argv[1]
    
    if len(sys.argv) > 2:
        mode = sys.argv[2]
    
    main(server_address, mode)
# gRPC Client implementation
# TODO: Code here
