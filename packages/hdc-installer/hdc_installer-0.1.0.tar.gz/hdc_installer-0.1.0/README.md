# harmony_hdc_bin_collection
Complete and available collection of `hdc` command tools. No need to download the development SDK for FamilyBucket, lightweight downloads are available.

## Installation

To install the hdc_installer package, navigate to the hdc_installer directory and run:

```bash
pip install .
```

Or for development installation:

```bash
pip install -e .
```

## Usage

After installation, you can use the hdc_installer command:

```bash
# Show help message
hdc_installer -h

# List available HDC binaries
hdc_installer -l

# Install HDC binary
hdc_installer -i
```

## Requirements

- Python 3.6 or higher
- click library (automatically installed with the package)

## Publishing

### Local Publishing

To publish locally to PyPI:

1. Make sure you have `twine` installed: `pip install twine`
2. Run the publish script: `./publish_local.sh`
3. Upload to PyPI: `twine upload dist/*`

### GitHub Actions Publishing

The repository includes GitHub Actions for automatic publishing:

- `publish.yml` - Publishes to PyPI when a release is published
- `test_publish.yml` - Publishes to TestPyPI on pushes to main branch

To enable GitHub Actions publishing, you need to set up secrets in your repository:
- `PYPI_API_TOKEN` - API token for PyPI
- `TEST_PYPI_API_TOKEN` - API token for TestPyPI