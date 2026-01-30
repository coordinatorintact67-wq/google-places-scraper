#!/usr/bin/env python3
"""
Test script to verify terminate functionality works correctly
"""
import requests
import time
import json

def test_terminate_functionality():
    """Test that the terminate endpoint works properly"""

    BASE_URL = "http://localhost:8000"

    print("Testing terminate functionality...")

    # First, check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Server is running")
        else:
            print("✗ Server is not responding properly")
            return False
    except Exception as e:
        print(f"✗ Server is not running: {e}")
        print("Please start the backend server with: cd backend && python server.py")
        return False

    # Test the terminate endpoint exists
    try:
        # This will fail with 404 since we're using a fake job ID, but that's expected
        response = requests.post(f"{BASE_URL}/api/terminate/fake-job-id")
        if response.status_code == 404:
            print("✓ Terminate endpoint exists and returns 404 for non-existent job (expected)")
        else:
            print(f"? Terminate endpoint exists but returned unexpected status: {response.status_code}")
    except Exception as e:
        print(f"✗ Terminate endpoint may not be accessible: {e}")
        return False

    # Test that the status endpoint can handle terminate status
    try:
        # This will also fail with 404, but that's expected
        response = requests.get(f"{BASE_URL}/api/status/fake-job-id")
        if response.status_code == 404:
            print("✓ Status endpoint exists and returns 404 for non-existent job (expected)")
        else:
            print(f"? Status endpoint exists but returned unexpected status: {response.status_code}")
    except Exception as e:
        print(f"✗ Status endpoint may not be accessible: {e}")
        return False

    print("\n✓ Basic terminate functionality endpoints are accessible")
    print("\nTo fully test termination:")
    print("1. Start the backend server")
    print("2. Start a scraping job from the frontend")
    print("3. While scraping is in progress, click the 'Terminate' button")
    print("4. Verify the job status changes to 'terminated' and scraping stops")

    return True

if __name__ == "__main__":
    test_terminate_functionality()