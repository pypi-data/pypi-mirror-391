# Publishing mini-rag as a Library

This guide walks you through publishing the `mini-rag` library to PyPI (Python Package Index).

## Prerequisites

1. **Python 3.11+** installed
2. **PyPI account**: Create one at https://pypi.org/account/register/
3. **TestPyPI account** (optional but recommended): Create one at https://test.pypi.org/account/register/
4. **API tokens**: Generate API tokens for uploading packages

## Step 1: Update Package Metadata

Before publishing, update the following in `pyproject.toml`:

1. **Author information**: Replace `Your Name` and `your.email@example.com` with your actual details
2. **Repository URLs**: Update all GitHub URLs with your actual repository
3. **Version**: Update version number as needed following [Semantic Versioning](https://semver.org/)

```toml
authors = [
    {name = "Your Actual Name", email = "youremail@example.com"}
]

[project.urls]
Homepage = "https://github.com/yourusername/mini-rag"
Repository = "https://github.com/yourusername/mini-rag"
```

## Step 2: Update the LICENSE

Edit `LICENSE` file and replace `[Your Name]` with your actual name.

## Step 3: Install Build Tools

```bash
# Using pip
pip install build twine

# Or using uv (if you're using it)
uv pip install build twine
```

## Step 4: Build the Package

From the project root directory:

```bash
# Clean any previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build
```

This will create two files in the `dist/` directory:
- `mini_rag-0.1.0-py3-none-any.whl` (wheel distribution)
- `mini_rag-0.1.0.tar.gz` (source distribution)

## Step 5: Test the Build Locally (Optional)

Install your package locally to test:

```bash
pip install dist/mini_rag-0.1.0-py3-none-any.whl
```

Or in editable mode during development:

```bash
pip install -e .
```

Test the installation:

```python
from mini import AgenticRAG, DocumentLoader, VectorStore
print("Import successful!")
```

## Step 6: Upload to TestPyPI (Recommended First Step)

Before uploading to the real PyPI, test with TestPyPI:

### 6.1 Configure TestPyPI credentials

Create or edit `~/.pypirc`:

```ini
[testpypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmc...  # Your TestPyPI token
```

### 6.2 Upload to TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
```

### 6.3 Test installation from TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mini-rag
```

Note: The `--extra-index-url` is needed because your dependencies are on the main PyPI.

## Step 7: Upload to PyPI (Production)

Once you've verified everything works on TestPyPI:

### 7.1 Get your PyPI API token

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Set scope to "Entire account" or specific project

### 7.2 Configure PyPI credentials

Add to `~/.pypirc`:

```ini
[pypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmc...  # Your PyPI token
```

### 7.3 Upload to PyPI

```bash
python -m twine upload dist/*
```

## Step 8: Verify Your Package

After uploading:

1. Check your package page: https://pypi.org/project/mini-rag/
2. Install from PyPI: `pip install mini-rag`
3. Test the installation

## Updating Your Package

When you need to publish a new version:

1. **Update the version** in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # or "0.2.0", "1.0.0", etc.
   ```

2. **Update version in** `mini/__init__.py`:
   ```python
   __version__ = "0.1.1"
   ```

3. **Rebuild and upload**:
   ```bash
   rm -rf dist/
   python -m build
   python -m twine upload dist/*
   ```

## Best Practices

### Version Numbering (Semantic Versioning)
- **MAJOR** (1.0.0): Incompatible API changes
- **MINOR** (0.1.0): Add functionality (backwards-compatible)
- **PATCH** (0.0.1): Bug fixes (backwards-compatible)

### Before Each Release
- [ ] Update version in `pyproject.toml` and `mini/__init__.py`
- [ ] Update CHANGELOG.md with changes
- [ ] Run tests
- [ ] Update documentation
- [ ] Build and test locally
- [ ] Tag release in git: `git tag -a v0.1.0 -m "Release version 0.1.0"`
- [ ] Push tag: `git push origin v0.1.0`

### .gitignore Additions

Make sure your `.gitignore` includes:

```
# Build artifacts
dist/
build/
*.egg-info/
__pycache__/

# PyPI
.pypirc

# Environment
.env
```

## Continuous Integration (Optional)

Consider setting up GitHub Actions to automatically publish on release:

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
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

Add your PyPI token as a secret in GitHub repository settings.

## Troubleshooting

### "File already exists" error
You cannot overwrite a version that's already published. Increment the version number.

### Import errors after installation
Make sure all imports in your code use absolute imports (`from mini.X import Y`), not relative imports.

### Missing dependencies
Ensure all required dependencies are listed in `pyproject.toml`.

### Package not found after upload
Wait a few minutes for PyPI's CDN to update, then try again.

## Resources

- [PyPI Help](https://pypi.org/help/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [Twine Documentation](https://twine.readthedocs.io/)

## Quick Command Reference

```bash
# Build
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mini-rag

# Install from PyPI
pip install mini-rag

# Install locally in development
pip install -e .
```

