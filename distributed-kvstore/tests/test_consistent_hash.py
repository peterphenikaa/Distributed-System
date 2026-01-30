"""
Unit Tests cho ConsistentHash và MembershipManager
"""

import sys
import os

# Fix import path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.consistent_hash import ConsistentHash
from src.membership_manager import MembershipManager, Node


def test_consistent_hash_basic():
    """Test basic ConsistentHash operations."""
    print("\n=== Test 1: Basic ConsistentHash ===")
    
    nodes = ["node1", "node2", "node3"]
    ch = ConsistentHash(nodes=nodes, virtual_nodes=150)
    
    # Test: All nodes added
    assert len(ch.get_all_nodes()) == 3, "Should have 3 nodes"
    print("✅ All nodes added correctly")
    
    # Test: Hash ring has virtual nodes
    assert len(ch.hash_ring) == 3 * 150, "Should have 450 virtual nodes (3 * 150)"
    print("✅ Virtual nodes created correctly")
    
    # Test: Get node for key
    node1 = ch.get_node("user:1")
    assert node1 in nodes, "Key should map to one of the nodes"
    print(f"✅ Key 'user:1' maps to {node1}")
    
    # Test: Same key always maps to same node
    node1_again = ch.get_node("user:1")
    assert node1 == node1_again, "Same key should map to same node"
    print("✅ Consistent mapping verified")


def test_consistent_hash_distribution():
    """Test hash ring distribution."""
    print("\n=== Test 2: Hash Ring Distribution ===")
    
    nodes = ["node1", "node2", "node3"]
    ch = ConsistentHash(nodes=nodes, virtual_nodes=150)
    
    distribution = ch.get_distribution()
    print(f"Distribution: {distribution}")
    
    # Verify each node has 150 virtual nodes
    for node in nodes:
        assert distribution[node] == 150, f"{node} should have 150 virtual nodes"
    
    print("✅ Distribution is balanced (150 virtual nodes per physical node)")


def test_consistent_hash_replication():
    """Test get_nodes for replication."""
    print("\n=== Test 3: Replication Nodes ===")
    
    nodes = ["node1", "node2", "node3"]
    ch = ConsistentHash(nodes=nodes, virtual_nodes=150)
    
    # Test: Get 3 replica nodes for a key
    replicas = ch.get_nodes("user:100", count=3)
    assert len(replicas) == 3, "Should return 3 unique nodes"
    assert len(set(replicas)) == 3, "All replica nodes should be unique"
    print(f"✅ Key 'user:100' has replicas on: {replicas}")
    
    # Test: Get 2 replica nodes
    replicas2 = ch.get_nodes("user:200", count=2)
    assert len(replicas2) == 2, "Should return 2 unique nodes"
    print(f"✅ Key 'user:200' has replicas on: {replicas2}")


def test_consistent_hash_remove_node():
    """Test adding/removing nodes."""
    print("\n=== Test 4: Add/Remove Nodes ===")
    
    nodes = ["node1", "node2"]
    ch = ConsistentHash(nodes=nodes, virtual_nodes=100)
    
    # Initial state
    key_location_before = ch.get_node("key1")
    print(f"Key 'key1' initially on {key_location_before}")
    
    # Add node3
    ch.add_node("node3")
    assert len(ch.get_all_nodes()) == 3, "Should have 3 nodes after adding"
    print("✅ Node3 added successfully")
    
    # Remove node2
    ch.remove_node("node2")
    assert len(ch.get_all_nodes()) == 2, "Should have 2 nodes after removing"
    assert "node2" not in ch.get_all_nodes()
    print("✅ Node2 removed successfully")
    
    # Verify no key maps to removed node
    for key in ["key1", "key2", "key3"]:
        node = ch.get_node(key)
        assert node in ["node1", "node3"], f"Key {key} should only map to remaining nodes"
    
    print("✅ No keys map to removed node")


def test_membership_manager_load_config():
    """Test MembershipManager loading config."""
    print("\n=== Test 5: MembershipManager - Load Config ===")
    
    config_path = os.path.join(project_root, "config", "cluster.json")
    mm = MembershipManager(config_path)
    
    # Test: Nodes loaded
    nodes = mm.get_all_nodes()
    assert len(nodes) == 3, "Should load 3 nodes from config"
    print(f"✅ Loaded {len(nodes)} nodes")
    
    # Test: Node IDs
    node_ids = [n.node_id for n in nodes]
    assert "node1" in node_ids
    assert "node2" in node_ids
    assert "node3" in node_ids
    print("✅ Node IDs correct: node1, node2, node3")
    
    # Test: Node addresses
    node1 = mm.get_node_by_id("node1")
    assert node1.get_address() == "localhost:8001"
    print(f"✅ Node1 address: {node1.get_address()}")


