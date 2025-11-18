# PyPI Setup Summary

This document summarizes the changes made to set up this repository for PyPI publication.

## Changes Made

### 1. Package Structure
- **Moved templates**: Relocated `templates/` into `mkdocs_header_dropdown/templates/`
- **Updated plugin code**: Modified `mkdocs_header_dropdown/plugin.py:75` to reference templates from package directory

### 2. Configuration Files

#### `pyproject.toml`
- Modernized license format: `{text = "MIT"}` → `"MIT"` (SPDX format)
- Removed deprecated license classifier
- Added keywords for PyPI search: `["mkdocs", "plugin", "dropdown", "navigation", "material-theme", "documentation"]`
- Added maintainers field
- Added `pyyaml` dependency
- Enhanced project URLs (Issues, Documentation)
- Updated Python version support (3.7-3.12)
- Fixed package data configuration

#### `MANIFEST.in` (new)
- Includes README.md, LICENSE, CHANGELOG.md, and other docs
- Recursively includes all template files

### 3. GitHub Actions Workflows

#### `.github/workflows/ci.yml` (new)
Tests the package across multiple environments:
- **Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Operating systems**: Ubuntu, macOS, Windows
- **Checks**:
  - Package installation
  - Import verification
  - Plugin registration
  - Code linting (ruff)

#### `.github/workflows/cd.yml` (new)
Automates building and publishing:
- **Builds** distributions on every push/PR (for validation)
- **Publishes to PyPI** automatically when you create a GitHub release
- Uses **PyPI Trusted Publishing** (no API tokens needed!)
- Leverages `hynek/build-and-inspect-python-package` for quality checks

### 4. Documentation

#### `PUBLISHING.md` (new)
Complete guide covering:
- Manual publishing steps
- Automated publishing with GitHub Actions
- PyPI Trusted Publishing setup
- Testing with TestPyPI
- Troubleshooting common issues
- Post-publication checklist

#### `.github/workflows/README.md` (new)
Documentation for the workflows:
- What each workflow does
- When they run
- How to use them
- Setup requirements

## Build Verification

Package successfully builds and validates:
```bash
$ python -m build
Successfully built mkdocs_header_dropdown-0.1.0.tar.gz and mkdocs_header_dropdown-0.1.0-py3-none-any.whl

$ twine check dist/*
Checking dist/mkdocs_header_dropdown-0.1.0-py3-none-any.whl: PASSED
Checking dist/mkdocs_header_dropdown-0.1.0.tar.gz: PASSED
```

Package includes all necessary files:
- ✅ Python code (`mkdocs_header_dropdown/*.py`)
- ✅ Templates (`mkdocs_header_dropdown/templates/**/*.html`)
- ✅ Metadata (LICENSE, README.md)

## Next Steps to Publish

### One-Time Setup

1. **Configure PyPI Trusted Publishing:**
   ```
   1. Go to: https://pypi.org/manage/account/publishing/
   2. Add new pending publisher:
      - PyPI Project Name: mkdocs-header-dropdown
      - Owner: cms-cat
      - Repository: mkdocs-header-dropdown
      - Workflow: cd.yml
      - Environment: release
   ```

2. **Create GitHub Environment (optional):**
   ```
   Repository Settings → Environments → New environment
   Name: release
   ```

### Publishing a Release

```bash
# 1. Update version numbers
# Edit: pyproject.toml (line 7) and setup.py (line 8)

# 2. Commit changes
git add pyproject.toml setup.py
git commit -m "Bump version to 0.1.0"
git push

# 3. Create and push tag
git tag v0.1.0
git push origin v0.1.0

# 4. Create GitHub release
gh release create v0.1.0 --title "v0.1.0" --notes "Initial release"
```

The CD workflow automatically handles the rest!

## Files to Commit

New files:
- `.github/workflows/ci.yml`
- `.github/workflows/cd.yml`
- `.github/workflows/README.md`
- `MANIFEST.in`
- `PUBLISHING.md`
- `SETUP_SUMMARY.md`
- `mkdocs_header_dropdown/templates/` (moved from root)

Modified files:
- `pyproject.toml`
- `mkdocs_header_dropdown/plugin.py`

Deleted files:
- `templates/` (moved into package)

## Testing Before First Release

Before creating the first release, test the workflow:

1. Push changes to GitHub
2. Check that CI workflow runs successfully
3. Verify CD workflow builds distributions (doesn't publish until release)
4. Review the artifacts in the Actions tab

## Resources

- See `PUBLISHING.md` for detailed publishing instructions
- See `.github/workflows/README.md` for workflow documentation
- GitHub Actions: https://github.com/cms-cat/mkdocs-header-dropdown/actions
- PyPI Trusted Publishing: https://docs.pypi.org/trusted-publishers/

## Inspiration

This setup was inspired by [scikit-hep/mplhep](https://github.com/scikit-hep/mplhep), which follows modern Python packaging best practices.
