#!/usr/bin/env python3
"""
Example script showing how to run gawk tests against pyawk_ai.py
"""

import sys
from pathlib import Path
from extract_tests import GawkTestRunner, get_starter_tests

def main():
    # Path to your Python AWK implementation
    PYGAWK = "./pyawk_ai_fixed.py"
    
    # Path to extracted tests
    TEST_DIR = "./gawk_tests"
    
    # Check if tests have been extracted
    test_dir = Path(TEST_DIR)
    if not test_dir.exists():
        print(f"Error: Test directory '{TEST_DIR}' not found!")
        print("\nFirst extract the tests by running:")
        print("  python3 extract_tests.py extract ../gawk/test ./gawk_tests")
        sys.exit(1)
    
    # Create test runner
    runner = GawkTestRunner(
        pygawk_path=PYGAWK,
        test_dir=test_dir,
        features=[]  # Add implemented features here as you develop
    )
    
    print("="*60)
    print("Running Gawk Test Suite against pyawk_ai.py")
    print("="*60)
    
    # Option 1: Run starter tests (recommended for initial development)
    print("\n1. Running starter tests (18 basic tests)...")
    starter_tests = get_starter_tests()
    runner.run_test_subset(starter_tests)
    
    # Generate report
    runner.generate_report("test_results.json")
    
    # Option 2: Run specific test with detailed diff
    # Uncomment to test a specific test case:
    # print("\n2. Running specific test with diff...")
    # runner.run_test("addcomma")
    # runner.show_diff("addcomma")
    
    # Option 3: Run all tests (600+ tests)
    # Warning: This will take a while and many will fail initially
    # Uncomment when ready for comprehensive testing:
    # print("\n3. Running ALL tests...")
    # runner.results = []  # Clear previous results
    # runner.run_all_tests()
    # runner.generate_report("all_test_results.json")
    
    return 0 if all(r.passed or r.skipped for r in runner.results) else 1

if __name__ == "__main__":
    sys.exit(main())