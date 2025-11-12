# WordLoom Quick Reference

## Daily Development

```bash
# Install in current virtualenv
uv pip install -U .

# Run tests
pytest test/ -v

# Run specific test file
pytest test/test_basics.py -v

# Run linting
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Run tests with coverage
pytest test/ --cov=wordloom --cov-report=html
```

## Making Changes

```bash
# After editing any Python files in pylib/
uv pip install -U .

# After editing resources/
uv pip install -U .

# After editing tests only (no reinstall needed)
pytest test/ -v
```

## Publishing a New Version

```bash
# 1. Update version
edit pylib/__about__.py  # Change __version__ = '0.X.Y'

# 2. Test everything
pytest test/ -v
ruff check .

# 3. Commit changes
git add .
git commit -m "Release v0.X.Y"
git push

# 4. Create and push tag
git tag v0.X.Y
git push origin v0.X.Y

# 5. Create GitHub release
# Go to: https://github.com/OoriData/WordLoom/releases/new
# - Select the tag you just created
# - Write release notes
# - Click "Publish release"

# 6. Approve deployment (if using pypi environment)
# Go to: https://github.com/OoriData/WordLoom/actions
# - Click on the running "Publish to PyPI" workflow
# - Review and click "Approve deployment"
# - The package will then upload to PyPI
```

## Testing Package Locally

```bash
# Build locally
python -m build

# Test the built wheel
pip install dist/wordloom-0.X.Y-py3-none-any.whl --force-reinstall

# Check package contents
unzip -l dist/wordloom-0.X.Y-py3-none-any.whl
```

## Common Issues

**Tests fail after code changes:**
```bash
# Make sure you reinstalled!
uv pip install -U .
pytest test/ -v
```

**Import errors in tests:**
```bash
# Check package is installed
pip list | grep wordloom

# Reinstall
uv pip install -U .
```

**Version mismatch:**
```bash
# Check installed version
python -c "import wordloom; print(wordloom.__version__)"

# Check source version
cat pylib/__about__.py
```

## Project Structure

```
WordLoom/
├── pylib/              # Source code (becomes 'wordloom' package)
│   ├── __init__.py
│   ├── __about__.py    # Version info
│   └── wordloom.py     # Main implementation
├── resources/          # Bundled resources
│   └── wordloom/
│       └── sample.toml
├── test/               # Tests
│   ├── test_basics.py
│   ├── test_i18n_integration.py
│   └── test_openai_integration.py
├── pyproject.toml      # Project config
└── README.md

When installed, becomes:
site-packages/
└── wordloom/
    ├── __init__.py
    ├── __about__.py
    ├── wordloom.py
    └── resources/
        └── wordloom/
            └── sample.toml
```

## Key Files

- **pylib/__about__.py** - Version number (update for releases)
- **pyproject.toml** - Dependencies, metadata, build config
- **resources/wordloom/sample.toml** - Sample file used by tests
- **README.md** - Main documentation
- **wordloom_spec.md** - Format specification (CC BY 4.0)

## Useful Commands

```bash
# See package structure after install
python -c "import wordloom, os; print(os.path.dirname(wordloom.__file__))"
ls -la $(python -c "import wordloom, os; print(os.path.dirname(wordloom.__file__))")

# Check what files are in the installed package
pip show -f wordloom

# Uninstall completely
pip uninstall wordloom -y

# Clean build artifacts
rm -rf build/ dist/ *.egg-info
rm -rf .pytest_cache .ruff_cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```
