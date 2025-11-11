# Release Guide for Grasp Python SDK

## Pre-release Checklist

- [ ] All tests pass locally
- [ ] Version number updated in `pyproject.toml`
- [ ] README.md is up to date
- [ ] CHANGELOG updated (if exists)
- [ ] Examples work correctly

## Current Release Info

- **Package Name**: grasp-sdk (on PyPI)
- **Import Name**: grasp (in Python code)
- **Previous Version**: 0.1.11 (from previous maintainer)
- **New Version**: 0.2.0 (complete rewrite)

## Publishing Steps

### 1. Clean previous builds
```bash
rm -rf dist/ build/ *.egg-info/
```

### 2. Install build tools
```bash
pip install --upgrade build twine
```

### 3. Build the package
```bash
python -m build
```

### 4. Check the distribution
```bash
# Check if package is correctly structured
twine check dist/*

# Test installation locally
pip install dist/grasp_sdk-0.2.0-py3-none-any.whl

# Verify it works
python -c "from grasp import Grasp; print('Import successful!')"
```

### 5. Upload to Test PyPI (optional but recommended)
```bash
# Upload to test.pypi.org first
twine upload --repository testpypi dist/*

# Test install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ grasp-sdk==0.2.0
```

### 6. Upload to PyPI
```bash
# You'll need PyPI credentials or token
twine upload dist/*
```

## Authentication

You'll need PyPI credentials. There are two options:

### Option 1: Using Token (Recommended)
1. Go to https://pypi.org/manage/account/token/
2. Create a token for `grasp-sdk` project
3. Use `__token__` as username and the token as password

### Option 2: Using .pypirc file
Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
```

## Post-release

After successful release:
1. Create a git tag: `git tag v0.2.0`
2. Push tag: `git push origin v0.2.0`
3. Create GitHub release with changelog
4. Update documentation if needed

## Breaking Changes from 0.1.11

Since this is a complete rewrite, users upgrading from 0.1.11 should be aware:
- Completely new API design
- Both sync and async clients available
- Different import structure
- New error handling system
- Better container lifecycle management

## Version History

- **0.1.11** - Last version from previous maintainer
- **0.2.0** - Complete rewrite with new architecture