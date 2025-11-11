#!/usr/bin/env python3
"""Test script to verify container cleanup in tests."""

import os
import subprocess
import sys

# Set test environment
os.environ["GRASP_API_KEY"] = "api-server-test"
os.environ["GRASP_BASE_URL"] = "http://localhost:3000"

def run_single_test():
    """Run a single test that creates a container."""
    print("🧪 Running single test to check cleanup...")

    # Run just one test that creates a container
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_client.py::TestGraspClient::test_create_container",
        "-v", "-s"  # Verbose and show print statements
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print("\n📋 Test Output:")
    print(result.stdout)

    if result.stderr:
        print("\n⚠️ Errors:")
        print(result.stderr)

    if "✓ Cleaned up container" in result.stdout or "shutdown" in result.stdout.lower():
        print("\n✅ Container cleanup detected in output!")
    else:
        print("\n⚠️ No explicit cleanup message found (but container may still be cleaned up)")

    return result.returncode == 0

if __name__ == "__main__":
    print("=" * 50)
    print("Container Cleanup Test")
    print("=" * 50)

    success = run_single_test()

    if success:
        print("\n✅ Test passed - check E2B console to verify no orphaned containers")
    else:
        print("\n❌ Test failed - there may be issues with the API server")

    print("\n💡 Tips:")
    print("  1. Check E2B console for any remaining containers")
    print("  2. Each test should create and destroy its own container")
    print("  3. Tests run sequentially (not in parallel)")

    sys.exit(0 if success else 1)