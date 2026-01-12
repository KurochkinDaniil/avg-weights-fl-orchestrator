#!/bin/bash
# Quick start script for FL project

set -e

echo "🚀 Starting Federated Learning Swipe Keyboard"
echo ""

# Check if we're in the right directory
if [ ! -d "apps/client" ] || [ ! -d "apps/frontend" ]; then
    echo "❌ Error: Run this script from the fl/ directory"
    exit 1
fi

# Start backend
echo "📦 Starting Python backend..."
cd apps/client

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch .deps_installed
fi

# Generate proto files if needed
if [ ! -f "grpc_client/serverside_pb2.py" ]; then
    echo "Generating proto files..."
    make proto
fi

# Start API in background
echo "Starting API server on http://localhost:8000"
./run.sh &
BACKEND_PID=$!

cd ../..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Build frontend if needed
echo ""
echo "🎨 Checking frontend..."
cd apps/frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install --legacy-peer-deps
fi

if [ ! -f "build/index.js" ]; then
    echo "Building frontend..."
    npm run build
fi

cd ../..

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "   1. Open: apps/frontend/demo/index.html"
echo "   2. Make a swipe gesture on the keyboard"
echo "   3. Watch the predicted word appear!"
echo ""
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the backend"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping backend...'; kill $BACKEND_PID 2>/dev/null || true; exit 0" INT

wait $BACKEND_PID
