"""
Replication Manager - Quản lý replication logic
- Xác định replica nodes
- Gửi replicate requests đến replica nodes
- Xử lý replicate responses
"""

import logging
import grpc
from typing import List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.membership_manager import MembershipManager, Node
from src.proto import kvstore_pb2_grpc, kvstore_pb2

logger = logging.getLogger(__name__)


class ReplicationManager:
    """
    Quản lý replication cho distributed system.
    
    Xử lý:
    - Xác định replica nodes cho key (successor nodes trên hash ring)
    - Gửi ReplicateRequest đến replica nodes sau PUT/DELETE
    - Xử lý replicate responses
    - Retry logic nếu replication fail
    - Async replication để không block client
    """
    
    def __init__(self, membership_manager: MembershipManager, 
                 node_id: str, max_retries: int = 3):
        """
        Initialize ReplicationManager.
        
        Args:
            membership_manager: MembershipManager instance
            node_id: ID của node hiện tại
            max_retries: Số lần retry nếu replication fail (default 3)
        """
        self.membership = membership_manager
        self.node_id = node_id
        self.max_retries = max_retries
        self.executor = ThreadPoolExecutor(max_workers=10)  # Thread pool cho async replication
    
    def get_replica_nodes(self, key: str) -> List[Node]:
        """
        Lấy danh sách replica nodes cho key (không gồm primary).
        
        Algorithm:
        1. Lấy replication_factor nodes từ consistent hash
        2. Node đầu tiên là primary (owner)
        3. Các nodes còn lại là replicas
        
        Args:
            key: Key để tìm replicas
        
        Returns:
            List replica nodes (không gồm primary)
        """
        all_nodes = self.membership.get_all_replicas(key)
        
        # Trả về tất cả trừ node đầu tiên (primary)
        replicas = all_nodes[1:] if len(all_nodes) > 1 else []
        
        logger.debug(f"Replica nodes for key '{key}': {[n.node_id for n in replicas]}")
        return replicas
    
    def get_primary_node(self, key: str) -> Optional[Node]:
        """
        Lấy primary node (owner) cho key.
        
        Args:
            key: Key
        
        Returns:
            Primary node hoặc None
        """
        return self.membership.get_owner_node(key)
    
    def replicate_put(self, key: str, value: str, timestamp: int) -> int:
        """
        Gửi replicate PUT request đến tất cả replica nodes.
        Chạy async (không block).
        
        Args:
            key: Key để replicate
            value: Value để replicate
            timestamp: Timestamp của operation
        
        Returns:
            Số lượng replicas đã replicate thành công
        """
        replicas = self.get_replica_nodes(key)
        
        if not replicas:
            logger.debug(f"No replicas for key '{key}'")
            return 0
        
        # Submit async replication tasks
        futures = []
        for replica_node in replicas:
            future = self.executor.submit(
                self._send_replicate_request,
                replica_node=replica_node,
                key=key,
                value=value,
                timestamp=timestamp,
                operation=kvstore_pb2.PUT
            )
            futures.append(future)
        
        # Count successful replications (non-blocking)
        success_count = 0
        for future in futures:
            try:
                # Wait với timeout
                result = future.result(timeout=5)
                if result:
                    success_count += 1
            except Exception as e:
                logger.warning(f"Replication failed: {e}")
        
        logger.info(f"PUT replicated to {success_count}/{len(replicas)} replicas for key '{key}'")
        return success_count
    
    def replicate_delete(self, key: str, timestamp: int) -> int:
        """
        Gửi replicate DELETE request đến tất cả replica nodes.
        Chạy async (không block).
        
        Args:
            key: Key để delete từ replicas
            timestamp: Timestamp của operation
        
        Returns:
            Số lượng replicas đã delete thành công
        """
        replicas = self.get_replica_nodes(key)
        
        if not replicas:
            logger.debug(f"No replicas for key '{key}'")
            return 0
        
        # Submit async replication tasks
        futures = []
        for replica_node in replicas:
            future = self.executor.submit(
                self._send_replicate_request,
                replica_node=replica_node,
                key=key,
                value="",  # Empty for DELETE
                timestamp=timestamp,
                operation=kvstore_pb2.DELETE
            )
            futures.append(future)
        
        # Count successful deletes
        success_count = 0
        for future in futures:
            try:
                result = future.result(timeout=5)
                if result:
                    success_count += 1
            except Exception as e:
                logger.warning(f"Replication DELETE failed: {e}")
        
        logger.info(f"DELETE replicated to {success_count}/{len(replicas)} replicas for key '{key}'")
        return success_count
    
    def _send_replicate_request(self, replica_node: Node, key: str, value: str,
                                timestamp: int, operation: int) -> bool:
        """
        Gửi ReplicateRequest tới 1 replica node.
        Có retry logic nếu fail.
        
        Args:
            replica_node: Node nhận replicate request
            key: Key
            value: Value
            timestamp: Timestamp
            operation: ReplicateOperation.PUT hoặc DELETE
        
        Returns:
            True nếu replicate thành công, False nếu fail
        """
        address = replica_node.get_address()
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                # Tạo gRPC channel
                channel = grpc.insecure_channel(address, options=[
                    ('grpc.max_receive_message_length', -1),
                    ('grpc.max_send_message_length', -1),
                ])
                
                # Tạo stub
                stub = kvstore_pb2_grpc.NodeServiceStub(channel)
                
                # Tạo request
                request = kvstore_pb2.ReplicateRequest(
                    key=key,
                    value=value,
                    timestamp=timestamp,
                    primary_node=self.node_id,
                    operation=operation
                )
                
                # Gửi request (với timeout)
                response = stub.Replicate(request, timeout=5)
                
                # Close channel
                channel.close()
                
                if response.success:
                    logger.info(
                        f"Replicate {'PUT' if operation == kvstore_pb2.PUT else 'DELETE'} "
                        f"successful for key '{key}' on {replica_node.node_id}"
                    )
                    return True
                else:
                    logger.warning(
                        f"Replicate failed on {replica_node.node_id}: {response.message}"
                    )
                    return False
                    
            except grpc.RpcError as e:
                retry_count += 1
                logger.warning(
                    f"Replicate RPC error on {replica_node.node_id} "
                    f"(attempt {retry_count}/{self.max_retries}): {e.details()}"
                )
                
                if retry_count >= self.max_retries:
                    logger.error(
                        f"Replicate failed after {self.max_retries} attempts "
                        f"on {replica_node.node_id} for key '{key}'"
                    )
                    return False
                
                # Retry sau 100ms
                import time
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Replicate error on {replica_node.node_id}: {str(e)}")
                return False
        
        return False
    
    def handle_replicate_request(self, request: kvstore_pb2.ReplicateRequest,
                                 storage) -> bool:
        """
        Xử lý ReplicateRequest từ primary node.
        Lưu data vào replica storage.
        
        Args:
            request: ReplicateRequest message
            storage: StorageEngine instance của node này
        
        Returns:
            True nếu replicate thành công
        """
        try:
            key = request.key
            
            if request.operation == kvstore_pb2.PUT:
                # Lưu vào storage
                storage.put(key, request.value)
                logger.info(
                    f"Replicated PUT from {request.primary_node}: "
                    f"key='{key}', value='{request.value}'"
                )
                return True
                
            elif request.operation == kvstore_pb2.DELETE:
                # Xóa khỏi storage
                storage.delete(key)
                logger.info(
                    f"Replicated DELETE from {request.primary_node}: key='{key}'"
                )
                return True
            
            else:
                logger.error(f"Unknown operation: {request.operation}")
                return False
                
        except Exception as e:
            logger.error(f"Error handling replicate request: {str(e)}")
            return False
    
    def shutdown(self):
        """Cleanup resources."""
        self.executor.shutdown(wait=True)
        logger.info("ReplicationManager shutdown")
