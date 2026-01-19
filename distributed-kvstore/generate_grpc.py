"""
Setup script for generating gRPC code from proto files
"""

import os
import sys
from grpc_tools import protoc

def generate_grpc_code():
    """Generate Python code from proto files"""
    
    print("=" * 60)
    print("🔨 Generating gRPC code from proto files...")
    print("=" * 60)
    
    # Proto file location
    proto_file = "src/proto/kvstore.proto"
    proto_dir = "src/proto"
    output_dir = "src"
    
    # Check if proto file exists
    if not os.path.exists(proto_file):
        print(f"❌ Error: Proto file not found: {proto_file}")
        sys.exit(1)
    
    # Generate code
    result = protoc.main([
        'grpc_tools.protoc',
        f'-I{proto_dir}',
        f'--python_out={output_dir}',
        f'--grpc_python_out={output_dir}',
        proto_file
    ])
    
    if result == 0:
        print("✅ Generated files:")
        print(f"   - {output_dir}/kvstore_pb2.py")
        print(f"   - {output_dir}/kvstore_pb2_grpc.py")
        print("=" * 60)
        print("✨ gRPC code generation completed successfully!")
        print("=" * 60)
    else:
        print("❌ Failed to generate gRPC code")
        sys.exit(1)

if __name__ == '__main__':
    generate_grpc_code()
