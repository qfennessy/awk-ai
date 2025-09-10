# Gawk Test Suite Extraction Guide for Python Reimplementation

## Overview

The gawk test suite contains ~600+ test programs with expected outputs that comprehensively test AWK functionality. These tests are invaluable for validating a Python reimplementation of gawk.

## Test File Structure

Each test typically consists of:
- `testname.awk` - The AWK program to execute
- `testname.in` - Input data (optional, ~210 tests have input files)
- `testname.ok` - Expected output

### Test Execution Pattern
```bash
gawk -f testname.awk < testname.in > actual_output
diff testname.ok actual_output
```

For tests without `.in` files, the AWK program generates its own data or operates on BEGIN/END blocks.

## Extraction Strategy

### Step 1: Copy Test Files

```bash
# Create directory structure
mkdir -p pygawk_tests/{tests,expected,inputs}

# Copy all test files
cp test/*.awk pygawk_tests/tests/
cp test/*.ok pygawk_tests/expected/
cp test/*.in pygawk_tests/inputs/ 2>/dev/null || true
```

### Step 2: Parse Test Metadata

Extract test requirements from Makefile.am to understand:
- Which tests need special command-line arguments
- Which tests are platform-specific
- Which tests require specific features (MPFR, networking, etc.)

### Step 3: Test Categories to Prioritize

Start with these fundamental test categories:

1. **Basic Operations** (Priority 1)
   - `addcomma` - Number formatting
   - `argtest` - Command-line arguments
   - `asort/asorti` - Array sorting
   - `concat*` - String concatenation
   - `math` - Basic math operations

2. **Core Language Features** (Priority 2)
   - `array*` - Array operations
   - `field*` - Field splitting ($1, $2, etc.)
   - `getline*` - Input operations
   - `printf*` - Formatted output
   - `regex*` - Regular expressions

3. **Functions** (Priority 3)
   - `func*` - User-defined functions
   - `builtin` - Built-in functions
   - `substr*` - String functions

4. **Advanced Features** (Priority 4)
   - `mpfr*` - Arbitrary precision (can skip initially)
   - `fork*` - Process management (OS-specific)
   - `network*` - Networking (can defer)

## Test Adaptation Considerations

### 1. Input/Output Handling
- Tests expect exact output matching
- Line endings matter (Unix vs Windows)
- Floating-point precision differences need handling

### 2. Feature Gaps
Track tests that fail due to unimplemented features:
- Create a `skipped_tests.txt` file
- Document why each test is skipped
- Use as a roadmap for implementation

### 3. Platform Differences
Some tests have platform-specific outputs:
- `-mpfr.ok` files for arbitrary precision math
- `.w32` files for Windows
- Locale-specific tests in `test/fr/`

## Python Test Runner Architecture

```python
import subprocess
import difflib
from pathlib import Path
import json

class GawkTestRunner:
    def __init__(self, pygawk_path, test_dir):
        self.pygawk = pygawk_path
        self.test_dir = Path(test_dir)
        self.results = []
    
    def run_test(self, test_name):
        """Run a single test and compare output"""
        awk_file = self.test_dir / "tests" / f"{test_name}.awk"
        input_file = self.test_dir / "inputs" / f"{test_name}.in"
        expected_file = self.test_dir / "expected" / f"{test_name}.ok"
        
        # Build command
        cmd = [self.pygawk, "-f", str(awk_file)]
        stdin_data = None
        
        if input_file.exists():
            with open(input_file, 'r') as f:
                stdin_data = f.read()
        
        # Run the test
        result = subprocess.run(
            cmd, 
            input=stdin_data, 
            capture_output=True, 
            text=True
        )
        
        # Compare output
        with open(expected_file, 'r') as f:
            expected = f.read()
        
        passed = result.stdout == expected
        
        return {
            'name': test_name,
            'passed': passed,
            'expected': expected,
            'actual': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    
    def run_all_tests(self):
        """Run all available tests"""
        test_files = self.test_dir.glob("tests/*.awk")
        
        for test_file in test_files:
            test_name = test_file.stem
            result = self.run_test(test_name)
            self.results.append(result)
            
            if result['passed']:
                print(f"✓ {test_name}")
            else:
                print(f"✗ {test_name}")
        
        return self.results
    
    def generate_report(self):
        """Generate test report"""
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        # Save detailed results
        with open('test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Show failures
        failures = [r for r in self.results if not r['passed']]
        if failures:
            print("\nFailed tests:")
            for fail in failures[:10]:  # Show first 10 failures
                print(f"\n{fail['name']}:")
                print("Expected:", repr(fail['expected'][:100]))
                print("Got:", repr(fail['actual'][:100]))
```

## Test Compatibility Matrix

Create a compatibility tracking system:

```python
# test_compatibility.yaml
tests:
  addcomma:
    status: passing
    features: [arithmetic, sprintf, regex]
    
  mpfr001:
    status: skipped
    reason: "MPFR support not implemented"
    features: [mpfr]
    
  fork:
    status: partial
    reason: "Process management differs in Python"
    features: [system, fork]
```

## Extraction Script

```bash
#!/bin/bash
# extract_gawk_tests.sh

GAWK_REPO="."
TARGET_DIR="pygawk_tests"

# Create directory structure
mkdir -p $TARGET_DIR/{tests,inputs,expected,metadata}

# Copy test files
echo "Copying test files..."
cp $GAWK_REPO/test/*.awk $TARGET_DIR/tests/ 2>/dev/null || true
cp $GAWK_REPO/test/*.in $TARGET_DIR/inputs/ 2>/dev/null || true  
cp $GAWK_REPO/test/*.ok $TARGET_DIR/expected/ 2>/dev/null || true

# Extract test metadata from Makefile.am
echo "Extracting test metadata..."
grep -E "^[a-z0-9_]+:" $GAWK_REPO/test/Makefile.am > $TARGET_DIR/metadata/test_targets.txt

# Create test inventory
echo "Creating test inventory..."
ls $TARGET_DIR/tests/*.awk | xargs -I {} basename {} .awk > $TARGET_DIR/metadata/test_list.txt

# Count tests
echo "Test extraction complete!"
echo "Total tests: $(ls $TARGET_DIR/tests/*.awk | wc -l)"
echo "Tests with input: $(ls $TARGET_DIR/inputs/*.in 2>/dev/null | wc -l)"
echo "Expected outputs: $(ls $TARGET_DIR/expected/*.ok | wc -l)"
```

## Progressive Implementation Strategy

1. **Phase 1**: Implement basic tests (no I/O, just computations)
2. **Phase 2**: Add field splitting and basic I/O
3. **Phase 3**: Regular expressions and string functions
4. **Phase 4**: Arrays and user-defined functions
5. **Phase 5**: Advanced features (getline, coprocesses, etc.)

## Notes on Test Peculiarities

- Some tests intentionally produce errors (check stderr)
- Tests ending in numbers often test edge cases (e.g., `array1`, `array2`)
- Tests prefixed with `lint` check for warnings/errors
- POSIX compliance tests are prefixed with `posix`
- Some tests require specific locales (see `test/fr/`)

## Validation Approach

1. Start with a subset of ~50 core tests
2. Track pass/fail rates as features are implemented
3. Use failing tests to prioritize development
4. Consider tests "done" when 95%+ pass (some platform-specific tests may never pass)