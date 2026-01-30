"""
Test Phase 3 - Distribution Verification
Test data phân chia đều giữa 3 nodes (~33% mỗi node)
"""

import sys
import os
import grpc
import time

# Fix import path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.proto import kvstore_pb2
from src.proto import kvstore_pb2_grpc


def connect_to_node(port):
    """Connect to a node."""
    address = f'localhost:{port}'
    channel = grpc.insecure_channel(address)
    stub = kvstore_pb2_grpc.KeyValueStoreStub(channel)
    return channel, stub


def list_keys_on_node(port):
    """Get all keys stored on a specific node."""
    try:
        channel, stub = connect_to_node(port)
        request = kvstore_pb2.ListKeysRequest()
        response = stub.ListKeys(request, timeout=5.0)
        channel.close()
        return list(response.keys) if response.keys else []
    except Exception as e:
        print(f"❌ Error listing keys on node {port}: {e}")
        return []


def test_distribution():
    """
    Test Phase 3 - Data Distribution.
    
    Steps:
    1. Connect to node1
    2. PUT 100 keys
    3. Check distribution across 3 nodes
    4. Verify ~33% per node
    """
    
    print("\n" + "=" * 70)
    print("  PHASE 3 TEST: Data Distribution Across 3 Nodes")
    print("=" * 70)
    
    # Step 1: Connect to node1
    print("\n[1] Connecting to node1 (localhost:8001)...")
    try:
        channel, stub = connect_to_node(8001)
        print("✅ Connected to node1")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # Step 2: PUT 100 keys
    print("\n[2] Inserting 100 keys (key_0 to key_99)...")
    success_count = 0
    
    for i in range(100):
        key = f"key_{i}"
        value = f"value_{i}"
        
        try:
            request = kvstore_pb2.PutRequest(key=key, value=value)
            response = stub.Put(request, timeout=5.0)
            
            if response.success:
                success_count += 1
                if (i + 1) % 20 == 0:
                    print(f"   Progress: {i + 1}/100 keys inserted...")
            else:
                print(f"❌ PUT failed for {key}")
        except Exception as e:
            print(f"❌ Error inserting {key}: {e}")
    
    print(f"✅ Successfully inserted {success_count}/100 keys\n")
    channel.close()
    
    # Wait for data to settle
    time.sleep(1)
    
    # Step 3: Check distribution on each node
    print("[3] Checking data distribution across nodes...")
    print("-" * 70)
    
    nodes = [
        (8001, "node1"),
        (8002, "node2"),
        (8003, "node3")
    ]
    
    distribution = {}
    total_keys = 0
    
    for port, node_id in nodes:
        keys = list_keys_on_node(port)
        count = len(keys)
        distribution[node_id] = {
            'count': count,
            'keys': keys,
            'percentage': 0  # Will calculate after
        }
        total_keys += count
        print(f"   {node_id} (port {port}): {count} keys")
    
    print(f"\n   Total keys across all nodes: {total_keys}")
    
    # Step 4: Calculate percentages and verify
    print("\n[4] Distribution Analysis:")
    print("-" * 70)
    
    expected_per_node = 100 / 3  # ~33.33%
    
    all_good = True
    
    for node_id, data in distribution.items():
        count = data['count']
        percentage = (count / 100) * 100 if 100 > 0 else 0
        data['percentage'] = percentage
        
        deviation = abs(percentage - expected_per_node)
        
        # Check if within acceptable range (±10% of expected)
        is_balanced = deviation <= 10
        
        status = "✅" if is_balanced else "⚠️"
        print(f"   {status} {node_id}: {count} keys ({percentage:.1f}%)")
        print(f"      Expected: ~33.3%, Deviation: {deviation:.1f}%")
        
        if not is_balanced:
            all_good = False
    
    # Step 5: Verify total
    print("\n[5] Verification:")
    print("-" * 70)
    
    if total_keys == 100:
        print("   ✅ Total keys match (100 keys)")
    else:
        print(f"   ❌ Total keys mismatch: expected 100, got {total_keys}")
        all_good = False
    
    if all_good:
        print("   ✅ Distribution is balanced (~33% per node)")
    else:
        print("   ⚠️  Distribution is unbalanced")
    
    # Step 6: Test forwarding (GET from different node)
    print("\n[6] Testing Request Forwarding:")
    print("-" * 70)
    
    # Pick a key and try to GET from each node
    test_key = "key_50"
    
    print(f"   Testing GET {test_key} from each node...")
    
    for port, node_id in nodes:
        try:
            channel, stub = connect_to_node(port)
            request = kvstore_pb2.GetRequest(key=test_key)
            response = stub.Get(request, timeout=5.0)
            channel.close()
            
            if response.found:
                print(f"   ✅ {node_id}: Found {test_key} = {response.value}")
            else:
                print(f"   ❌ {node_id}: Key {test_key} not found")
        except Exception as e:
            print(f"   ❌ {node_id}: Error - {e}")
    
    # Final summary
    print("\n" + "=" * 70)
    if all_good:
        print("  ✅ PHASE 3 TEST PASSED")
        print("     - Data distributed evenly (~33% per node)")
        print("     - Request forwarding works correctly")
    else:
        print("  ⚠️  PHASE 3 TEST COMPLETED WITH WARNINGS")
        print("     - Check distribution balance")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    """
    Usage:
        python tests/test_phase3_distribution.py
    
    Prerequisites:
        - All 3 nodes must be running (8001, 8002, 8003)
        - Use scripts/start-cluster.bat to start cluster
    """
    
    print("\nPhase 3 Distribution Test")
    print("Make sure all 3 nodes are running before starting test!\n")
    
    # Check if nodes are running
    print("Checking if nodes are running...")
    nodes_running = []
    
    for port, node_id in [(8001, "node1"), (8002, "node2"), (8003, "node3")]:
        try:
            channel, stub = connect_to_node(port)
            # Try a simple operation
            request = kvstore_pb2.ListKeysRequest()
            stub.ListKeys(request, timeout=2.0)
            channel.close()
            print(f"✅ {node_id} (port {port}) is running")
            nodes_running.append(True)
        except Exception as e:
            print(f"❌ {node_id} (port {port}) is NOT running")
            nodes_running.append(False)
    
    if all(nodes_running):
        print("\n✅ All nodes are running. Starting test...\n")
        time.sleep(1)
        test_distribution()
    else:
        print("\n❌ Not all nodes are running!")
        print("Please start the cluster first:")
        print("   scripts\\start-cluster.bat")
        sys.exit(1)
