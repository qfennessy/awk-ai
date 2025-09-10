# Using Gawk Tests with pyawk_ai

## Quick Start

### 1. Extract Tests (One-time setup)
```bash
# From the awk-ai directory, extract all gawk tests
python3 extract_tests.py extract ../gawk/test ./gawk_tests
```

This creates:
- `gawk_tests/tests/` - 609 AWK test programs
- `gawk_tests/inputs/` - 210 input data files
- `gawk_tests/expected/` - 668 expected output files
- `gawk_tests/metadata/` - Test inventory and metadata

### 2. Run Tests

#### Option A: Use the provided runner script
```bash
python3 run_gawk_tests.py
```

#### Option B: Run tests programmatically
```python
from extract_tests import GawkTestRunner

runner = GawkTestRunner(
    pygawk_path="./pyawk_ai.py",
    test_dir="./gawk_tests"
)

# Run a single test
result = runner.run_test("addcomma")
print(f"Test passed: {result.passed}")

# Run multiple tests
results = runner.run_test_subset(["addcomma", "argtest", "concat1"])

# Generate report
runner.generate_report("test_results.json")
```

#### Option C: Run tests manually
```bash
# Run a single test manually
./pyawk_ai.py -f gawk_tests/tests/addcomma.awk < gawk_tests/inputs/addcomma.in > output.txt
diff gawk_tests/expected/addcomma.ok output.txt
```

## Test Categories

### Starter Tests (Basic functionality)
- `addcomma` - Number formatting with commas
- `concat1` - String concatenation
- `argtest` - Command-line argument handling
- `arrayind1` - Array indexing
- `aasort` - Array sorting

### Intermediate Tests
- `substr` - Substring operations
- `printf0` - Formatted printing
- `fieldassign` - Field assignment ($1, $2, etc.)
- `getline` - Input operations

### Advanced Tests
- `mpfr*` - Arbitrary precision math (requires MPFR support)
- `fork*` - Process management
- `network*` - TCP/IP networking

## Understanding Test Results

### Test Result Structure
```json
{
  "name": "addcomma",
  "passed": false,
  "expected": "1,234\n",
  "actual": "1234\n",
  "stderr": "",
  "returncode": 0,
  "skipped": false,
  "error": ""
}
```

### Common Failure Patterns

1. **Missing Feature**: Test uses unimplemented AWK feature
   - Solution: Implement the feature or skip the test

2. **Output Format**: Minor differences in formatting
   - Example: Floating point precision, whitespace
   - Solution: Adjust output formatting

3. **Error Handling**: Different error messages
   - Solution: Match gawk's error behavior

## Development Workflow

### 1. Start with Basic Tests
```python
# Focus on tests that don't require file I/O
basic_tests = [
    "aasort",      # Array sorting (no input file)
    "concat1",     # String operations
    "arrayind1",   # Array basics
]
```

### 2. Track Progress
```bash
# Run tests and save results
python3 run_gawk_tests.py

# Check which tests pass
cat test_results.json | jq '.summary'

# See specific failures
cat test_results.json | jq '.results[] | select(.passed == false) | .name'
```

### 3. Debug Failures
```python
# Show detailed diff for a failing test
from extract_tests import GawkTestRunner

runner = GawkTestRunner("./pyawk_ai.py", "./gawk_tests")
runner.run_test("addcomma")
runner.show_diff("addcomma")
```

### 4. Skip Unimplemented Features
```python
# Configure features your implementation supports
runner = GawkTestRunner(
    pygawk_path="./pyawk_ai.py",
    test_dir="./gawk_tests",
    features=["arrays", "strings", "math"]  # Skip tests requiring other features
)
```

## Test File Locations

```
gawk_tests/
├── tests/          # AWK programs (.awk files)
│   ├── addcomma.awk
│   ├── argtest.awk
│   └── ...
├── inputs/         # Input data (.in files)
│   ├── addcomma.in
│   └── ...
├── expected/       # Expected output (.ok files)
│   ├── addcomma.ok
│   └── ...
└── metadata/       # Test inventory
    └── test_list.json
```

## Tips

1. **Start Small**: Begin with 10-20 basic tests
2. **Incremental Development**: Fix one test category at a time
3. **Use Test Names**: Test names often hint at what they test
4. **Check Gawk Source**: Look at test files to understand requirements
5. **Platform Differences**: Some tests are platform-specific

## Example: Analyzing a Test

Let's examine the `addcomma` test:

```bash
# View the AWK program
cat gawk_tests/tests/addcomma.awk

# View the input
cat gawk_tests/inputs/addcomma.in

# View expected output
cat gawk_tests/expected/addcomma.ok

# Run with gawk to understand behavior
gawk -f gawk_tests/tests/addcomma.awk < gawk_tests/inputs/addcomma.in

# Run with your implementation
./pyawk_ai.py -f gawk_tests/tests/addcomma.awk < gawk_tests/inputs/addcomma.in
```

## Next Steps

1. Run the starter tests to baseline your implementation
2. Pick a category of tests to focus on (e.g., string operations)
3. Implement missing features based on test failures
4. Track your progress toward full compatibility