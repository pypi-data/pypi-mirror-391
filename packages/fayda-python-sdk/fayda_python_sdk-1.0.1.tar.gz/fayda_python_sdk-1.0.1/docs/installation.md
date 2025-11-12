# Installation

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Install from PyPI

The recommended way to install fayda-python-sdk is from PyPI:

```bash
pip install fayda-python-sdk
```

## Install from Source

To install from the source repository:

```bash
git clone https://github.com/National-ID-Program-Ethiopia/python-ida-sdk.git
cd python-ida-sdk
pip install -e .
```

## Verify Installation

To verify the installation, run:

```python
python -c "from fayda_py_sdk import ConfigBuilder; print('Installation successful!')"
```

## Dependencies

The SDK automatically installs the following dependencies:

- `cryptography>=41.0.0` - For cryptographic operations
- `pyjwt>=2.8.0` - For JWT signature generation
- `requests>=2.31.0` - For HTTP communication

## Development Dependencies

For development, install with dev dependencies:

```bash
pip install -e ".[dev]"
```

This includes:
- pytest - Testing framework
- black - Code formatter
- flake8 - Linter
- mypy - Type checker

