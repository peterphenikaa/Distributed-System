"""
Simple gRPC Client để test server
"""
import grpc
import sys
import os

# Thêm project root vào Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.proto import kvstore_pb2
from src.proto import kvstore_pb2_grpc


class KVStoreClient:
    """Client để connect đến server và gọi RPC methods"""
    
    def __init__(self, host='localhost', port=8001):
        """
        Khởi tạo connection đến server
        
        Args:
            host: Server hostname (default: localhost)
            port: Server port (default: 8001)
        """
        # Tạo channel (connection) đến server
        self.address = f'{host}:{port}'
        self.channel = grpc.insecure_channel(self.address)
        
        # Tạo stub (đại diện cho remote service)
        self.stub = kvstore_pb2_grpc.KeyValueStoreStub(self.channel)
        
        print(f"✅ Connected to server at {self.address}")
    
    def put(self, key, value):
        """Gửi PUT request đến server"""
        print(f"📤 Sending PUT: {key} = {value}")
        request = kvstore_pb2.PutRequest(key=key, value=value)
        response = self.stub.Put(request)
        print(f"✅ PUT successful")
        return response
    
    def get(self, key):
        """Gửi GET request đến server"""
        print(f"📥 Sending GET: {key}")
        request = kvstore_pb2.GetRequest(key=key)
        response = self.stub.Get(request)
        print(f"✅ GET successful")
        return response
    
    def delete(self, key):
        """Gửi DELETE request đến server"""
        print(f"🗑️ Sending DELETE: {key}")
        request = kvstore_pb2.DeleteRequest(key=key)
        response = self.stub.Delete(request)
        print(f"✅ DELETE successful")
        return response
    
    def list_keys(self):
        """Gửi ListKeys request đến server"""
        print(f"📋 Sending ListKeys")
        request = kvstore_pb2.ListKeysRequest()
        response = self.stub.ListKeys(request)
        print(f"✅ ListKeys successful")
        return response
    
    def close(self):
        """Đóng connection"""
        self.channel.close()
        print("🔌 Connection closed")


# Test script khi chạy file này trực tiếp
if __name__ == '__main__':
    # Tạo client instance
    client = KVStoreClient()
    
    print("\n🧪 Testing basic operations...\n")
    
    # Test PUT
    client.put("user:1", "Alice")
    
    # Test GET
    client.get("user:1")
    
    # Test DELETE
    client.delete("user:1")
    
    # Test ListKeys
    client.list_keys()
    
    # Close connection
    client.close()
    
    print("\n✅ All tests completed!")
