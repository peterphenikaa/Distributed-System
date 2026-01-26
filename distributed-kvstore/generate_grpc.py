# Import subprocess để chạy lệnh shell từ Python
import subprocess
# Import sys để lấy Python executable path
import sys
# Import os để xử lý file paths
import os

# In thông báo bắt đầu
print("🚀 Starting gRPC code generation...")

# Lấy đường dẫn thư mục hiện tại (distributed-kvstore/)
project_root = os.path.dirname(os.path.abspath(__file__))
print(f"📂 Project root: {project_root}")

# Đường dẫn đến file proto
proto_file = os.path.join(project_root, "src", "proto", "kvstore.proto")
print(f"📄 Proto file: {proto_file}")

# Kiểm tra file proto có tồn tại không
if not os.path.exists(proto_file):
    print(f"❌ Error: Proto file not found at {proto_file}")
    sys.exit(1)  # Exit với error code 1

# Đường dẫn thư mục output (project root)
# Protoc sẽ tự tạo structure src/proto/ dựa vào proto file path
output_dir = project_root
print(f"📁 Output directory: {output_dir}")

# Tạo lệnh để chạy protoc compiler
# -m grpc_tools.protoc: Chạy protoc từ Python module
# -I.: Include path là thư mục hiện tại
# --python_out: Generate Python message classes
# --grpc_python_out: Generate Python gRPC service classes
# Cuối cùng là đường dẫn file proto
command = [
    sys.executable,  # Python executable (python.exe)
    "-m", "grpc_tools.protoc",  # Module protoc
    f"-I{project_root}",  # Include path
    f"--python_out={output_dir}",  # Output cho messages
    f"--grpc_python_out={output_dir}",  # Output cho gRPC services
    proto_file  # File proto cần compile
]

# In ra lệnh sẽ chạy (để debug)
print(f"\n🔧 Running command:")
print(" ".join(command))

# Chạy lệnh và capture output
try:
    result = subprocess.run(
        command,
        check=True,  # Raise exception nếu command fail
        capture_output=True,  # Capture stdout và stderr
        text=True  # Return string thay vì bytes
    )
    
    # In ra output nếu có
    if result.stdout:
        print(f"\n📝 Output:\n{result.stdout}")
    
    print("\n✅ gRPC code generation successful!")
    
    # Kiểm tra files được generate
    pb2_file = os.path.join(output_dir, "proto", "kvstore_pb2.py")
    grpc_file = os.path.join(output_dir, "proto", "kvstore_pb2_grpc.py")
    
    if os.path.exists(pb2_file):
        print(f"✓ Generated: {pb2_file}")
    else:
        print(f"⚠ Warning: {pb2_file} not found")
        
    if os.path.exists(grpc_file):
        print(f"✓ Generated: {grpc_file}")
    else:
        print(f"⚠ Warning: {grpc_file} not found")
    
except subprocess.CalledProcessError as e:
    # Lỗi khi chạy command
    print(f"\n❌ Error during generation:")
    print(f"Exit code: {e.returncode}")
    if e.stderr:
        print(f"Error message:\n{e.stderr}")
    sys.exit(1)
    
except Exception as e:
    # Lỗi khác
    print(f"\n❌ Unexpected error: {str(e)}")
    sys.exit(1)

print("\n🎉 All done! You can now use the generated files.")