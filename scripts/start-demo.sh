#!/bin/bash
# Start FL Demo with 2 clients

set -e

echo "=================================================="
echo "  FL Demo: Starting 2-Client System"
echo "=================================================="
echo ""

# Step 1: Build
echo "[Step 1/4] Building Docker images..."
docker-compose build

# Step 2: Upload model
echo ""
echo "[Step 2/4] Uploading initial model to MinIO..."
python scripts/upload-model-to-minio.py

# Step 3: Start services
echo ""
echo "[Step 3/4] Starting all services..."
docker-compose up -d

# Step 4: Wait for services
echo ""
echo "[Step 4/4] Waiting for services to be ready..."
sleep 15

# Check status
echo ""
echo "=================================================="
echo "  Services Status:"
echo "=================================================="
docker-compose ps

echo ""
echo "=================================================="
echo "  FL Demo System Ready!"
echo "=================================================="
echo ""
echo "Access points:"
echo "  - Client 1 Frontend: apps/frontend/demo1/index.html"
echo "  - Client 2 Frontend: apps/frontend/demo2/index.html"
echo "  - Client 1 API: http://localhost:8000/docs"
echo "  - Client 2 API: http://localhost:8001/docs"
echo "  - MinIO Console: http://localhost:9001 (admin/admin12345)"
echo ""
echo "Monitor logs:"
echo "  docker-compose logs -f fl-server    # Server logs"
echo "  docker-compose logs -f fl-client-1  # Client 1 logs"
echo "  docker-compose logs -f fl-client-2  # Client 2 logs"
echo ""
echo "See DEMO_GUIDE.md for full demonstration instructions"
echo "=================================================="

