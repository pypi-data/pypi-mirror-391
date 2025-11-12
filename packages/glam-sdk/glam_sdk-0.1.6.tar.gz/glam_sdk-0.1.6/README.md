# GLAM SDK for Python

Python SDK for interacting with the GLAM protocol on Solana. This SDK provides Python bindings for the GLAM Mint and Protocol programs.

[![PyPI version](https://badge.fury.io/py/glam-sdk.svg)](https://badge.fury.io/py/glam-sdk)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Installation

```bash
pip install glam-sdk
```

## Development

### Install for Development

```bash
# Clone the repository
git clone https://github.com/glamsystems/glam-sdk-py.git
cd glam-sdk-py

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Lint and auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

## Requirements

- Python >= 3.8
- anchorpy >= 0.21.0
- solana >= 0.36.0
- solders >= 0.26.0

## Note

This SDK code under `glam/mint` and `glam/protocol` directories is auto-generated from the GLAM program IDLs using [codama-py](https://github.com/Solana-ZH/codama-py). Do not manually edit the generated files.
