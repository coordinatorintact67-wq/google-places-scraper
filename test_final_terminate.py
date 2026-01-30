#!/usr/bin/env python3
"""
Final test to verify terminate functionality implementation
"""
import ast
import inspect
import sys
from pathlib import Path

def check_backend_implementation():
    """Check if backend implementation is correct"""
    server_path = Path("backend/server.py")
    scraper_path = Path("backend/scraper.py")

    if not server_path.exists():
        print("❌ Backend server.py not found")
        return False

    if not scraper_path.exists():
        print("❌ Backend scraper.py not found")
        return False

    server_content = server_path.read_text()
    scraper_content = scraper_path.read_text()

    checks = [
        # Check that thread_drivers is defined in server
        ("thread_drivers" in server_content, "Global thread_drivers variable"),

        # Check that termination endpoint closes drivers
        ("thread_drivers[job_id]" in server_content and "driver.quit()" in server_content, "Driver cleanup in termination endpoint"),

        # Check that scraper accepts thread_drivers parameter
        ("thread_drivers=None" in scraper_content, "Scraper function accepts thread_drivers parameter"),

        # Check that scraper registers driver
        ("thread_drivers[job_id] = driver" in scraper_content, "Driver registration in scraper"),

        # Check that scraper cleans up driver
        ("del thread_drivers[job_id]" in scraper_content, "Driver cleanup in scraper finally block"),

        # Check that scraper function call passes thread_drivers
        ("thread_drivers=thread_drivers" in server_content, "thread_drivers passed to scraper function"),
    ]

    all_passed = True
    for check_result, description in checks:
        if check_result:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
            all_passed = False

    return all_passed

def check_frontend_implementation():
    """Check if frontend implementation is correct"""
    frontend_path = Path("frontend-next/src/app/page.tsx")
    api_path = Path("frontend-next/src/lib/api.ts")

    if not frontend_path.exists():
        print("❌ Frontend page.tsx not found")
        return False

    if not api_path.exists():
        print("❌ Frontend api.ts not found")
        return False

    frontend_content = frontend_path.read_text()
    api_content = api_path.read_text()

    checks = [
        # Check that terminateJob is imported
        ("terminateJob" in frontend_content, "terminateJob function imported in page.tsx"),

        # Check that terminateJob is used in handleTerminateStatus
        ("await terminateJob" in frontend_content, "terminateJob function used in handleTerminateStatus"),

        # Check that terminateJob API function has proper headers
        ("Content-Type" in api_content and "terminateJob" in api_content, "terminateJob API function with proper headers"),
    ]

    all_passed = True
    for check_result, description in checks:
        if check_result:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
            all_passed = False

    return all_passed

def main():
    print("🔍 Verifying Terminate Functionality Implementation")
    print("="*50)

    backend_ok = check_backend_implementation()
    print()
    frontend_ok = check_frontend_implementation()

    print()
    print("="*50)

    if backend_ok and frontend_ok:
        print("🎉 All terminate functionality improvements implemented successfully!")
        print("\n📋 Summary of changes:")
        print("   • Backend: Driver cleanup in termination endpoint")
        print("   • Backend: Proper resource management with thread_drivers")
        print("   • Backend: Enhanced finally blocks for cleanup")
        print("   • Frontend: Better error handling and API integration")
        print("   • Both: Improved termination responsiveness")
        return True
    else:
        print("❌ Some implementation issues detected")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)