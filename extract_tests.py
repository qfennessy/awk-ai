#!/usr/bin/env python3
"""
Gawk Test Suite Extractor and Runner for Python AWK Implementation

This script extracts gawk tests and provides a framework for running them
against a Python implementation of AWK.
"""

import subprocess
import difflib
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass, asdict


@dataclass
class TestResult:
    """Result of a single test execution"""
    name: str
    passed: bool
    expected: str
    actual: str
    stderr: str
    returncode: int
    skipped: bool = False
    skip_reason: str = ""
    error: str = ""


class GawkTestExtractor:
    """Extract gawk tests to a structured format"""
    
    def __init__(self, gawk_test_dir: Path, output_dir: Path):
        self.gawk_test_dir = Path(gawk_test_dir)
        self.output_dir = Path(output_dir)
        
    def extract_tests(self) -> Dict[str, int]:
        """Extract all test files to organized directories"""
        # Create output directories
        (self.output_dir / "tests").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "inputs").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "expected").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "metadata").mkdir(parents=True, exist_ok=True)
        
        stats = {
            'awk_files': 0,
            'input_files': 0,
            'expected_files': 0
        }
        
        # Copy AWK test programs
        for awk_file in self.gawk_test_dir.glob("*.awk"):
            dest = self.output_dir / "tests" / awk_file.name
            try:
                dest.write_text(awk_file.read_text(encoding='utf-8'))
            except UnicodeDecodeError:
                # Handle binary or non-UTF8 files
                dest.write_bytes(awk_file.read_bytes())
            stats['awk_files'] += 1
            
        # Copy input files
        for input_file in self.gawk_test_dir.glob("*.in"):
            dest = self.output_dir / "inputs" / input_file.name
            try:
                dest.write_text(input_file.read_text(encoding='utf-8'))
            except UnicodeDecodeError:
                # Handle binary or non-UTF8 files
                dest.write_bytes(input_file.read_bytes())
            stats['input_files'] += 1
            
        # Copy expected output files
        for ok_file in self.gawk_test_dir.glob("*.ok"):
            dest = self.output_dir / "expected" / ok_file.name
            try:
                dest.write_text(ok_file.read_text(encoding='utf-8'))
            except UnicodeDecodeError:
                # Handle binary or non-UTF8 files
                dest.write_bytes(ok_file.read_bytes())
            stats['expected_files'] += 1
            
        # Generate test inventory
        test_list = sorted([f.stem for f in (self.output_dir / "tests").glob("*.awk")])
        (self.output_dir / "metadata" / "test_list.json").write_text(
            json.dumps(test_list, indent=2)
        )
        
        print(f"Extracted {stats['awk_files']} AWK programs")
        print(f"Extracted {stats['input_files']} input files")
        print(f"Extracted {stats['expected_files']} expected output files")
        
        return stats


