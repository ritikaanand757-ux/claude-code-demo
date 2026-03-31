# 🧪 How to Run Tests

## Prerequisites

Make sure you have installed all dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

### Run All Tests
```bash
# Run all test files
pytest

# Run with verbose output
pytest -v

# Run with very verbose output
pytest -vv
```

### Run Specific Test Files
```bash
# Run only the enhanced API tests
pytest tests/test_enhanced_api.py -v

# Run only the original API tests
pytest tests/test_api.py -v
```

### Run Specific Test Cases
```bash
# Run a specific test class
pytest tests/test_enhanced_api.py::TestEnhancedTaskAPI -v

# Run a specific test method
pytest tests/test_enhanced_api.py::TestEnhancedTaskAPI::test_update_task_priority -v
```

### Run Tests with Coverage
```bash
# Generate coverage report
pytest --cov=backend tests/

# Generate HTML coverage report
pytest --cov=backend --cov-report=html tests/

# View coverage report (opens in browser)
# The report will be in htmlcov/index.html
```

### Run Tests with Different Output Formats
```bash
# Short test summary
pytest --tb=short

# Long test summary with full tracebacks
pytest --tb=long

# Show only the first and last line of each failure
pytest --tb=line

# No traceback at all
pytest --tb=no
```

### Run Tests and Stop on First Failure
```bash
pytest -x
```

### Run Tests in Parallel (faster)
```bash
# Install pytest-xdist first
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

### Filter Tests
```bash
# Run tests matching a keyword
pytest -k "update" -v

# Run tests NOT matching a keyword
pytest -k "not update" -v

# Run tests matching multiple keywords
pytest -k "priority or tags" -v
```

## Debugging Tests

### Run with Print Statements
```bash
# By default pytest captures print output
# Use -s to see print statements
pytest -s
```

### Run with PDB Debugger
```bash
# Drop into PDB on failure
pytest --pdb

# Drop into PDB at the start of each test
pytest --trace
```

### Show Detailed Test Output
```bash
# Show local variables in tracebacks
pytest -l

# Show captured output for failed tests
pytest --showlocals
```

## Continuous Testing

### Watch Mode (requires pytest-watch)
```bash
pip install pytest-watch

# Automatically re-run tests when files change
ptw
```

## Common Issues

### Tests Fail Due to Database
If tests fail with database connection errors:
1. Make sure PostgreSQL is running
2. Check database credentials in `backend/database.py`
3. Ensure the test database exists

### Import Errors
If you get import errors:
```bash
# Make sure you're in the project root directory
cd C:/Users/2000185351/claude-code-demo

# Run tests with Python module syntax
python -m pytest tests/
```

### Slow Tests
If tests are running slowly:
1. Use parallel execution: `pytest -n auto`
2. Run only specific tests during development
3. Consider using test markers to skip slow tests:
   ```bash
   pytest -m "not slow"
   ```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Pytest fixtures and configuration
├── test_api.py           # Original API tests
└── test_enhanced_api.py  # Enhanced API tests with new features
```

## Useful Pytest Options

| Option | Description |
|--------|-------------|
| `-v` | Verbose output |
| `-vv` | Very verbose output |
| `-s` | Show print statements |
| `-x` | Stop on first failure |
| `--lf` | Run only tests that failed last time |
| `--ff` | Run failures first, then the rest |
| `-k EXPRESSION` | Run tests matching the expression |
| `--maxfail=N` | Stop after N failures |
| `-m MARKER` | Run tests with specific marker |
| `--durations=N` | Show N slowest tests |

## Example Workflow

```bash
# 1. Run all tests to ensure everything works
pytest -v

# 2. During development, run specific tests
pytest tests/test_enhanced_api.py::TestEnhancedTaskAPI::test_update_task_priority -vv

# 3. Before committing, run full test suite with coverage
pytest --cov=backend --cov-report=html

# 4. View coverage report
# Open htmlcov/index.html in your browser
```

## CI/CD Integration

For GitHub Actions or similar:
```yaml
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest --cov=backend --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v2
```

---

Happy Testing! 🎉
