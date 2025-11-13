# Quick Start Guide for Publishing mini-rag

## TL;DR - Steps to Publish

1. **Update metadata** in `pyproject.toml`:
   - Replace author name and email
   - Update GitHub repository URLs
   
2. **Install build tools**:
   ```bash
   pip install build twine
   ```

3. **Build the package**:
   ```bash
   python -m build
   ```

4. **Get PyPI API token**:
   - Go to https://pypi.org/manage/account/token/
   - Create new token

5. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   # Enter __token__ as username
   # Paste your token as password
   ```

## What I've Set Up For You

✅ Created `mini/__init__.py` - Exports all public APIs  
✅ Updated `pyproject.toml` - Added all required metadata  
✅ Created `LICENSE` - MIT License (update with your name)  
✅ Created `MANIFEST.in` - Includes necessary files  
✅ Fixed all imports - Changed to absolute imports (`from mini.X`)  
✅ Updated `.gitignore` - Excludes build artifacts and credentials  

## Files You Need to Customize

### 1. `pyproject.toml` (lines 12-16, 50-53)
```toml
authors = [
    {name = "Your Name", email = "your.email@example.com"}  # ← Change this
]

[project.urls]
Homepage = "https://github.com/yourusername/mini-rag"  # ← Change these
Repository = "https://github.com/yourusername/mini-rag"
Issues = "https://github.com/yourusername/mini-rag/issues"
```

### 2. `LICENSE` (line 3)
```
Copyright (c) 2025 [Your Name]  # ← Change this
```

## Test Locally First

```bash
# Build the package
python -m build

# Install locally
pip install dist/*.whl

# Test it works
python -c "from mini import AgenticRAG, DocumentLoader; print('Success!')"
```

## After Publishing

Your users can install with:
```bash
pip install mini-rag
```

And use it like:
```python
from mini import AgenticRAG, DocumentLoader, VectorStore, EmbeddingConfig

# Your library is now published!
```

## Need More Details?

See `PUBLISHING.md` for:
- Testing with TestPyPI before production
- Setting up CI/CD with GitHub Actions
- Version management best practices
- Troubleshooting common issues

