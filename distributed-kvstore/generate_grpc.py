# gRPC code generation script
# TODO: Code here
import subprocess # thư viện chạy lệnh teminal từ python
import sys # thư viện hệ thống
import os # thư viện làm việc với file 

#Phần 1: định nghĩa đường dẫn 
# Lấy thư mục chứa file generate_grpc.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn tuyệt đối
PROTO_DIR = os.path.join(BASE_DIR, "src", "proto")
PROTO_FILE = os.path.join(PROTO_DIR, "kvstore.proto")
OUTPUT_DIR = os.path.join(BASE_DIR, "src")



#Phần 2: kiểm tra file .proto tồn tại

if not os.path.exists(PROTO_FILE):
    # nếu file không tồn tại thì in lỗi và thoát
    print(f"[ERROR] Proto file not found: {PROTO_FILE}")
    print(f"[ERROR] Current working directory: {os.getcwd()}")
    print(f"[ERROR] Absolute path:{os.path.abspath(PROTO_FILE)}")
    sys.exit(1) # thoát chương trình với mã lỗi 1
print(f"[OK] Proto file found at {PROTO_FILE}")

#Phần 3: tạo lệnh Protoc compiler


print("[*] Building protoc command ...")
# Lệnh protoc dưới dạng list (subprocess yêu cầu list, không string)
# - "python", "-m", "grpc_tools.protoc": Chạy protoc qua Python module
#   (không cần cài protoc riêng nếu có grpcio-tools)
# - "--proto_path=...": Cho protoc biết đâu là thư mục .proto
# - "--python_out=...": Output messages (kvstore_pb2.py) vào thư mục
# - "--grpc_python_out=...": Output service stubs (kvstore_pb2_grpc.py) vào thư mục
# - PROTO_FILE: File input (kvstore.proto)
command = [
    "python",
    "-m",
    "grpc_tools.protoc",
    f"--proto_path={BASE_DIR}", # thư mục root để tìm proto
    f"--python_out={BASE_DIR}", # output vào root
    f"--grpc_python_out={BASE_DIR}", # output vào root
    "src/proto/kvstore.proto", # path relative từ root
]
print(f"[OK] Command: {' '.join(command)}")

#phần 4: chạy protoc compiler

print("[*] Running protoc compiler...")
print("-"*60)
try:
   # Chạy lệnh protoc
    # - capture_output=True: Lưu stdout/stderr để in sau
    # - text=True: Trả về string thay vì bytes
    # - check=True: Raise exception nếu exit code != 0 (lỗi)
    
    result = subprocess.run(
        command,
        capture_output= True,
        text = True,
        check = True
    )
    # nếu chạy thành công thì in thông báo
    if result.stdout:
        print(result.stdout)
    else:
        print("[OK] gRPC code generation completed successfully(no out put).")
except subprocess.CalledProcessError as e:
    # nếu chạy lỗi thì in lỗi
    print("[ERROR] gRPC code generation failed.")
    print(f"[ERROR] Exit Code: {e.returncode}")
    print(f"[ERROR] Stdout: {e.stdout}")
    print(f"[ERROR] Stderr: {e.stderr}")
    sys.exit(1)
print("-"*60)

#phần 5: verify files generated

print("[*] Verifying generated files...")
pb2_file = os.path.join(OUTPUT_DIR, 'kvstore_pb2.py')
pb2_grpc_file = os.path.join(OUTPUT_DIR, 'kvstore_pb2_grpc.py')

success = True
# Kiểm tra kvstore_pb2.py tồn tại
if os.path.exists(pb2_file):
    file_size = os.path.getsize(pb2_file)
    print(f"[OK] {pb2_file} generated ({file_size} bytes)")
else:
    print(f"[ERROR] {pb2_file} NOT found!")
    success = False

# Kiểm tra kvstore_pb2_grpc.py tồn tại
if os.path.exists(pb2_grpc_file):
    file_size = os.path.getsize(pb2_grpc_file)
    print(f"[OK] {pb2_grpc_file} generated ({file_size} bytes)")
else:
    print(f"[ERROR] {pb2_grpc_file} NOT found!")
    success = False

# test 

print("[*] testing imports ...")
try:
    # thử import 2 file vừa tạo
    sys.path.insert(0, OUTPUT_DIR)  # Thêm src/ vào đầu sys.path
    import kvstore_pb2  # Bây giờ Python tìm thấy file trong src/
    print("[OK] kvstore_pb2 imported successfully")
    
    import kvstore_pb2_grpc
    print("[OK] kvstore_pb2_grpc imported successfully")
    

except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    success = False
# thoát
print("\n" + "=" * 60)

if success:
    print("[SUCCESS] gRPC code generated successfully!")
    print(f"[INFO] Generated files:")
    print(f"  - {pb2_file}")
    print(f"  - {pb2_grpc_file}")
    print(f"[INFO] You can now use these in server.py and client.py")
    print("=" * 60)
    sys.exit(0)  # Exit code 0 = thành công
else:
    print("[FAILURE] Some checks failed. See errors above.")
    print("=" * 60)
    sys.exit(1)  # Exit code 1 = thất bại
