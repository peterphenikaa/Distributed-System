"""
Membership Manager - Quản lý cluster nodes
Load cluster config, track node status, manage node list
"""

import json
from typing import Dict, List, Optional
import logging

from src.consistent_hash import ConsistentHash

logger = logging.getLogger(__name__)


class Node:
    """Đại diện cho 1 node trong cluster."""
    
    def __init__(self, node_id: str, host: str, port: int, 
                 redis_host: str = None, redis_port: int = None):
        """
        Initialize Node.
        
        Args:
            node_id: Node identifier (e.g., "node1")
            host: Host/IP address
            port: gRPC port
            redis_host: Redis host
            redis_port: Redis port
        """
        self.node_id = node_id
        self.host = host
        self.port = port
        self.redis_host = redis_host or host
        self.redis_port = redis_port or 6379
        self.is_alive = True  # Status của node
    
    def get_address(self) -> str:
        """Trả về address dạng host:port cho gRPC connection."""
        return f"{self.host}:{self.port}"
    
    def __repr__(self) -> str:
        return f"Node({self.node_id}, {self.get_address()})"
    
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.node_id == other.node_id
        return False
    
    def __hash__(self):
        return hash(self.node_id)


class MembershipManager:
    """
    Quản lý cluster membership (danh sách nodes).
    
    Xử lý:
    - Load cluster config từ cluster.json
    - Quản lý consistent hash ring
    - Tìm owner node cho key
    - Tìm replica nodes
    - Quản lý node alive status
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize MembershipManager.
        
        Args:
            config_path: Đường dẫn đến cluster.json
        """
        self.nodes: Dict[str, Node] = {}  # node_id -> Node mapping
        self.consistent_hash: Optional[ConsistentHash] = None
        self.replication_factor = 2  # Default: primary + 1 replica
        self.virtual_nodes = 150  # Virtual nodes per physical node
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """
        Load cluster config từ JSON file.
        
        Config format:
        {
            "nodes": [
                {"id": "node1", "host": "localhost", "port": 8001, ...},
                ...
            ],
            "replication": {"replication_factor": 2},
            "consistent_hashing": {"virtual_nodes": 150}
        }
        
        Args:
            config_path: Đường dẫn đến cluster.json
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Load replication factor
            if 'replication' in config:
                self.replication_factor = config['replication'].get(
                    'replication_factor', 2
                )
            
            # Load virtual nodes count
            if 'consistent_hashing' in config:
                self.virtual_nodes = config['consistent_hashing'].get(
                    'virtual_nodes', 150
                )
            
            # Load nodes
            self.nodes = {}
            node_ids = []
            
            for node_config in config.get('nodes', []):
                node_id = node_config['id']
                node = Node(
                    node_id=node_id,
                    host=node_config['host'],
                    port=node_config['port'],
                    redis_host=node_config.get('redis_host', node_config['host']),
                    redis_port=node_config.get('redis_port', 6379)
                )
                self.nodes[node_id] = node
                node_ids.append(node_id)
            
            # Initialize consistent hash ring
            self.consistent_hash = ConsistentHash(
                nodes=node_ids,
                virtual_nodes=self.virtual_nodes
            )
            
            logger.info(f"Loaded cluster config: {len(self.nodes)} nodes")
            logger.info(f"Replication factor: {self.replication_factor}")
            logger.info(f"Virtual nodes per physical node: {self.virtual_nodes}")
            
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    def get_node_by_id(self, node_id: str) -> Optional[Node]:
        """Lấy Node object theo node ID."""
        return self.nodes.get(node_id)
    
    def get_all_nodes(self) -> List[Node]:
        """Lấy tất cả nodes."""
        return list(self.nodes.values())
    
    def get_alive_nodes(self) -> List[Node]:
        """Lấy tất cả alive nodes."""
        return [node for node in self.nodes.values() if node.is_alive]
    
    def get_owner_node(self, key: str) -> Optional[Node]:
        """
        Tìm node sẽ lưu key này (primary owner).
        
        Args:
            key: Key để tìm owner
        
        Returns:
            Node object hoặc None
        """
        if not self.consistent_hash:
            return None
        
        node_id = self.consistent_hash.get_node(key)
        return self.get_node_by_id(node_id) if node_id else None
    
    def get_replica_nodes(self, key: str) -> List[Node]:
        """
        Tìm replica nodes cho key (theo replication_factor).
        
        Args:
            key: Key để tìm replicas
        
        Returns:
            List Node objects (không gồm owner)
        """
        if not self.consistent_hash:
            return []
        
        # Lấy `replication_factor` nodes (gồm cả owner)
        node_ids = self.consistent_hash.get_nodes(key, self.replication_factor)
        
        # Convert từ node IDs sang Node objects
        nodes = [self.get_node_by_id(nid) for nid in node_ids if nid]
        
        # Trả về replicas (bỏ owner - node đầu tiên)
        return nodes[1:] if len(nodes) > 1 else []
    
    def get_all_replicas(self, key: str) -> List[Node]:
        """
        Lấy tất cả nodes lưu key (gồm cả owner).
        
        Args:
            key: Key
        
        Returns:
            List Node objects
        """
        if not self.consistent_hash:
            return []
        
        node_ids = self.consistent_hash.get_nodes(key, self.replication_factor)
        return [self.get_node_by_id(nid) for nid in node_ids if nid]
    
    def mark_node_alive(self, node_id: str) -> None:
        """Đánh dấu node là alive."""
        if node_id in self.nodes:
            self.nodes[node_id].is_alive = True
            logger.info(f"Node {node_id} marked as alive")
    
    def mark_node_dead(self, node_id: str) -> None:
        """Đánh dấu node là dead (failure detected)."""
        if node_id in self.nodes:
            self.nodes[node_id].is_alive = False
            logger.warning(f"Node {node_id} marked as dead")
    
    def add_node(self, node_id: str, host: str, port: int,
                 redis_host: str = None, redis_port: int = None) -> None:
        """
        Thêm node mới vào cluster (dynamic).
        Tự động update hash ring.
        
        Args:
            node_id: Node ID
            host: Host
            port: Port
            redis_host: Redis host
            redis_port: Redis port
        """
        node = Node(node_id, host, port, redis_host, redis_port)
        self.nodes[node_id] = node
        
        if self.consistent_hash:
            self.consistent_hash.add_node(node_id)
        
        logger.info(f"Added node: {node}")
    
    def remove_node(self, node_id: str) -> None:
        """
        Xóa node khỏi cluster (dynamic).
        Tự động update hash ring.
        
        Args:
            node_id: Node ID
        """
        if node_id in self.nodes:
            del self.nodes[node_id]
            
            if self.consistent_hash:
                self.consistent_hash.remove_node(node_id)
            
            logger.info(f"Removed node: {node_id}")
    
    def get_hash_distribution(self) -> Dict[str, int]:
        """
        Lấy distribution của hash ring.
        (Để debug, verify balance)
        
        Returns:
            Dict {node_id: virtual_node_count}
        """
        if not self.consistent_hash:
            return {}
        return self.consistent_hash.get_distribution()
