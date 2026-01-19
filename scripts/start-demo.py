#!/usr/bin/env python3
"""Start FL Demo with 2 clients."""

import subprocess
import sys
import time

def run_command(cmd, description):
    """Run a command and print status."""
    print(f"\n{'=' * 60}")
    print(f"[RUNNING] {description}")
    print(f"{'=' * 60}")
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"[OK] {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        return False

def main():
    print("""
==================================================
  FL Demo: Starting 2-Client System
==================================================
    """)
    
    # Step 1: Build
    if not run_command("docker-compose build", "Building Docker images"):
        return 1
    
    # Step 2: Upload model
    if not run_command(f"{sys.executable} scripts/upload-model-to-minio.py", "Uploading initial model"):
        print("[WARNING] Model upload failed, but continuing...")
    
    # Step 3: Start services
    if not run_command("docker-compose up -d", "Starting all services"):
        return 1
    
    # Step 4: Wait
    print("\n[Step 4/4] Waiting for services to be ready...")
    time.sleep(15)
    
    # Check status
    print("\n" + "=" * 60)
    print("  Services Status:")
    print("=" * 60)
    subprocess.run("docker-compose ps", shell=True)
    
    print("""
==================================================
  FL Demo System Ready!
==================================================

Access points:
  - Client 1 Frontend: apps/frontend/demo1/index.html
  - Client 2 Frontend: apps/frontend/demo2/index.html
  - Client 1 API: http://localhost:8000/docs
  - Client 2 API: http://localhost:8001/docs
  - MinIO Console: http://localhost:9001 (admin/admin12345)

Monitor logs:
  docker-compose logs -f fl-server    # Server logs
  docker-compose logs -f fl-client-1  # Client 1 logs
  docker-compose logs -f fl-client-2  # Client 2 logs

See DEMO_GUIDE.md for full demonstration instructions
==================================================
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

