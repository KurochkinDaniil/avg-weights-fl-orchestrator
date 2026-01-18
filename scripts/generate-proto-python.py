#!/usr/bin/env python3
"""Generate Python gRPC stubs from proto files."""

import subprocess
import sys
from pathlib import Path

def main():
    print("=" * 50)
    print("Generating Python gRPC stubs")
    print("=" * 50)
    
    # Check if grpcio-tools is installed
    try:
        import grpc_tools
    except ImportError:
        print("Installing grpcio-tools...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "grpcio-tools"])
    
    # Paths
    proto_file = Path("apps/server/api/serverside.proto")
    proto_dir = proto_file.parent
    output_dir = Path("apps/client/grpc_client")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate Python proto files
    print(f"\nGenerating from {proto_file}...")
    cmd = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"-I{proto_dir}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        str(proto_file)
    ]
    
    subprocess.check_call(cmd)
    print(f"[OK] Generated Python proto files in {output_dir}/")
    
    # Fix imports in generated files
    grpc_file = output_dir / "serverside_pb2_grpc.py"
    if grpc_file.exists():
        content = grpc_file.read_text(encoding='utf-8')
        content = content.replace(
            "import serverside_pb2",
            "from . import serverside_pb2"
        )
        grpc_file.write_text(content, encoding='utf-8')
        print("[OK] Fixed imports")
    
    # Create __init__.py
    init_file = output_dir / "__init__.py"
    init_file.touch()
    
    print("\n" + "=" * 50)
    print("[OK] Proto generation complete!")
    print("=" * 50)
    print("\nGenerated files:")
    print(f"  - {output_dir}/serverside_pb2.py")
    print(f"  - {output_dir}/serverside_pb2_grpc.py")
    print()

if __name__ == "__main__":
    main()

