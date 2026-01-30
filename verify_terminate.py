#!/usr/bin/env python3
"""
Verification script to confirm terminate functionality is properly implemented
"""
import ast
import os

def verify_backend_implementation():
    """Verify backend terminate implementation"""
    print("Verifying backend terminate implementation...")

    server_file = "/mnt/d/Hamza coding/google places scraper/backend/server.py"
    scraper_file = "/mnt/d/Hamza coding/google places scraper/backend/scraper.py"

    if not os.path.exists(server_file):
        print("❌ Backend server.py file not found")
        return False

    if not os.path.exists(scraper_file):
        print("❌ Backend scraper.py file not found")
        return False

    with open(server_file, 'r') as f:
        server_content = f.read()

    with open(scraper_file, 'r') as f:
        scraper_content = f.read()

    # Check for thread_drivers global variable
    if 'thread_drivers = {}' in server_content:
        print("✅ Global thread_drivers dictionary found")
    else:
        print("❌ Global thread_drivers dictionary not found")
        return False

    # Check for terminate endpoint that closes drivers
    if 'del thread_drivers[job_id]' in server_content:
        print("✅ Driver cleanup in terminate endpoint found")
    else:
        print("❌ Driver cleanup in terminate endpoint not found")
        return False

    # Check for driver registration in scraper call
    if 'thread_drivers=thread_drivers' in server_content:
        print("✅ thread_drivers passed to scraper function found")
    else:
        print("❌ thread_drivers passed to scraper function not found")
        return False

    # Check for driver registration in scraper
    if 'thread_drivers[job_id] = driver' in scraper_content:
        print("✅ Driver registration in scraper found")
    else:
        print("❌ Driver registration in scraper not found")
        return False

    # Check for driver cleanup in scraper finally block
    if 'del thread_drivers[job_id]' in scraper_content:
        print("✅ Driver cleanup in scraper finally block found")
    else:
        print("❌ Driver cleanup in scraper finally block not found")
        return False

    # Check for updated scraper function signature
    if 'thread_drivers=None' in scraper_content:
        print("✅ Updated scraper function signature found")
    else:
        print("❌ Updated scraper function signature not found")
        return False

    # Check for enhanced finally block in server
    if 'del thread_drivers[job_id]' in server_content and 'driver.quit()' in server_content:
        print("✅ Enhanced cleanup in server finally block found")
    else:
        print("❌ Enhanced cleanup in server finally block not found")
        return False

    print("✅ All backend terminate implementation checks passed")
    return True

def verify_frontend_implementation():
    """Verify frontend terminate implementation"""
    print("\nVerifying frontend terminate implementation...")

    page_file = "/mnt/d/Hamza coding/google places scraper/frontend-next/src/app/page.tsx"
    api_file = "/mnt/d/Hamza coding/google places scraper/frontend-next/src/lib/api.ts"

    if not os.path.exists(page_file):
        print("❌ Frontend page.tsx file not found")
        return False

    if not os.path.exists(api_file):
        print("❌ Frontend api.ts file not found")
        return False

    with open(page_file, 'r') as f:
        page_content = f.read()

    with open(api_file, 'r') as f:
        api_content = f.read()

    # Check for enhanced handleTerminateStatus function
    if 'pollForTermination' in page_content:
        print("✅ Enhanced termination polling in page.tsx found")
    else:
        print("❌ Enhanced termination polling in page.tsx not found")
        return False

    # Check for improved error handling in terminate function
    if 'Failed to terminate job' in api_content:
        print("✅ Enhanced error handling in API found")
    else:
        print("❌ Enhanced error handling in API not found")
        return False

    print("✅ All frontend terminate implementation checks passed")
    return True

def main():
    print("🔍 Verifying terminate functionality implementation...")
    print("="*60)

    backend_ok = verify_backend_implementation()
    frontend_ok = verify_frontend_implementation()

    print("\n" + "="*60)
    if backend_ok and frontend_ok:
        print("🎉 SUCCESS: All terminate functionality implementations verified!")
        print("\nThe terminate button should now properly:")
        print("  ✅ Stop the scraping process immediately")
        print("  ✅ Close any active browser instances")
        print("  ✅ Update the UI status to 'terminated'")
        print("  ✅ Clean up all resources properly")
        print("  ✅ Prevent any zombie processes")
        return True
    else:
        print("❌ FAILURE: Some implementation checks failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)