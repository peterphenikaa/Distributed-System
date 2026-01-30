"""
Consistent Hashing Implementation
Sử dụng MD5 hash và virtual nodes để phân chia data đều trên các nodes
"""

import hashlib
from typing import List, Dict, Optional
import bisect


class ConsistentHash:
    """
    Consistent Hashing algorithm with virtual nodes.
    
    Xử lý:
    - Tạo hash ring từ danh sách nodes
    - Map key đến node trên ring
    - Hỗ trợ virtual nodes để balance tốt hơn
    - Tự động thêm/xóa nodes mà không shuffle toàn bộ data
    """
    
    def __init__(self, nodes: List[str] = None, virtual_nodes: int = 150):
        """
        Initialize ConsistentHash.
        
        Args:
            nodes: List node names (e.g., ["node1", "node2", "node3"])
            virtual_nodes: Số virtual nodes per physical node (default 150)
        """
        self.virtual_nodes = virtual_nodes  # Virtual nodes per physical node
        self.hash_ring = {}  # hash_value -> node_name mapping
        self.sorted_keys = []  # Sorted list of hash values cho binary search
        self.nodes = set()  # Set of node names
        
        if nodes:
            for node in nodes:
                self.add_node(node)
    
    def _hash(self, key: str) -> int:
        """
        Tính hash value của key.
        
        Args:
            key: Key để hash
        
        Returns:
            Hash value (0 to 2^32-1)
        """
        # Sử dụng MD5 hash function
        md5 = hashlib.md5(key.encode('utf-8'))
        # Lấy 8 bytes đầu (64 bits) và convert thành int
        return int(md5.hexdigest()[:8], 16)
    
    def add_node(self, node: str) -> None:
        """
        Thêm node vào hash ring.
        Tạo `virtual_nodes` virtual nodes cho physical node này.
        
        Args:
            node: Node name (e.g., "node1")
        """
        self.nodes.add(node)
        
        # Tạo virtual nodes
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            self.hash_ring[hash_value] = node
        
        # Sort hash keys cho binary search
        self.sorted_keys = sorted(self.hash_ring.keys())
    
    def remove_node(self, node: str) -> None:
        """
        Xóa node khỏi hash ring.
        Xóa tất cả virtual nodes của node này.
        
        Args:
            node: Node name
        """
        if node not in self.nodes:
            return
        
        self.nodes.discard(node)
        
        # Xóa tất cả virtual nodes của node này
        keys_to_remove = []
        for hash_value, node_name in self.hash_ring.items():
            if node_name == node:
                keys_to_remove.append(hash_value)
        
        for hash_value in keys_to_remove:
            del self.hash_ring[hash_value]
        
        # Re-sort hash keys
        self.sorted_keys = sorted(self.hash_ring.keys())
    
    def get_node(self, key: str) -> Optional[str]:
        """
        Tìm node sẽ lưu key này.
        
        Algorithm:
        1. Hash key thành hash_value
        2. Tìm virtual node trên ring có hash >= hash_value
        3. Return physical node của virtual node đó
        
        Args:
            key: Key để tìm node
        
        Returns:
            Node name hoặc None nếu ring trống
        """
        if not self.hash_ring:
            return None
        
        hash_value = self._hash(key)
        
        # Binary search để tìm position trên sorted ring
        idx = bisect.bisect_right(self.sorted_keys, hash_value)
        
        # Nếu không tìm thấy trên phần bên phải, wrap around về đầu
        if idx == len(self.sorted_keys):
            idx = 0
        
        hash_key = self.sorted_keys[idx]
        return self.hash_ring[hash_key]
    
    def get_nodes(self, key: str, count: int = 1) -> List[str]:
        """
        Tìm `count` nodes cho replication.
        Trả về list nodes khác nhau (không duplicate).
        
        Args:
            key: Key để tìm nodes
            count: Số nodes cần (default 1)
        
        Returns:
            List of node names
        """
        if not self.hash_ring or count <= 0:
            return []
        
        # Số unique nodes không thể vượt quá tổng số nodes
        count = min(count, len(self.nodes))
        
        hash_value = self._hash(key)
        
        # Tìm position trên sorted ring
        idx = bisect.bisect_right(self.sorted_keys, hash_value)
        
        result = []
        seen = set()
        
        # Iterate qua ring từ position đó đến khi có đủ unique nodes
        for i in range(len(self.sorted_keys)):
            current_idx = (idx + i) % len(self.sorted_keys)
            hash_key = self.sorted_keys[current_idx]
            node = self.hash_ring[hash_key]
            
            if node not in seen:
                result.append(node)
                seen.add(node)
                
                if len(result) == count:
                    break
        
        return result
    
    def get_all_nodes(self) -> List[str]:
        """Lấy tất cả physical nodes trên ring."""
        return sorted(list(self.nodes))
    
    def get_node_key_count(self, node: str) -> int:
        """
        Tính số virtual nodes của 1 node trên ring.
        (Để debug, verify distribution)
        """
        return sum(1 for n in self.hash_ring.values() if n == node)
    
    def get_distribution(self) -> Dict[str, int]:
        """
        Lấy distribution của tất cả nodes (số virtual nodes mỗi cái).
        Dùng để verify ring balance.
        
        Returns:
            Dict {node_name: virtual_node_count}
        """
        distribution = {node: 0 for node in self.nodes}
        for node in self.hash_ring.values():
            distribution[node] += 1
        return distribution
