# PyPI Package Upload Instructions

## Prerequisites
Ensure `.pypirc` is in home directory (`~/`) with proper tokens
   - TestPyPI and PyPI tokens should be configured
   - Use `CMD + Shift + .` in Finder to view hidden files

## Update Tools
```bash
python -m pip install --upgrade pip
python -m pip install --upgrade build
python -m pip install --upgrade twine
```

## Important Notes:
- Always update version in `setup.py`/`pyproject.toml` before building
- Test the package from TestPyPI before uploading to production PyPI
- Never reuse version numbers - they must be unique
- Keep your `.pypirc` tokens secure

## Build and Upload Process
1. Clean old builds (Important!) - Remove all build artifacts
```bash
rm -rf build/ dist/ *.egg-info/
```
Ff "no egg-info" exists, manually remove .dist 
```bash
rm -rf dist/*
```

2. Build new distribution
```bash
python -m build
```

3. Verify the distribution
```bash
twine check dist/*
```

4. Test Upload (TestPyPI)
```bash
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI (replace 'your-package-name')
pip install --index-url https://test.pypi.org/simple/ your-package-name
```

5. Final Upload (PyPI)
```bash
python -m twine upload dist/*
```



How to upload package to pypi
.pypirc contains the testpypi and pypi token information.
It is located in the home directory. Use CMD + Shift + . to show hidden files

# 1. Check required tools:
python -m pip install --upgrade pip
python -m pip install --upgrade build
python -m pip install --upgrade twine

# 2. Remove the old .tar.gz and .whl files from the dist directory
rm -rf dist/*

# 3. Clean up all build artifacts
rm -rf build/ dist/ *.egg-info/

# 4. Build new distribution
python -m build

# 5. Check the distribution
twine check dist/*

# 6. Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ your-package-name

# 7. Upload to PyPI (when ready)
python -m twine upload dist/*