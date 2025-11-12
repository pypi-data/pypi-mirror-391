# Building and Publishing Guide

This guide covers how to build, test, and publish the sheep-herding-rl package.

## Building the Package

### Prerequisites

Install build tools:

```bash
pip install build twine
```

### Build Distribution Files

```bash
# Clean previous builds (if any)
rm -rf build/ dist/ *.egg-info  # On Linux/Mac
# On Windows PowerShell:
# Remove-Item -Recurse -Force build, dist, *.egg-info

# Build source distribution and wheel
python -m build
```

This creates two files in the `dist/` directory:
- `sheep_herding_rl-1.0.tar.gz` (source distribution)
- `sheep_herding_rl-1.0-py3-none-any.whl` (wheel distribution)

### Verify the Build

```bash
# Check package contents
tar -tzf dist/sheep_herding_rl-1.0.tar.gz

# Or for wheel
unzip -l dist/sheep_herding_rl-1.0-py3-none-any.whl

# Verify package metadata
twine check dist/*
```

## Testing the Package Locally

### Install from Local Build

```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from wheel
pip install dist/sheep_herding_rl-0.1.0-py3-none-any.whl

# Test import
python -c "import sheep_herding_rl; print(sheep_herding_rl.__version__)"
```

### Test Installation

```python
# test_install.py
from sheep_herding_rl import Simulator, PPOAgent, SACAgent, TD3Agent
import sheep_herding_rl.config as config

print(f"Version: {sheep_herding_rl.__version__}")
print("All imports successful!")

# Test basic functionality
sim = Simulator()
print("Simulator created successfully!")
```

## Publishing to PyPI

### TestPyPI (Recommended First)

Test your package on TestPyPI before publishing to the main PyPI:

```bash
# Register on TestPyPI: https://test.pypi.org/account/register/

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Install from TestPyPI to test
pip install --index-url https://test.pypi.org/simple/ sheep-herding-rl
```

### Production PyPI

```bash
# Register on PyPI: https://pypi.org/account/register/

# Upload to PyPI
twine upload dist/*

# Now anyone can install with:
# pip install sheep-herding-rl
```

### Using API Tokens (Recommended)

Instead of username/password, use API tokens:

1. Generate token on PyPI: Account Settings → API tokens
2. Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
```

Then upload:

```bash
twine upload dist/*
```

## Version Management

### Updating Version Number

Update version in multiple places:

1. `setup.py`: `version='0.1.0'`
2. `pyproject.toml`: `version = "0.1.0"`
3. `__init__.py`: `__version__ = '0.1.0'`

### Version Numbering Convention

Follow Semantic Versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- `1.0.0` - First stable release
- `1.1.0` - New features, backwards compatible
- `1.1.1` - Bug fixes
- `2.0.0` - Breaking changes

## Continuous Integration (Optional)

### GitHub Actions for Automated Building

Create `.github/workflows/build.yml`:

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
        pip install -e ".[dev]"
    - name: Build package
      run: python -m build
    - name: Check package
      run: twine check dist/*
```

### Automated PyPI Publishing

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Checklist Before Publishing

- [ ] Update version numbers
- [ ] Update README.md with latest features
- [ ] Test package locally
- [ ] Run tests (if available)
- [ ] Check code formatting
- [ ] Update CHANGELOG.md
- [ ] Build distribution files
- [ ] Verify with `twine check`
- [ ] Test on TestPyPI
- [ ] Create git tag for version
- [ ] Publish to PyPI
- [ ] Create GitHub release

## Common Issues

### Missing Files in Distribution

Add to `MANIFEST.in`:
```
include path/to/file
```

### Import Errors After Installation

Check `setup.py` packages list or use `find_packages()`.

### Wrong Dependencies

Ensure `install_requires` in `setup.py` matches actual requirements.

## Documentation

Consider hosting documentation:

1. **Read the Docs**: Connect to GitHub
2. **GitHub Pages**: Use `mkdocs` or `sphinx`
3. **GitHub Wiki**: Simple documentation

## Support and Maintenance

After publishing:
- Monitor GitHub issues
- Respond to bug reports
- Accept pull requests
- Release updates regularly
- Keep dependencies updated
