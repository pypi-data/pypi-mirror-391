# Local Testing Guide for drivee-client

This guide explains how to test the `drivee-client` package locally before publishing to PyPI.

## 🎯 Testing Methods

### Method 1: Editable Install (Recommended for Development)

**Best for:** Active development where you're making frequent changes.

```bash
# Install in editable mode
python build.py install-local

# Or manually:
pip install -e .
```

**Advantages:**

- ✅ Changes to source code are immediately reflected
- ✅ No need to rebuild after each change
- ✅ Can use debugger and see source code
- ✅ Perfect for development workflow

**Test it:**

```bash
# Run the test script
python test_local_install.py

# Or test manually in Python
python -c "from drivee_client import DriveeClient; print('Success!')"
```

**Uninstall when done:**

```bash
pip uninstall drivee-client
```

---

### Method 2: Install from Built Distribution

**Best for:** Testing the actual package before publishing to PyPI.

```bash
# Build the package
python build.py build

# Install from the built wheel
python build.py install-dist

# Or manually:
pip install dist/drivee_client-*.whl --force-reinstall
```

**Advantages:**

- ✅ Tests the exact package that will be published
- ✅ Verifies package metadata and dependencies
- ✅ Ensures all files are included correctly
- ✅ Validates the installation process

**Important:** You need to rebuild and reinstall after each code change.

---

### Method 3: Test from Test PyPI

**Best for:** Final validation before production release.

```bash
# Build and upload to Test PyPI
python build.py all
python build.py test-upload

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/drivee-client

# Or with dependencies from regular PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/drivee-client
```

**Advantages:**

- ✅ Tests the complete publishing workflow
- ✅ Validates package on a real PyPI server
- ✅ Safe environment (won't affect production)
- ✅ Can share test version with others

---

## 📋 Complete Testing Workflow

### Step 1: Development Testing

```bash
# Install in editable mode
python build.py install-local

# Run tests
pytest

# Run the verification script
python test_local_install.py

# Test your code manually
python -c "
import asyncio
from drivee_client import DriveeClient

async def test():
    async with DriveeClient('user', 'pass') as client:
        print('Client created successfully!')
        
asyncio.run(test())
"
```

### Step 2: Pre-publish Testing

```bash
# Clean and build
python build.py all

# Install from dist to test the package
python build.py install-dist

# Run full test suite
pytest

# Run the verification script
python test_local_install.py
```

### Step 3: Test PyPI Validation

```bash
# Upload to Test PyPI
python build.py test-upload

# Create a new virtual environment for clean testing
python -m venv test_env
test_env\Scripts\activate  # Windows
# source test_env/bin/activate  # Linux/Mac

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ drivee-client

# Test the package
python test_local_install.py

# Deactivate and cleanup
deactivate
```

### Step 4: Production Release

```bash
# Only after all tests pass!
python build.py upload
```

---

## 🧪 Testing Checklist

Before publishing to PyPI, ensure:

- [ ] All unit tests pass (`pytest`)
- [ ] Package builds without errors (`python build.py build`)
- [ ] Package passes twine check (`python build.py check`)
- [ ] Local install works (`python build.py install-local`)
- [ ] Verification script passes (`python test_local_install.py`)
- [ ] Version number updated in `drivee_client/__init__.py`
- [ ] CHANGELOG.md updated with changes
- [ ] README.md is accurate and up-to-date
- [ ] All dependencies are listed in `pyproject.toml`
- [ ] Test PyPI upload successful (`python build.py test-upload`)
- [ ] Installation from Test PyPI works
- [ ] Git changes committed and tagged

---

## 🐛 Troubleshooting

### "no running event loop" error

If you see `RuntimeError: no running event loop` when trying to instantiate `DriveeClient`:

**Problem:** The `DriveeClient` creates an `aiohttp.ClientSession` in `__init__`, which requires an active event loop.

**Solution:** Always instantiate and use `DriveeClient` within an async context:

```python
import asyncio
from drivee_client import DriveeClient

# ❌ Wrong - will fail with "no running event loop"
client = DriveeClient("user", "pass")

# ✅ Correct - use within async function
async def main():
    async with DriveeClient("user", "pass") as client:
        await client.init()
        # Your code here

asyncio.run(main())
```

### "Module not found" after installation

```bash
# Ensure you're in the right environment
pip list | grep drivee

# Try reinstalling
pip uninstall drivee-client
python build.py install-local
```

### Changes not reflected after editing code

```bash
# If using editable install, restart Python interpreter
# If using dist install, rebuild and reinstall
python build.py build
python build.py install-dist
```

### Import errors for dependencies

```bash
# Install dependencies manually
pip install aiohttp pydantic tenacity python-dotenv

# Or from the project
pip install -r requirements.txt
```

### Package metadata issues

```bash
# Check the built package
python build.py build
python build.py check

# Inspect the wheel contents
pip install wheel
wheel unpack dist/drivee_client-*.whl
```

---

## 💡 Tips

1. **Always use virtual environments** to avoid conflicts:

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

2. **Use pytest fixtures** for testing async code:

   ```python
   import pytest
   from drivee_client import DriveeClient
   
   @pytest.mark.asyncio
   async def test_client():
       async with DriveeClient("user", "pass") as client:
           assert client is not None
   ```

3. **Mock API calls** during testing:

   ```python
   from unittest.mock import AsyncMock, patch
   
   @patch('aiohttp.ClientSession.post')
   async def test_login(mock_post):
       mock_post.return_value.__aenter__.return_value.json = AsyncMock(
           return_value={"token": "test_token"}
       )
       # Your test code here
   ```

4. **Test with different Python versions** if supporting multiple versions:

   ```bash
   # Using pyenv or virtualenv for each version
   python3.10 -m venv venv310
   python3.11 -m venv venv311
   python3.12 -m venv venv312
   ```

---

## 📚 Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [Testing with pytest](https://docs.pytest.org/)
- [Test PyPI](https://test.pypi.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
