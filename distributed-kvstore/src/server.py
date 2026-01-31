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

# Fix import path - add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import generated gRPC code
from src.proto import kvstore_pb2  # Generated message classes
from src.proto import kvstore_pb2_grpc  # Generated service stubs
from src.storage.storage_engine import StorageEngine  # Storage engine
from src.membership_manager import MembershipManager  # Cluster membership
from src.replication_manager import ReplicationManager  # Replication management

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

    def __init__(self, node_id: str, port: int, storage, membership_manager, replication_manager):
        """
        Initialize servicer.
        
        Args:
            node_id: ID của node này (e.g., "node1")
            port: Port mà server listen (e.g., 8001)
            storage: StorageEngine instance
            membership_manager: MembershipManager instance
            replication_manager: ReplicationManager instance
        """
        self.node_id = node_id
        self.port = port
        self.storage = storage
        self.membership = membership_manager
        self.replication = replication_manager
        logger.info(f"KeyValueStoreServicer initialized for {node_id}:{port}")

    def Put(self, request, context):
        """
        Handle PUT request từ client.
        
        Phase 3: Check if we're the owner, otherwise forward to owner node.
        
        Args:
            request: PutRequest message (key, value, timestamp)
            context: gRPC context (client info, timeout, ...)
        
        Returns:
            PutResponse (success, node_id, replicas_count)
        """
        logger.info(f"PUT request: key={request.key}, value={request.value}")
        
        try:
            # Task 3.5: Determine owner node
            owner_node = self.membership.get_owner_node(request.key)
            
            if owner_node is None:
                logger.error("No owner node found (cluster empty?)")
                context.set_details("No available nodes")
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                return kvstore_pb2.PutResponse(success=False)
            
            # Task 3.6: Check if we're the owner
            if owner_node.node_id == self.node_id:
                # We're the owner - handle locally
                logger.info(f"[LOCAL] This node owns key={request.key}")
                self.storage.put(request.key, request.value)
                
                # Task 4.3: Replicate PUT to replica nodes (async, non-blocking)
                timestamp = int(time.time())
                replicas_count = self.replication.replicate_put(
                    request.key, 
                    request.value, 
                    timestamp
                )
                
                response = kvstore_pb2.PutResponse(
                    success=True,
                    node_id=self.node_id,
                    replicas_count=replicas_count + 1  # +1 for primary
                )
                logger.info(f"PUT success (local): key={request.key}, replicas={replicas_count + 1}")
                return response
            else:
                # We're NOT the owner - forward to owner node
                logger.info(f"[FORWARD] key={request.key} belongs to {owner_node.node_id}")
                
                # Forward to owner node
                owner_address = owner_node.get_address()
                channel = grpc.insecure_channel(owner_address)
                stub = kvstore_pb2_grpc.NodeServiceStub(channel)
                
                # Call ForwardPut on owner node
                forward_response = stub.ForwardPut(request, timeout=5.0)
                channel.close()
                
                logger.info(f"PUT forwarded to {owner_node.node_id}: success={forward_response.success}")
                return forward_response
            
        except grpc.RpcError as e:
            logger.error(f"Forward PUT failed (gRPC error): {str(e)}")
            context.set_details(f"Forward failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.PutResponse(success=False)
        except Exception as e:
            logger.error(f"PUT failed: {str(e)}")
            context.set_details(f"PUT failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.PutResponse(success=False)

    def Get(self, request, context):
        """
        Handle GET request từ client.
        
        Phase 3: Check if we're the owner, otherwise forward to owner node.
        
        Args:
            request: GetRequest message (key)
            context: gRPC context
        
        Returns:
            GetResponse (found, value, node_id, timestamp)
        """
        logger.info(f"GET request: key={request.key}")
        
        try:
            # Task 3.5: Determine owner node
            owner_node = self.membership.get_owner_node(request.key)
            
            if owner_node is None:
                logger.error("No owner node found")
                context.set_details("No available nodes")
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                return kvstore_pb2.GetResponse(found=False)
            
            # Task 3.6: Check if we're the owner
            if owner_node.node_id == self.node_id:
                # We're the owner - handle locally
                logger.info(f"[LOCAL] This node owns key={request.key}")
                value, found = self.storage.get(request.key)
                
                response = kvstore_pb2.GetResponse(
                    found=found,
                    value=value if found else "",
                    node_id=self.node_id,
                    timestamp=int(time.time())
                )
                logger.info(f"GET (local): key={request.key}, found={found}")
                return response
            else:
                # We're NOT the owner - forward to owner node
                logger.info(f"[FORWARD] key={request.key} belongs to {owner_node.node_id}")
                
                # Forward to owner node
                owner_address = owner_node.get_address()
                channel = grpc.insecure_channel(owner_address)
                stub = kvstore_pb2_grpc.NodeServiceStub(channel)
                
                # Call ForwardGet on owner node
                forward_response = stub.ForwardGet(request, timeout=5.0)
                channel.close()
                
                logger.info(f"GET forwarded to {owner_node.node_id}: found={forward_response.found}")
                return forward_response
            
        except grpc.RpcError as e:
            logger.error(f"Forward GET failed (gRPC error): {str(e)}")
            context.set_details(f"Forward failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.GetResponse(found=False)
        except Exception as e:
            logger.error(f"GET failed: {str(e)}")
            context.set_details(f"GET failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.GetResponse(found=False)

    def Delete(self, request, context):
        """
        Handle DELETE request từ client.
        
        Phase 3: Check if we're the owner, otherwise forward to owner node.
        
        Args:
            request: DeleteRequest message (key)
            context: gRPC context
        
        Returns:
            DeleteResponse (success, replicas_count)
        """
        logger.info(f"DELETE request: key={request.key}")
        
        try:
            # Task 3.5: Determine owner node
            owner_node = self.membership.get_owner_node(request.key)
            
            if owner_node is None:
                logger.error("No owner node found")
                context.set_details("No available nodes")
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                return kvstore_pb2.DeleteResponse(success=False)
            
            # Task 3.6: Check if we're the owner
            if owner_node.node_id == self.node_id:
                # We're the owner - handle locally
                logger.info(f"[LOCAL] This node owns key={request.key}")
                deleted = self.storage.delete(request.key)
                
                # Task 4.3: Replicate DELETE to replica nodes (async, non-blocking)
                if deleted:
                    timestamp = int(time.time())
                    replicas_count = self.replication.replicate_delete(request.key, timestamp)
                else:
                    replicas_count = 0
                
                response = kvstore_pb2.DeleteResponse(
                    success=deleted,
                    replicas_count=replicas_count + (1 if deleted else 0)
                )
                
                if deleted:
                    logger.info(f"DELETE success (local): key={request.key}, replicas={replicas_count + 1}")
                else:
                    logger.warning(f"DELETE: key not found: {request.key}")
                
                return response
            else:
                # We're NOT the owner - forward to owner node
                logger.info(f"[FORWARD] key={request.key} belongs to {owner_node.node_id}")
                
                # Forward to owner node
                owner_address = owner_node.get_address()
                channel = grpc.insecure_channel(owner_address)
                stub = kvstore_pb2_grpc.NodeServiceStub(channel)
                
                # Call ForwardDelete on owner node
                forward_response = stub.ForwardDelete(request, timeout=5.0)
                channel.close()
                
                logger.info(f"DELETE forwarded to {owner_node.node_id}: success={forward_response.success}")
                return forward_response
            
        except grpc.RpcError as e:
            logger.error(f"Forward DELETE failed (gRPC error): {str(e)}")
            context.set_details(f"Forward failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.DeleteResponse(success=False)
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
            # Get all keys from storage
            keys = self.storage.list_keys()
            
            response = kvstore_pb2.ListKeysResponse(
                keys=keys
            )
            logger.info(f"LISTKEYS: returned {len(keys)} keys")
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

    def __init__(self, node_id: str, port: int, storage, replication_manager=None):
        """
        Initialize Node service.
        
        Args:
            node_id: Node ID
            port: Port
            storage: StorageEngine instance (for handling forwarded requests)
            replication_manager: ReplicationManager instance (optional)
        """
        self.node_id = node_id
        self.port = port
        self.storage = storage
        self.replication = replication_manager
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
        
        Task 3.7: Implement actual storage logic.
        """
        logger.info(f"[FORWARDED] ForwardPut: key={request.key}, value={request.value}")
        
        try:
            # Save to local storage (we are the owner)
            self.storage.put(request.key, request.value)
            
            response = kvstore_pb2.PutResponse(
                success=True,
                node_id=self.node_id,
                replicas_count=1
            )
            logger.info(f"ForwardPut success: key={request.key}")
            return response
        except Exception as e:
            logger.error(f"ForwardPut failed: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.PutResponse(success=False)

    def ForwardGet(self, request, context):
        """
        Handle forwarded GET request từ node khác.
        
        Task 3.7: Implement actual storage retrieval logic.
        """
        logger.info(f"[FORWARDED] ForwardGet: key={request.key}")
        
        try:
            # Get from local storage (we are the owner)
            value, found = self.storage.get(request.key)
            
            response = kvstore_pb2.GetResponse(
                found=found,
                value=value if found else "",
                node_id=self.node_id,
                timestamp=int(time.time())
            )
            logger.info(f"ForwardGet: key={request.key}, found={found}")
            return response
        except Exception as e:
            logger.error(f"ForwardGet failed: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.GetResponse(found=False)

    def ForwardDelete(self, request, context):
        """
        Handle forwarded DELETE request từ node khác.
        
        Task 3.7: Implement actual storage deletion logic.
        """
        logger.info(f"[FORWARDED] ForwardDelete: key={request.key}")
        
        try:
            # Delete from local storage (we are the owner)
            deleted = self.storage.delete(request.key)
            
            response = kvstore_pb2.DeleteResponse(
                success=deleted,
                replicas_count=1
            )
            logger.info(f"ForwardDelete: key={request.key}, deleted={deleted}")
            return response
        except Exception as e:
            logger.error(f"ForwardDelete failed: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.DeleteResponse(success=False)

    def Replicate(self, request, context):
        """
        Handle Replicate request từ primary node.
        Lưu replicated data vào replica node này.
        
        Task 4.1-4.3: Handle replication requests (PUT or DELETE).
        """
        operation_name = "PUT" if request.operation == kvstore_pb2.PUT else "DELETE"
        logger.info(f"[REPLICATE] {operation_name}: key={request.key} from {request.primary_node}")
        
        try:
            # Handle based on operation type
            success = False
            
            if request.operation == kvstore_pb2.PUT:
                self.storage.put(request.key, request.value)
                success = True
                logger.info(f"Replicated PUT: key={request.key}, value={request.value}")
                
            elif request.operation == kvstore_pb2.DELETE:
                deleted = self.storage.delete(request.key)
                success = deleted
                logger.info(f"Replicated DELETE: key={request.key}, deleted={deleted}")
            
            response = kvstore_pb2.ReplicateResponse(
                success=success,
                replica_node_id=self.node_id
            )
            return response
            
        except Exception as e:
            logger.error(f"Replicate handler failed: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return kvstore_pb2.ReplicateResponse(success=False)

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
    
    # Create storage engine
    storage = StorageEngine()
    
    # Load cluster membership (Phase 3)
    config_path = os.path.join(project_root, "config", "cluster.json")
    membership = MembershipManager(config_path)
    logger.info(f"Loaded cluster config: {len(membership.get_all_nodes())} nodes")
    
    # Create replication manager (Phase 4)
    replication = ReplicationManager(membership, node_id)
    logger.info(f"Initialized ReplicationManager for {node_id}")
    
    kv_servicer = KeyValueStoreServicer(node_id, port, storage, membership, replication)
    node_servicer = NodeServicer(node_id, port, storage, replication)
    
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
        replication.shutdown()
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





