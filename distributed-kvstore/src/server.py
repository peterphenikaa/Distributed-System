# Import thư viện gRPC
import grpc
# Import concurrent.futures để xử lý multi-threading
from concurrent import futures
# Import sys để lấy command line arguments (port number)
import sys
# Import os để xử lý paths
import os

# Thêm project root vào Python path để import được module local
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import generated code từ protobuf
# kvstore_pb2: Chứa message classes (PutRequest, GetResponse, etc.)
from src.proto import kvstore_pb2
# kvstore_pb2_grpc: Chứa service classes (Servicer, Stub)
from src.proto import kvstore_pb2_grpc


# Class này kế thừa từ KeyValueStoreServicer (generated từ proto)
# Servicer là base class cho server implementation
class KeyValueStoreServicer(kvstore_pb2_grpc.KeyValueStoreServicer):
    """
    Implementation của KeyValueStore service
    Xử lý các requests từ clients: PUT, GET, DELETE, ListKeys
    """
    
    def __init__(self):
        """Constructor - khởi tạo server"""
        # TODO: Phase 2 sẽ thêm storage engine vào đây
        print("✅ KeyValueStoreServicer initialized")
    
    # Override method Put từ base class
    # request: PutRequest object (có key, value fields)
    # context: gRPC context (metadata, authentication, etc.)
    def Put(self, request, context):
        """Handler cho PUT operation"""
        # TODO: Phase 2 sẽ implement logic lưu data
        print(f"📥 Received PUT request: key={request.key}")
        
        # Trả về empty response (chỉ để test Phase 1)
        return kvstore_pb2.PutResponse()
    
    # Override method Get
    def Get(self, request, context):
        """Handler cho GET operation"""
        # TODO: Phase 2 sẽ implement logic đọc data
        print(f"📤 Received GET request: key={request.key}")
        
        # Trả về empty response
        return kvstore_pb2.GetResponse()
    
    # Override method Delete
    def Delete(self, request, context):
        """Handler cho DELETE operation"""
        # TODO: Phase 2 sẽ implement logic xóa data
        print(f"🗑️ Received DELETE request: key={request.key}")
        
        # Trả về empty response
        return kvstore_pb2.DeleteResponse()
    
    # Override method ListKeys
    def ListKeys(self, request, context):
        """Handler cho ListKeys operation - list tất cả keys"""
        # TODO: Phase 2 sẽ implement logic list keys
        print("📋 Received ListKeys request")
        
        # Trả về empty response
        return kvstore_pb2.ListKeysResponse()


def serve(port):
    """
    Hàm chính để start gRPC server
    
    Args:
        port: Port number để server listen (vd: 8001)
    """
    # Tạo gRPC server với thread pool
    # max_workers=10: Tối đa 10 threads xử lý requests đồng thời
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Đăng ký servicer vào server
    # add_KeyValueStoreServicer_to_server: Generated function từ proto
    kvstore_pb2_grpc.add_KeyValueStoreServicer_to_server(
        KeyValueStoreServicer(),  # Instance của servicer class
        server  # Server object
    )
    
    # Bind server vào address
    # [::]:port nghĩa là listen trên tất cả network interfaces
    server_address = f'[::]:{port}'
    server.add_insecure_port(server_address)
    
    # Start server
    server.start()
    print(f"🚀 Server started on port {port}")
    print(f"📡 Listening on {server_address}")
    print("Press Ctrl+C to stop")
    
    # Giữ server chạy cho đến khi Ctrl+C
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n⏹️ Server stopping...")
        server.stop(0)  # Grace period 0 giây
        print("✅ Server stopped")


# Entry point của script
if __name__ == '__main__':
    # Lấy port từ command line arguments
    # Default port = 8001 nếu không truyền vào
    if len(sys.argv) > 1:
        port = int(sys.argv[1])  # Parse string -> int
    else:
        port = 8001  # Default port
    
    print(f"🎯 Starting server on port {port}...")
    serve(port)