def test_membership_manager_owner_node():
    """Test finding owner node for key."""
    print("\n=== Test 6: MembershipManager - Owner Node ===")
    
    config_path = os.path.join(project_root, "config", "cluster.json")
    mm = MembershipManager(config_path)
    
    # Test: Get owner for key
    owner = mm.get_owner_node("user:1")
    assert owner is not None, "Should find owner for key"
    assert owner.node_id in ["node1", "node2", "node3"]
    print(f"✅ Key 'user:1' owner: {owner.node_id}")
    
    # Test: Same key always maps to same owner
    owner_again = mm.get_owner_node("user:1")
    assert owner.node_id == owner_again.node_id
    print("✅ Consistent owner mapping verified")
    
    # Test: Different keys may have different owners
    keys_owners = {}
    for i in range(100):
        key = f"user:{i}"
        owner = mm.get_owner_node(key)
        node_id = owner.node_id
        keys_owners[node_id] = keys_owners.get(node_id, 0) + 1
    
    print(f"✅ 100 keys distributed: {keys_owners}")
    # Verify roughly even distribution
    for count in keys_owners.values():
        assert 20 <= count <= 50, f"Should be roughly distributed (got {count} keys)"
    print("✅ Distribution is roughly balanced")


def test_membership_manager_replicas():
    """Test finding replica nodes."""
    print("\n=== Test 7: MembershipManager - Replicas ===")
    
    config_path = os.path.join(project_root, "config", "cluster.json")
    mm = MembershipManager(config_path)
    
    # Test: Get all replicas (including owner)
    all_replicas = mm.get_all_replicas("key:1")
    assert len(all_replicas) <= mm.replication_factor
    print(f"✅ All replicas for 'key:1': {[n.node_id for n in all_replicas]}")
    
    # Test: Get only replica nodes (excluding owner)
    replicas = mm.get_replica_nodes("key:1")
    assert len(replicas) < len(all_replicas)
    print(f"✅ Replica nodes for 'key:1': {[n.node_id for n in replicas]}")
    
    # Test: All replicas are unique
    replica_ids = [n.node_id for n in all_replicas]
    assert len(replica_ids) == len(set(replica_ids)), "All replicas should be unique"
    print("✅ All replicas are unique")


def test_membership_manager_node_status():
    """Test node alive/dead status."""
    print("\n=== Test 8: MembershipManager - Node Status ===")
    
    config_path = os.path.join(project_root, "config", "cluster.json")
    mm = MembershipManager(config_path)
    
    # Test: All nodes initially alive
    alive_nodes = mm.get_alive_nodes()
    assert len(alive_nodes) == 3
    print(f"✅ All nodes initially alive: {len(alive_nodes)}")
    
    # Test: Mark node as dead
    mm.mark_node_dead("node1")
    alive_nodes = mm.get_alive_nodes()
    assert len(alive_nodes) == 2
    node_ids = [n.node_id for n in alive_nodes]
    assert "node1" not in node_ids
    print("✅ Node1 marked as dead, alive_nodes = 2")
    
    # Test: Mark node as alive again
    mm.mark_node_alive("node1")
    alive_nodes = mm.get_alive_nodes()
    assert len(alive_nodes) == 3
    print("✅ Node1 marked as alive again, alive_nodes = 3")


def test_membership_manager_dynamic_nodes():
    """Test dynamic node addition/removal."""
    print("\n=== Test 9: MembershipManager - Dynamic Nodes ===")
    
    config_path = os.path.join(project_root, "config", "cluster.json")
    mm = MembershipManager(config_path)
    
    # Initial state
    initial_count = len(mm.get_all_nodes())
    print(f"Initial nodes: {initial_count}")
    
    # Add node4
    mm.add_node("node4", "localhost", 8004, "localhost", 6382)
    assert len(mm.get_all_nodes()) == initial_count + 1
    assert "node4" in [n.node_id for n in mm.get_all_nodes()]
    print("✅ Node4 added successfully")
    
    # Remove node4
    mm.remove_node("node4")
    assert len(mm.get_all_nodes()) == initial_count
    assert "node4" not in [n.node_id for n in mm.get_all_nodes()]
    print("✅ Node4 removed successfully")


def test_hash_distribution_uniformity():
    """Test hash distribution uniformity across keys."""
    print("\n=== Test 10: Hash Distribution Uniformity ===")
    
    config_path = os.path.join(project_root, "config", "cluster.json")
    mm = MembershipManager(config_path)
    
    # Distribute 1000 keys across nodes
    distribution = {}
    for i in range(1000):
        key = f"key:{i}"
        owner = mm.get_owner_node(key)
        node_id = owner.node_id
        distribution[node_id] = distribution.get(node_id, 0) + 1
    
    print(f"Distribution of 1000 keys: {distribution}")
    
    # Check uniformity (within ±10% of average)
    avg = 1000 / 3
    for count in distribution.values():
        ratio = count / avg
        assert 0.85 <= ratio <= 1.15, f"Distribution imbalanced: {ratio:.2f}x average"
    
    print("✅ Hash distribution is uniform (within ±15% of average)")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running ConsistentHash & MembershipManager Unit Tests")
    print("=" * 60)
    
    tests = [
        test_consistent_hash_basic,
        test_consistent_hash_distribution,
        test_consistent_hash_replication,
        test_consistent_hash_remove_node,
        test_membership_manager_load_config,
        test_membership_manager_owner_node,
        test_membership_manager_replicas,
        test_membership_manager_node_status,
        test_membership_manager_dynamic_nodes,
        test_hash_distribution_uniformity,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
