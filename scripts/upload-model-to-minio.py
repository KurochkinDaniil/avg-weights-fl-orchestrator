#!/usr/bin/env python3
"""Upload initial model to MinIO."""

import subprocess
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("Uploading initial model to MinIO")
    print("=" * 60)
    
    # Check if model exists
    model_path = Path("apps/server/models/initial_model.pt")
    if not model_path.exists():
        print(f"[ERROR] Model not found: {model_path}")
        return 1
    
    # Get absolute path for Docker mount
    abs_model_dir = model_path.parent.absolute()
    
    print(f"\nModel path: {model_path}")
    print(f"Mounting: {abs_model_dir}")
    
    try:
        # Step 1: Set alias
        print("\nStep 1: Setting MinIO alias...")
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "--network", "avg-weights-fl-orchestrator_fl-network",
                "minio/mc:latest",
                "alias", "set", "myminio", "http://fl-minio:9000", "admin", "admin12345"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        
        # Step 2: Copy model
        print("\nStep 2: Copying model to MinIO...")
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "--network", "avg-weights-fl-orchestrator_fl-network",
                "-v", f"{abs_model_dir}:/models",
                "minio/mc:latest",
                "cp", "/models/initial_model.pt", "myminio/mybucket/weights/global/latest.pt"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        
        print("\n[OK] Model uploaded successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Upload failed:")
        print(e.stdout)
        print(e.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())

