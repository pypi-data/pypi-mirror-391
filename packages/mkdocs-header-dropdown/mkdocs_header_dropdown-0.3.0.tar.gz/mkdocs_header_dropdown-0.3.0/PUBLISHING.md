# Publishing to PyPI

This guide explains how to publish the `mkdocs-header-dropdown` plugin to PyPI.

## Prerequisites

1. Install build tools:
```bash
pip install --upgrade build twine
```

2. Create PyPI account:
   - Go to https://pypi.org/account/register/
   - Verify your email address

3. Create a PyPI API token:
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token with scope "Entire account" or specific to this project
   - Save the token securely (it will only be shown once)

## Publishing Steps

### 1. Update Version Number

Before publishing, update the version number in:
- `pyproject.toml` (line 7)
- `setup.py` (line 8)

Follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### 2. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### 3. Build the Package

```bash
python -m build
```

This creates two distribution files in the `dist/` directory:
- `.tar.gz` (source distribution)
- `.whl` (wheel distribution)

### 4. Validate the Package

```bash
twine check dist/*
```

Both files should pass validation.

### 5. Test Upload to TestPyPI (Optional but Recommended)

Before publishing to the real PyPI, test on TestPyPI:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

When prompted:
- Username: `__token__`
- Password: Your TestPyPI API token (starts with `pypi-`)

Then test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ mkdocs-header-dropdown
```

### 6. Upload to PyPI

Once you're satisfied with the test:

```bash
twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

### 7. Verify Publication

Visit https://pypi.org/project/mkdocs-header-dropdown/ to see your published package.

Test installation:
```bash
pip install mkdocs-header-dropdown
```

## Using API Tokens (Recommended)

Instead of entering credentials each time, configure them in `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

**Important:** Keep this file secure and never commit it to version control!

Set proper permissions:
```bash
chmod 600 ~/.pypirc
```

## Automated Publishing with GitHub Actions (RECOMMENDED)

This repository includes automated GitHub Actions workflows in `.github/workflows/`:

### CD Workflow (Continuous Deployment)

The `cd.yml` workflow automatically:
- **Builds** the package on every push and PR (for testing)
- **Publishes** to PyPI when you create a GitHub release

### Setup Steps for Automated Publishing

#### 1. Configure PyPI Trusted Publishing (No API tokens needed!)

This is the modern, secure way to publish to PyPI:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher with:
   - **PyPI Project Name**: `mkdocs-header-dropdown`
   - **Owner**: `cms-cat` (your GitHub username/org)
   - **Repository name**: `mkdocs-header-dropdown`
   - **Workflow name**: `cd.yml`
   - **Environment name**: `release`

3. That's it! No API tokens needed.

#### 2. Create a GitHub Environment (Optional but Recommended)

1. Go to your repository's Settings → Environments
2. Create a new environment named `release`
3. Add protection rules:
   - Require reviewers (optional)
   - Limit to specific branches (e.g., `main`)

#### 3. Create a Release

When you're ready to publish:

```bash
# Update version in pyproject.toml and setup.py first!

# Commit and push changes
git add pyproject.toml setup.py
git commit -m "Bump version to 0.2.0"
git push

# Create and push a tag
git tag v0.2.0
git push origin v0.2.0

# Create a GitHub release
# Go to https://github.com/cms-cat/mkdocs-header-dropdown/releases/new
# Or use the GitHub CLI:
gh release create v0.2.0 --title "v0.2.0" --notes "Release notes here"
```

The CD workflow will automatically:
1. Build the distribution packages
2. Verify them
3. Publish to PyPI

### Alternative: Using API Tokens

If you prefer the traditional approach with API tokens:

1. Create a PyPI API token at https://pypi.org/manage/account/token/
2. Add it as a GitHub secret:
   - Go to Settings → Secrets and variables → Actions
   - Add a new repository secret named `PYPI_API_TOKEN`
   - Paste your token

3. Modify `.github/workflows/cd.yml` to use token auth instead of trusted publishing (replace the `permissions: id-token: write` section with environment variables).

## Troubleshooting

### "File already exists" error
PyPI doesn't allow re-uploading the same version. You must increment the version number.

### Import errors after installation
Make sure templates are properly included in the package by checking:
```bash
python -m zipfile -l dist/*.whl
```

### Authentication issues
- Ensure you're using `__token__` as the username (not your PyPI username)
- Check that your API token hasn't expired
- Verify token permissions include upload rights

## Post-Publication

After publishing:
1. Create a git tag for the release:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. Create a GitHub release with release notes

3. Update the CHANGELOG.md file

4. Announce the release in relevant communities

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)
