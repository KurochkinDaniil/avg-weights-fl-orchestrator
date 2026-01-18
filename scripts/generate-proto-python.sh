#!/bin/bash
# Generate Python proto files from Go proto definition

set -e

echo "====================================="
echo "Generating Python gRPC stubs"
echo "====================================="

# Check if grpcio-tools is installed
if ! python -c "import grpc_tools" 2>/dev/null; then
    echo "Installing grpcio-tools..."
    pip install grpcio-tools
fi

# Create output directory
mkdir -p apps/client/grpc_client

# Generate Python proto files
python -m grpc_tools.protoc \
    -I apps/server/api \
    --python_out=apps/client/grpc_client \
    --grpc_python_out=apps/client/grpc_client \
    apps/server/api/serverside.proto

echo "✓ Generated Python proto files in apps/client/grpc_client/"

# Fix imports in generated files (Python relative imports)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' 's/import serverside_pb2/from . import serverside_pb2/g' apps/client/grpc_client/serverside_pb2_grpc.py
else
    # Linux/Windows Git Bash
    sed -i 's/import serverside_pb2/from . import serverside_pb2/g' apps/client/grpc_client/serverside_pb2_grpc.py
fi

echo "✓ Fixed imports"

# Create __init__.py if not exists
touch apps/client/grpc_client/__init__.py

echo ""
echo "====================================="
echo "✓ Proto generation complete!"
echo "====================================="
echo ""
echo "Generated files:"
echo "  - apps/client/grpc_client/serverside_pb2.py"
echo "  - apps/client/grpc_client/serverside_pb2_grpc.py"
echo ""

