#!/usr/bin/env python3
"""
Quick local test to verify bot server can start and respond to basic requests
"""

import subprocess
import time
import requests
import sys
from pathlib import Path

def wait_for_server(max_tries=30):
    """Wait for server to be ready"""
    for i in range(max_tries):
        try:
            resp = requests.get("http://localhost:8000/v1/healthz", timeout=2)
            if resp.status_code == 200:
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def main():
    print("Starting Vera AI Bot Server...")
    print("=" * 60)
    
    # Start server in background
    proc = subprocess.Popen(
        [sys.executable, "bot_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("Waiting for server to be ready...")
    if not wait_for_server():
        print("❌ Server failed to start!")
        proc.kill()
        return False
    
    print("✓ Server is ready!")
    
    # Test basic endpoints
    try:
        print("\nTesting /v1/healthz...")
        resp = requests.get("http://localhost:8000/v1/healthz")
        print(f"✓ Status {resp.status_code}: {resp.json()}")
        
        print("\nTesting /v1/metadata...")
        resp = requests.get("http://localhost:8000/v1/metadata")
        print(f"✓ Status {resp.status_code}: {resp.json()['team_name']}, {resp.json()['model']}")
        
        print("\n" + "=" * 60)
        print("Bot server is working! ✓")
        print("=" * 60)
        print("\nServer running on http://localhost:8000")
        print("Press Ctrl+C to stop")
        
        # Keep running
        proc.wait()
    except Exception as e:
        print(f"❌ Error: {e}")
        proc.kill()
        return False
    finally:
        proc.terminate()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
