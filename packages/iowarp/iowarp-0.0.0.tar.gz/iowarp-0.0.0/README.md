# iowarp

[![Test Package](https://github.com/hyoklee/iowarp/actions/workflows/test.yml/badge.svg)](https://github.com/hyoklee/iowarp/actions/workflows/test.yml)
[![Publish to PyPI](https://github.com/hyoklee/iowarp/actions/workflows/publish.yml/badge.svg)](https://github.com/hyoklee/iowarp/actions/workflows/publish.yml)
[![PyPI version](https://badge.fury.io/py/iowarp.svg)](https://badge.fury.io/py/iowarp)

A PyPI wrapper package that installs both `iowarp-agent-toolkit` and `iowarp-core`.

## Installation

Install the package from PyPI:

```bash
pip install iowarp
```

This will automatically install both:
- `iowarp-agent-toolkit`
- `iowarp-core`

## Usage

Simply import the package in your Python code:

```python
import iowarp

print(f"IOWarp version: {iowarp.__version__}")
```

The underlying packages will be available for import as well:
```python
import iowarp_agent_toolkit
import iowarp_core
```

## Development

### Building the package locally

```bash
pip install build
python -m build
```

### Running tests

The test suite is automatically run via GitHub Actions on every push and pull request.

## Publishing

The package is automatically published to PyPI when a new release is created or a tag starting with `v` is pushed.

To publish a new version:

1. Update the version in `pyproject.toml` and `src/iowarp/__init__.py`
2. Create a new release on GitHub with a tag like `v0.1.0`
3. The GitHub Action will automatically build and publish to PyPI

Make sure the `PYPI_TOKEN` secret is configured in your GitHub repository settings.

## License

BSD 3-Clause License - see [LICENSE](LICENSE) file for details.