class GawkTestRunner:
    """Run extracted gawk tests against a Python AWK implementation"""
    
    # Tests that require special features
    FEATURE_REQUIREMENTS = {
        'mpfr': ['mpfr', 'mpfr_arbitrary_precision'],
        'fork': ['process_management', 'fork'],
        'getline': ['getline', 'coprocess'],
        'network': ['networking', 'tcp_ip'],
        'strftime': ['time_functions', 'locale'],
    }
    
    def __init__(self, pygawk_path: str, test_dir: Path, features: Optional[List[str]] = None):
        self.pygawk = pygawk_path
        self.test_dir = Path(test_dir)
        self.features = features or []
        self.results: List[TestResult] = []
        
    def should_skip_test(self, test_name: str) -> Tuple[bool, str]:
        """Check if a test should be skipped based on features"""
        for feature_prefix, required_features in self.FEATURE_REQUIREMENTS.items():
            if test_name.startswith(feature_prefix):
                missing = [f for f in required_features if f not in self.features]
                if missing:
                    return True, f"Missing features: {', '.join(missing)}"
        return False, ""
    
    def run_test(self, test_name: str) -> TestResult:
        """Run a single test and compare output"""
        # Check if test should be skipped
        should_skip, skip_reason = self.should_skip_test(test_name)
        if should_skip:
            return TestResult(
                name=test_name,
                passed=False,
                expected="",
                actual="",
                stderr="",
                returncode=0,
                skipped=True,
                skip_reason=skip_reason
            )
        
        awk_file = self.test_dir / "tests" / f"{test_name}.awk"
        input_file = self.test_dir / "inputs" / f"{test_name}.in"
        expected_file = self.test_dir / "expected" / f"{test_name}.ok"
        
        if not awk_file.exists():
            return TestResult(
                name=test_name,
                passed=False,
                expected="",
                actual="",
                stderr="",
                returncode=1,
                error=f"AWK file not found: {awk_file}"
            )
        
        if not expected_file.exists():
            # Some tests might not have expected output files
            expected = ""
        else:
            expected = expected_file.read_text()
        
        # Build command
        # Check if pygawk supports -f flag
        if self.pygawk.endswith('pyawk_ai.py'):
            # pyawk_ai.py takes the program as a direct argument
            with open(awk_file, 'r') as f:
                program = f.read()
            cmd = [self.pygawk, program]
        else:
            # Standard awk/gawk uses -f flag
            cmd = [self.pygawk, "-f", str(awk_file)]
        stdin_data = None
        
        if input_file.exists():
            stdin_data = input_file.read_text()
        
        try:
            # Run the test
            result = subprocess.run(
                cmd,
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=5  # 5 second timeout
            )
            
            actual = result.stdout
            stderr = result.stderr
            returncode = result.returncode
            
        except subprocess.TimeoutExpired:
            return TestResult(
                name=test_name,
                passed=False,
                expected=expected,
                actual="",
                stderr="TIMEOUT",
                returncode=-1,
                error="Test timed out after 5 seconds"
            )
        except Exception as e:
            return TestResult(
                name=test_name,
                passed=False,
                expected=expected,
                actual="",
                stderr=str(e),
                returncode=-1,
                error=f"Failed to run test: {e}"
            )
        
        # Compare output
        passed = actual == expected
        
        return TestResult(
            name=test_name,
            passed=passed,
            expected=expected,
            actual=actual,
            stderr=stderr,
            returncode=returncode
        )
    
    def run_test_subset(self, test_names: List[str]) -> List[TestResult]:
        """Run a specific subset of tests"""
        for test_name in test_names:
            result = self.run_test(test_name)
            self.results.append(result)
            
            if result.skipped:
                print(f"⊘ {test_name} (skipped: {result.skip_reason})")
            elif result.passed:
                print(f"✓ {test_name}")
            else:
                print(f"✗ {test_name}")
                if result.error:
                    print(f"  Error: {result.error}")
        
        return self.results
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all available tests"""
        test_files = sorted(self.test_dir.glob("tests/*.awk"))
        test_names = [f.stem for f in test_files]
        
        return self.run_test_subset(test_names)
    
    def generate_report(self, output_file: Optional[str] = None) -> Dict:
        """Generate comprehensive test report"""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed and not r.skipped)
        skipped = sum(1 for r in self.results if r.skipped)
        total = len(self.results)
        
        report = {
            'summary': {
                'total': total,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'pass_rate': f"{(passed/total*100):.1f}%" if total > 0 else "0%"
            },
            'results': [asdict(r) for r in self.results]
        }
        
        print(f"\n{'='*50}")
        print(f"Test Results Summary")
        print(f"{'='*50}")
        print(f"Total:   {total}")
        print(f"Passed:  {passed} ({(passed/total*100):.1f}%)" if total > 0 else "Passed:  0")
        print(f"Failed:  {failed}")
        print(f"Skipped: {skipped}")
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nDetailed report saved to: {output_file}")
        
        # Show first 10 failures
        failures = [r for r in self.results if not r.passed and not r.skipped]
        if failures:
            print(f"\n{'='*50}")
            print(f"Failed Tests (showing first 10)")
            print(f"{'='*50}")
            
            for fail in failures[:10]:
                print(f"\n{fail.name}:")
                if fail.error:
                    print(f"  Error: {fail.error}")
                else:
                    print(f"  Expected: {repr(fail.expected[:100])}")
                    print(f"  Got:      {repr(fail.actual[:100])}")
                    if fail.stderr:
                        print(f"  Stderr:   {fail.stderr[:100]}")
        
        return report
    
    def show_diff(self, test_name: str):
        """Show detailed diff for a specific test"""
        result = next((r for r in self.results if r.name == test_name), None)
        
        if not result:
            print(f"Test '{test_name}' not found in results")
            return
        
        if result.skipped:
            print(f"Test '{test_name}' was skipped: {result.skip_reason}")
            return
        
        if result.passed:
            print(f"Test '{test_name}' passed")
            return
        
        print(f"\nDiff for test '{test_name}':")
        print("="*50)
        
        diff = difflib.unified_diff(
            result.expected.splitlines(keepends=True),
            result.actual.splitlines(keepends=True),
            fromfile=f"{test_name}.ok",
            tofile=f"{test_name}.actual"
        )
        
        sys.stdout.writelines(diff)


def get_starter_tests() -> List[str]:
    """Return a list of basic tests to start with"""
    return [
        # Basic operations
        'addcomma',     # Number formatting
        'argtest',      # Command-line arguments  
        'aasort',       # Array sorting (no input file)
        'aasorti',      # Array index sorting
        
        # String operations
        'concat1',      # String concatenation
        'substr',       # Substring function
        
        # Arithmetic
        'math',         # Basic math operations
        
        # Control flow
        'forsimp',      # Simple for loops
        'nfloop',       # Loop with NF
        
        # Arrays
        'arrayind1',    # Array indexing
        'delarprm',     # Array element deletion
        
        # Functions
        'functab1',     # Function table test
        
        # Field operations
        'fieldassign',  # Field assignment
        'nfldstr',      # NF with field strings
    ]


def main():
    parser = argparse.ArgumentParser(description='Extract and run gawk tests')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract tests from gawk repo')
    extract_parser.add_argument('gawk_test_dir', help='Path to gawk/test directory')
    extract_parser.add_argument('output_dir', help='Output directory for extracted tests')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run extracted tests')
    run_parser.add_argument('pygawk', help='Path to Python AWK implementation')
    run_parser.add_argument('test_dir', help='Directory with extracted tests')
    run_parser.add_argument('--subset', choices=['starter', 'all'], default='starter',
                           help='Which tests to run')
    run_parser.add_argument('--output', help='Output file for test report')
    run_parser.add_argument('--features', nargs='*', default=[],
                           help='List of implemented features')
    
    # Diff command
    diff_parser = subparsers.add_parser('diff', help='Show diff for a specific test')
    diff_parser.add_argument('pygawk', help='Path to Python AWK implementation')
    diff_parser.add_argument('test_dir', help='Directory with extracted tests')
    diff_parser.add_argument('test_name', help='Name of test to diff')
    
    args = parser.parse_args()
    
    if args.command == 'extract':
        extractor = GawkTestExtractor(args.gawk_test_dir, args.output_dir)
        extractor.extract_tests()
        
    elif args.command == 'run':
        runner = GawkTestRunner(args.pygawk, args.test_dir, args.features)
        
        if args.subset == 'starter':
            test_names = get_starter_tests()
            print(f"Running {len(test_names)} starter tests...\n")
            runner.run_test_subset(test_names)
        else:
            print("Running all tests...\n")
            runner.run_all_tests()
        
        runner.generate_report(args.output)
        
    elif args.command == 'diff':
        runner = GawkTestRunner(args.pygawk, args.test_dir)
        runner.run_test(args.test_name)
        runner.show_diff(args.test_name)
        
    else:
        parser.print_help()


if __name__ == '__main__':
    main()