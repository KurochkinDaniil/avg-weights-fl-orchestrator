#!/bin/bash
# Initialize server with base model from client

set -e

echo "====================================="
echo "Initializing FL Server Base Model"
echo "====================================="

# Check if client model exists
CLIENT_MODEL="apps/client/model2.pt"
if [ ! -f "$CLIENT_MODEL" ]; then
    echo "ERROR: Client model not found at $CLIENT_MODEL"
    echo "Please ensure model2.pt exists in apps/client/"
    exit 1
fi

echo "✓ Found client model: $CLIENT_MODEL"

# Create server models directory
mkdir -p apps/server/models

# Copy model to server
cp "$CLIENT_MODEL" apps/server/models/initial_model.pt

echo "✓ Copied model to apps/server/models/initial_model.pt"

# Upload to MinIO (if Docker is running)
if docker ps | grep -q fl-minio; then
    echo "✓ MinIO container is running, uploading model..."
    
    # Use MinIO client in Docker
    docker run --rm \
        --network avg-weights-fl-orchestrator_fl-network \
        -v "$(pwd)/apps/server/models:/models" \
        minio/mc:latest \
        /bin/sh -c "
        mc alias set myminio http://fl-minio:9000 admin admin12345;
        mc cp /models/initial_model.pt myminio/fl-models/weights/global/latest.pt;
        echo '✓ Model uploaded to MinIO';
        "
else
    echo "⚠ MinIO not running. Model will be uploaded when you start Docker."
    echo "  Run: docker-compose up -d"
fi

echo ""
echo "====================================="
echo "✓ Server initialized successfully!"
echo "====================================="

