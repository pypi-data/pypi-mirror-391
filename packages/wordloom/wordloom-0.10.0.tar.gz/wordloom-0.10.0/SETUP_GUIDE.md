# WordLoom Setup Guide

This guide covers setting up GitHub Actions and PyPI publishing for the WordLoom project.

## GitHub Actions Setup

The repository includes two workflows:

### 1. CI Workflow (`.github/workflows/main.yml`)

Runs automatically on every push and pull request. It:
- Tests on Python 3.12 and 3.13
- Runs ruff linting
- Runs pytest test suite

No setup needed; should work automatically once pushed to GitHub.

### 2. Publish Workflow (`.github/workflows/publish.yml`)

Runs when you create a new GitHub release. It builds and publishes to PyPI.

## PyPI Publishing Setup

You have two options for authentication:

### Option A: Trusted Publishing (RECOMMENDED)

This is the modern, more secure approach that doesn't require managing API tokens.

**What does the environment name do?**

Using an environment name (`pypi`) adds an extra layer of protection:
- **Without environment**: Workflow runs automatically when you create a release
- **With environment**: You can add protection rules like:
  - Required reviewers (manual approval before publishing)
  - Wait timers (delay before publishing)
  - Branch restrictions

This prevents accidental publishes and gives you a chance to review before releasing.

**Note**: If you want simpler setup (no manual approval), you can:
- Leave the environment name blank on PyPI, OR
- Remove the `environment: pypi` line from the workflow

But using the environment is recommended for production packages.

**Steps:**

1. **On PyPI** (https://pypi.org):
   - Log in to your PyPI account
   - If this is a new package:
     - Go to: https://pypi.org/manage/account/publishing/
     - Click "Add a new pending publisher"
     - Fill in:
       - **PyPI Project Name**: `wordloom` (must match `name` in pyproject.toml)
       - **Owner**: `OoriData`
       - **Repository name**: `WordLoom`
       - **Workflow name**: `publish.yml`
       - **Environment name**: `pypi` (PyPI's recommended name)
   - If the package already exists on PyPI:
     - Go to the project page: https://pypi.org/manage/project/wordloom/settings/publishing/
     - Add the publisher configuration as above

2. **On GitHub**:
   - Go to: https://github.com/OoriData/WordLoom/settings/environments
   - Click "New environment"
   - Name: `pypi`
   - Click "Configure environment"
   - (Optional) Add protection rules:
     - Required reviewers: Add yourself to require manual approval before publishing
     - Wait timer: Add a delay (e.g., 5 minutes) before publishing
   - Click "Save protection rules"

3. **Update the workflow**:
   Edit `.github/workflows/publish.yml` and add the environment to the job:
   ```yaml
   jobs:
     publish:
       runs-on: ubuntu-latest
       environment: pypi  # Add this line
       permissions:
         id-token: write
   ```

4. **Publishing a release**:
   ```bash
   # Make sure version is updated in pylib/__about__.py
   git tag v0.10.0
   git push origin v0.10.0

   # Or create a release via GitHub UI:
   # Go to: https://github.com/OoriData/WordLoom/releases/new
   # - Tag: v0.10.0
   # - Title: v0.10.0
   # - Description: Release notes
   # - Click "Publish release"
   ```

### Option B: API Token (Fallback)

If trusted publishing doesn't work or you prefer tokens:

**Steps:**

1. **On PyPI** (https://pypi.org):
   - Go to Account Settings → API tokens
   - Create a new token:
     - Name: `wordloom-github-actions`
     - Scope: "Project: wordloom" (after first manual upload) or "Entire account" (for first upload)
   - Copy the token (starts with `pypi-`)

2. **On GitHub**:
   - Go to: https://github.com/OoriData/WordLoom/settings/secrets/actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: paste your PyPI token
   - Click "Add secret"

3. **Update the workflow**:
   In `.github/workflows/publish.yml`, uncomment the password line:
   ```yaml
   - name: Publish to PyPI
     uses: pypa/gh-action-pypi-publish@release/v1
     with:
       password: ${{ secrets.PYPI_API_TOKEN }}  # Uncomment this line
   ```

## First Time Publishing

For the very first release to PyPI, you may want to do a manual publish to ensure everything is set up correctly:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the build
twine check dist/*

# Upload to Test PyPI first (optional but recommended)
twine upload --repository testpypi dist/*
# Username: __token__
# Password: your-test-pypi-token

# If test looks good, upload to real PyPI
twine upload dist/*
# Username: __token__
# Password: your-pypi-token
```

After the first manual upload, you can use trusted publishing for all future releases.

## Release Checklist

Before creating a release:

- [ ] Update version in `pylib/__about__.py`
- [ ] Update CHANGELOG (if you have one)
- [ ] Run tests locally: `pytest test/ -v`
- [ ] Run linting: `ruff check .`
- [ ] Commit and push all changes
- [ ] Create git tag: `git tag v0.X.Y`
- [ ] Push tag: `git push origin v0.X.Y`
- [ ] Create GitHub release (triggers publish workflow)
- [ ] Verify package appears on PyPI: https://pypi.org/project/wordloom/

## Testing the Package

After publishing, test the installation:

```bash
# Create a fresh virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from PyPI
pip install wordloom

# Test import
python -c "import wordloom; print(wordloom.__version__)"

# Test basic functionality
python -c "
import wordloom
import io

toml_data = b'''
lang = 'en'
[test]
_ = 'Hello'
'''

loom = wordloom.load(io.BytesIO(toml_data))
print(loom['test'])
"
```

## Troubleshooting

### "Project name 'wordloom' is not valid"
- Check that the name in `pyproject.toml` matches exactly
- Names are case-insensitive but must match what you registered on PyPI

### "Invalid or non-existent authentication information"
- For trusted publishing: Double-check the repository name, owner, and workflow name
- For token auth: Make sure the token is saved as `PYPI_API_TOKEN` in GitHub secrets

### Workflow fails with "Resource not accessible by integration"
- Make sure the workflow has `id-token: write` permission
- Check that the repository settings allow GitHub Actions

### Package version already exists
- You can't overwrite versions on PyPI
- Increment the version in `pylib/__about__.py` and create a new release

## Additional Resources

- [PyPI Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
- [Python Packaging Guide](https://packaging.python.org/en/latest/)
