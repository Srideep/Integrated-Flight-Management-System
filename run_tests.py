
#!/usr/bin/env python3
"""
FMS Test Runner - Comprehensive testing for the FMS system
"""

import sys
import os
import subprocess
from pathlib import Path

def run_test_file(test_file):
    """Run a single test file and return success status"""
    print(f"\n{'='*60}")
    print(f"Running {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return False

def main():
    """Run all tests in sequence"""
    print("FMS Integrated System - Test Suite")
    print("=" * 60)
    
    # Test files in order
    test_files = [
        "tests/test_nav_database.py",
        "tests/test_flight_planning.py"
    ]
    
    results = {}
    
    # Run each test
    for test_file in test_files:
        if os.path.exists(test_file):
            results[test_file] = run_test_file(test_file)
        else:
            print(f"Warning: Test file {test_file} not found")
            results[test_file] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    all_passed = True
    for test_file, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test_file}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
