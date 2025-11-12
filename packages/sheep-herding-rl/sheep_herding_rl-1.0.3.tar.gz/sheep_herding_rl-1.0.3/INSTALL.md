# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- CUDA-capable GPU (optional, for GPU acceleration)

## Installation Methods

### Method 1: Install from Source (Development Mode)

This is recommended if you want to modify the code:

```bash
# Clone the repository
git clone https://github.com/dzijo/ferit-hackathon.git
cd ferit-hackathon

# Install in editable mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Method 2: Install from Source (Standard)

```bash
# Clone the repository
git clone https://github.com/dzijo/ferit-hackathon.git
cd ferit-hackathon

# Install the package
pip install .
```

### Method 3: Build and Install as Wheel

```bash
# Clone the repository
git clone https://github.com/dzijo/ferit-hackathon.git
cd ferit-hackathon

# Build the package
python -m pip install build
python -m build

# Install the built wheel
pip install dist/sheep_herding_rl-0.1.0-py3-none-any.whl
```

### Method 4: Install from GitHub (Future)

Once published:

```bash
pip install sheep-herding-rl
```

## GPU Support (PyTorch with CUDA)

For GPU acceleration, install PyTorch with CUDA support:

```bash
# For CUDA 12.4
pip install torch --index-url https://download.pytorch.org/whl/cu124

# Then install the package
pip install -e .
```

## Verifying Installation

After installation, verify it works:

```python
import sheep_herding_rl
print(sheep_herding_rl.__version__)

# Test basic functionality
from sheep_herding_rl import Simulator
sim = Simulator()
print("Installation successful!")
```

## Development Setup

For development, install with development dependencies:

```bash
pip install -e ".[dev]"

# Run tests (when available)
pytest

# Format code
black .

# Lint code
flake8 .
```

## Troubleshooting

### Import Errors

If you encounter import errors, ensure all dependencies are installed:

```bash
pip install pygame numpy pillow scipy pyyaml matplotlib torch
```

### PyTorch CUDA Issues

If CUDA is not detected:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

If False, reinstall PyTorch with CUDA support.

### Permission Issues

On Linux/Mac, you might need to use `sudo` or install in a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## Uninstallation

To uninstall the package:

```bash
pip uninstall sheep-herding-rl
```

## Virtual Environment (Recommended)

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv sheep_herding_env

# Activate it
# On Windows:
sheep_herding_env\Scripts\activate
# On Linux/Mac:
source sheep_herding_env/bin/activate

# Install the package
pip install -e .
```
