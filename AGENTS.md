# Coding Agent Guide

## Environment Setup

Before running tests, activate the virtual environment:

```bash
source venv/bin/activate
```

## Running Tests

Tests use Python's built-in unittest framework (not pytest). Run from the `tests/` directory:

```bash
# Run all tests from tests/ directory
cd tests
python -m unittest discover -s . -p "test_*.py"

# Run a specific test file
python -m unittest test_base
python -m unittest test_posix
python -m unittest test_windows

# Run from project root
find tests/ -name test_*.py -print -exec python {} \;
# or
python tests/test_base.py
python tests/test_posix.py
python tests/test_windows.py
```

## Test Architecture

- Platform-independent tests in `test_base.py`
- Platform-specific tests auto-skip on incompatible platforms via `@unittest.skipIf`
- `tests/context.py` adds parent directory to `sys.path` for imports
- `PosixConfig` uses `~/.config/{app_name}/`, `WindowsConfig` uses `%APPDATA%\{app_name}\`

## Assertion Convention

**Always include a second part in assertions** showing the actual value for debugging:

```python
# For simple values
assert config.get("test") is None, config.get("test")

# For list/tuple comparisons
assert received == [("custom_event", "test_data")], received

# For complex expressions, use the exact expression
assert config.path()[-len(self.app_name):] == self.app_name, \
    (config.path()[-len(self.app_name):], self.app_name)
```

This pattern provides actual failure values when assertions fail.
