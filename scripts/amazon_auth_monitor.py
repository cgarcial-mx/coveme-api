#!/usr/bin/env python3
"""
Amazon SP API Authentication Monitor

This script runs the Amazon SP API authentication test every minute for 90 minutes (1.5 hours).
It continuously monitors the authentication status and logs results to a file.

Usage:
    python scripts/amazon_auth_monitor.py

Requirements:
    - Django project must be set up
    - python-amazon-sp-api package must be installed
    - Virtual environment must be activated
"""

import os
import sys
import time
import subprocess
import datetime
from pathlib import Path

# Add the Django project to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

def setup_django():
    """Initialize Django settings"""
    try:
        import django
        django.setup()
        print("✅ Django initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Django: {e}")
        sys.exit(1)

def run_auth_test():
    """Run the Amazon API authentication test"""
    try:
        # Run the Django management command
        result = subprocess.run([
            'python', 'manage.py', 'test_amazon_api'
        ], 
        capture_output=True, 
        text=True, 
        cwd=project_root,
        timeout=60  # 60 second timeout
        )
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Test timed out after 60 seconds"
    except Exception as e:
        return False, str(e)

def log_result(timestamp, success, output, log_file):
    """Log the test result to file"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    log_entry = f"""
{'='*80}
Timestamp: {timestamp}
Status: {status}
{'='*80}
Output:
{output}
{'='*80}
"""
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def main():
    """Main function to run the authentication monitor"""
    print("🔐 Amazon SP API Authentication Monitor")
    print("=" * 50)
    print("This script will run authentication tests every minute for 90 minutes")
    print("Results will be logged to 'amazon_auth_monitor.log'")
    print("=" * 50)
    
    # Setup Django
    setup_django()
    
    # Create log file
    log_file = project_root / 'amazon_auth_monitor.log'
    
    # Clear previous log
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Amazon SP API Authentication Monitor Log\n")
        f.write(f"Started at: {datetime.datetime.now()}\n")
        f.write(f"{'='*80}\n\n")
    
    # Configuration
    total_minutes = 90  # 1.5 hours
    interval_seconds = 60  # 1 minute
    
    print(f"📊 Will run {total_minutes} tests with {interval_seconds} second intervals")
    print(f"📝 Log file: {log_file}")
    print(f"⏰ Total duration: {total_minutes} minutes")
    print()
    
    # Calculate end time
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(minutes=total_minutes)
    
    print(f"🚀 Starting at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏹️  Will stop at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Statistics
    successful_tests = 0
    failed_tests = 0
    
    try:
        for test_number in range(1, total_minutes + 1):
            current_time = datetime.datetime.now()
            
            # Check if we've reached the end time
            if current_time >= end_time:
                print(f"⏰ Reached end time. Stopping monitor.")
                break
            
            print(f"🔄 Test #{test_number}/{total_minutes} - {current_time.strftime('%H:%M:%S')}")
            
            # Run the authentication test
            success, output = run_auth_test()
            
            # Update statistics
            if success:
                successful_tests += 1
                print(f"✅ Test #{test_number} PASSED")
            else:
                failed_tests += 1
                print(f"❌ Test #{test_number} FAILED")
                print(f"   Error: {output[:200]}...")  # Show first 200 chars of error
            
            # Log the result
            log_result(current_time, success, output, log_file)
            
            # Show progress
            success_rate = (successful_tests / test_number) * 100
            print(f"📊 Progress: {test_number}/{total_minutes} | Success Rate: {success_rate:.1f}%")
            print(f"   ✅ Success: {successful_tests} | ❌ Failed: {failed_tests}")
            
            # Wait for next test (except for the last test)
            if test_number < total_minutes:
                print(f"⏳ Waiting {interval_seconds} seconds until next test...")
                print("-" * 50)
                time.sleep(interval_seconds)
    
    except KeyboardInterrupt:
        print("\n⚠️  Monitor interrupted by user")
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 FINAL SUMMARY")
    print("=" * 50)
    print(f"Total tests run: {test_number}")
    print(f"Successful tests: {successful_tests}")
    print(f"Failed tests: {failed_tests}")
    print(f"Success rate: {(successful_tests / test_number) * 100:.1f}%")
    print(f"Log file: {log_file}")
    print(f"Monitor completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

if __name__ == "__main__":
    main() 