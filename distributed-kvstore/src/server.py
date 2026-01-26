"""
gRPC Server cho Distributed Key-Value Store.
Implement KeyValueStore service và Node service.
"""

import sys  # Để lấy command line arguments
import os  # Để làm việc với đường dẫn
import logging  # Để logging
import grpc  # gRPC library
from concurrent import futures  # ThreadPoolExecutor
import time  # Để sleep

# Import generated gRPC code
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import kvstore_pb2  # Generated message classes
import kvstore_pb2_grpc  # Generated service stubs

# ============================================================================
# PHẦN 1: Setup Logging
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),  # In ra console
        logging.FileHandler('server.log')  # Lưu vào file
    ]
)

logger = logging.getLogger(__name__)


# ============================================================================
# PHẦN 2: Implement KeyValueStore Service
# ============================================================================

class KeyValueStoreServicer(kvstore_pb2_grpc.KeyValueStoreServicer):
    """
    Implement KeyValueStore gRPC service.
    Methods: Put, Get, Delete, ListKeys
    """

    def __init__(self, node_id: str, port: int):
        """
        Initialize servicer.
        
        Args:
            node_id: ID của node này (e.g., "node1")
            port: Port mà server listen (e.g., 8001)
        """
        self.node_id = node_id
        self.port = port
        logger.info(f"KeyValueStoreServicer initialized for {node_id}:{port}")

    def Put(self, request, context):
        """
        Handle PUT request từ client.
        
        Args:
            request: PutRequest message (key, value, timestamp)
            context: gRPC context (client info, timeout, ...)
        
        Returns:
            PutResponse (success, node_id, replicas_count)
        """
        logger.info(f"PUT request: key={request.key}, value={request.value}")
        
        try:
            response = kvstore_pb2.PutResponse(
                success=True,
                node_id=self.node_id,
                replicas_count=1
            )
            logger.info(f"PUT success: key={request.key}")
            return response
            
        except Exception as e:
            logger.error(f"PUT failed: {str(e)}")
            context.set_details(f"PUT failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.PutResponse(success=False)

    def Get(self, request, context):
        """
        Handle GET request từ client.
        
        Args:
            request: GetRequest message (key)
            context: gRPC context
        
        Returns:
            GetResponse (found, value, node_id, timestamp)
        """
        logger.info(f"GET request: key={request.key}")
        
        try:
            response = kvstore_pb2.GetResponse(
                found=False,
                value="",
                node_id=self.node_id,
                timestamp=int(time.time())
            )
            logger.info(f"GET: key={request.key}, found={response.found}")
            return response
            
        except Exception as e:
            logger.error(f"GET failed: {str(e)}")
            context.set_details(f"GET failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.GetResponse(found=False)

    def Delete(self, request, context):
        """
        Handle DELETE request từ client.
        
        Args:
            request: DeleteRequest message (key)
            context: gRPC context
        
        Returns:
            DeleteResponse (success, replicas_count)
        """
        logger.info(f"DELETE request: key={request.key}")
        
        try:
            response = kvstore_pb2.DeleteResponse(
                success=True,
                replicas_count=1
            )
            logger.info(f"DELETE success: key={request.key}")
            return response
            
        except Exception as e:
            logger.error(f"DELETE failed: {str(e)}")
            context.set_details(f"DELETE failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.DeleteResponse(success=False)

    def ListKeys(self, request, context):
        """
        Handle LISTKEYS request từ client.
        Trả về tất cả keys hiện tại lưu trên node này.
        
        Args:
            request: Empty message
            context: gRPC context
        
        Returns:
            ListKeysResponse (keys list)
        """
        logger.info("LISTKEYS request")
        
        try:
            response = kvstore_pb2.ListKeysResponse(
                keys=[]
            )
            logger.info(f"LISTKEYS: returned {len(response.keys)} keys")
            return response
            
        except Exception as e:
            logger.error(f"LISTKEYS failed: {str(e)}")
            context.set_details(f"LISTKEYS failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.ListKeysResponse(keys=[])


# ============================================================================
# PHẦN 3: Implement Node Service
# ============================================================================

class NodeServicer(kvstore_pb2_grpc.NodeServiceServicer):
    """
    Implement Node gRPC service.
    Dùng cho inter-node communication: replication, heartbeat, forwarding.
    """

    def __init__(self, node_id: str, port: int):
        """Initialize Node service."""
        self.node_id = node_id
        self.port = port
        logger.info(f"NodeServicer initialized for {node_id}:{port}")

    def Heartbeat(self, request, context):
        """
        Handle Heartbeat request từ node khác.
        Để failure detection biết node này còn sống.
        
        Returns:
            HeartbeatResponse (node_id, timestamp)
        """
        logger.debug(f"Heartbeat from {request.node_id}")
        
        response = kvstore_pb2.HeartbeatResponse(
            node_id=self.node_id,
            timestamp=int(time.time()),
            is_alive=True
        )
        return response

    def ForwardPut(self, request, context):
        """
        Handle forwarded PUT request từ node khác.
        Khi client PUT key thuộc node khác, node đó forward đến node này.
        """
        logger.info(f"ForwardPut: key={request.key}")
        
        try:
            response = kvstore_pb2.PutResponse(
                success=True,
                node_id=self.node_id,
                replicas_count=1
            )
            return response
        except Exception as e:
            logger.error(f"ForwardPut failed: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.PutResponse(success=False)

    def ForwardGet(self, request, context):
        """Handle forwarded GET request từ node khác."""
        logger.info(f"ForwardGet: key={request.key}")
        
        try:
            response = kvstore_pb2.GetResponse(
                found=False,
                value="",
                node_id=self.node_id,
                timestamp=int(time.time())
            )
            return response
        except Exception as e:
            logger.error(f"ForwardGet failed: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.GetResponse(found=False)

    def ForwardDelete(self, request, context):
        """Handle forwarded DELETE request từ node khác."""
        logger.info(f"ForwardDelete: key={request.key}")
        
        try:
            response = kvstore_pb2.DeleteResponse(
                success=True,
                replicas_count=1
            )
            return response
        except Exception as e:
            logger.error(f"ForwardDelete failed: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.DeleteResponse(success=False)

    def Replicate(self, request, context):
        """
        Handle Replicate request từ primary node.
        Primary node gửi data đến replica node.
        """
        logger.info(f"Replicate: key={request.key}")
        
        try:
            response = kvstore_pb2.ReplicateResponse(
                success=True,
                node_id=self.node_id
            )
            return response
        except Exception as e:
            logger.error(f"Replicate failed: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.ReplicateResponse(success=False)

    def GetSnapshot(self, request, context):
        """
        Handle GetSnapshot request.
        Node recovering request snapshot của tất cả data từ node này.
        Dùng cho recovery khi node restart.
        """
        logger.info("GetSnapshot request")
        
        try:
            response = kvstore_pb2.SnapshotResponse(
                success=True,
                node_id=self.node_id,
                timestamp=int(time.time()),
                data=[]
            )
            return response
        except Exception as e:
            logger.error(f"GetSnapshot failed: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.SnapshotResponse(success=False)

    def JoinCluster(self, request, context):
        """
        Handle JoinCluster request từ node mới.
        Ghi nhận node mới vào cluster membership.
        """
        logger.info(f"JoinCluster from {request.node_id}")
        
        try:
            response = kvstore_pb2.JoinClusterResponse(
                success=True,
                cluster_nodes=[]
            )
            return response
        except Exception as e:
            logger.error(f"JoinCluster failed: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.JoinClusterResponse(success=False)


# ============================================================================
# PHẦN 4: Hàm Start Server
# ============================================================================

def serve(node_id: str = "node1", port: int = 8001):
    """
    Start gRPC server.
    
    Args:
        node_id: ID của node (e.g., "node1", "node2", "node3")
        port: Port để listen (e.g., 8001, 8002, 8003)
    """
    executor = futures.ThreadPoolExecutor(max_workers=10)
    server = grpc.server(executor)
    
    kv_servicer = KeyValueStoreServicer(node_id, port)
    node_servicer = NodeServicer(node_id, port)
    
    kvstore_pb2_grpc.add_KeyValueStoreServicer_to_server(
        kv_servicer, server
    )
    kvstore_pb2_grpc.add_NodeServiceServicer_to_server(
        node_servicer, server
    )
    
    address = f'0.0.0.0:{port}'
    server.add_insecure_port(address)
    
    server.start()
    logger.info(f"Server started on {address}")
    logger.info(f"Node ID: {node_id}")
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(grace=5)
        logger.info("Server stopped")


# ============================================================================
# PHẦN 5: Main Entry Point
# ============================================================================

if __name__ == '__main__':
    """
    Script entry point.
    Cách sử dụng:
        python server.py              # Default: node1 on port 8001
        python server.py 8002         # node1 on port 8002
        python server.py 8003 node3   # node3 on port 8003
    """
    
    port = 8001
    node_id = "node1"
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        node_id = sys.argv[2]
    
    if len(sys.argv) == 2:
        port_to_node = {
            8001: "node1",
            8002: "node2",
            8003: "node3"
        }
        node_id = port_to_node.get(port, f"node_{port}")
    
    serve(node_id, port)
# gRPC Server implementation
# TODO: Code here
