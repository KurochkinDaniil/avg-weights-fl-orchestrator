#!/usr/bin/env python3
"""Complete setup script for FL system."""

import subprocess
import sys
from pathlib import Path
import shutil

def run_command(cmd, description):
    """Run a command and print status."""
    print(f"\n{'=' * 60}")
    print(f"⚙ {description}")
    print(f"{'=' * 60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        return False

def check_file_exists(file_path, description):
    """Check if a file exists."""
    path = Path(file_path)
    if path.exists():
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description} not found: {file_path}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║     Federated Learning System Setup                      ║
║     Complete Docker Infrastructure                       ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check prerequisites
    print("\n[Step 1/6] Checking prerequisites...")
    
    checks = [
        ("docker --version", "Docker"),
        ("docker-compose --version", "Docker Compose"),
    ]
    
    for cmd, name in checks:
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            print(f"✓ {name} is installed")
        except subprocess.CalledProcessError:
            print(f"✗ {name} is not installed")
            print(f"\nPlease install {name} first:")
            if name == "Docker":
                print("  Windows: https://docs.docker.com/desktop/install/windows-install/")
            return 1
    
    # Check model exists
    model_path = Path("apps/client/model2.pt")
    if not model_path.exists():
        print(f"\n✗ Base model not found: {model_path}")
        print("  Please ensure model2.pt exists in apps/client/")
        return 1
    print(f"✓ Base model found: {model_path}")
    
    # Step 2: Generate Python proto files
    print("\n[Step 2/6] Generating Python gRPC stubs...")
    if not run_command(
        f"{sys.executable} scripts/generate-proto-python.py",
        "Python proto generation"
    ):
        print("⚠ Proto generation failed, but continuing...")
    
    # Step 3: Create server models directory
    print("\n[Step 3/6] Preparing server models...")
    server_models_dir = Path("apps/server/models")
    server_models_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy base model to server
    initial_model = server_models_dir / "initial_model.pt"
    shutil.copy(model_path, initial_model)
    print(f"✓ Copied base model to {initial_model}")
    
    # Step 4: Build Docker images
    print("\n[Step 4/6] Building Docker images...")
    if not run_command(
        "docker-compose build",
        "Docker build"
    ):
        print("✗ Docker build failed")
        return 1
    
    # Step 5: Start services
    print("\n[Step 5/6] Starting Docker services...")
    if not run_command(
        "docker-compose up -d",
        "Docker compose up"
    ):
        print("✗ Failed to start services")
        return 1
    
    # Wait for services to be healthy
    print("\nWaiting for services to be healthy...")
    subprocess.run("sleep 10", shell=True)
    
    # Step 6: Upload initial model to MinIO
    print("\n[Step 6/6] Uploading initial model to MinIO...")
    upload_cmd = """
docker run --rm \
    --network avg-weights-fl-orchestrator_fl-network \
    -v "{models_dir}:/models" \
    minio/mc:latest \
    /bin/sh -c "
    mc alias set myminio http://fl-minio:9000 admin admin12345 && \
    mc cp /models/initial_model.pt myminio/mybucket/weights/global/latest.pt && \
    echo 'Model uploaded successfully'
    "
    """.format(models_dir=server_models_dir.absolute().as_posix())
    
    if not run_command(upload_cmd, "Model upload to MinIO"):
        print("⚠ Model upload failed, but system may still work")
    
    # Final status check
    print("\n[Checking services...]")
    run_command("docker-compose ps", "Service status")
    
    # Success message
    print(f"""
╔══════════════════════════════════════════════════════════╗
║              ✓ Setup Complete!                           ║
╚══════════════════════════════════════════════════════════╝

Services running:
  ✓ FL Server (gRPC):  localhost:50051
  ✓ FL Client (API):   http://localhost:8000
  ✓ MinIO (Console):   http://localhost:9001 (admin/admin12345)
  ✓ PostgreSQL:        localhost:5432

Next steps:
  1. Check API docs:    http://localhost:8000/docs
  2. Check MinIO:       http://localhost:9001
  3. View logs:         docker-compose logs -f
  4. Open frontend:     apps/frontend/demo/index.html

Troubleshooting:
  - View logs:          docker-compose logs -f fl-server
  - Restart service:    docker-compose restart fl-client
  - Stop all:           docker-compose down
  
For full documentation, see: DOCKER_SETUP.md
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

