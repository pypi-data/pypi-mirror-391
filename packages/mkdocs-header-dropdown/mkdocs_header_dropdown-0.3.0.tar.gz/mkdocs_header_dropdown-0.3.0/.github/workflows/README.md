# GitHub Actions Workflows

This directory contains automated workflows for continuous integration and deployment.

## Workflows

### CI (Continuous Integration) - `ci.yml`

**Triggers:** Push to `main`, Pull Requests, Manual dispatch

**Purpose:** Test the package across multiple Python versions and operating systems.

**Jobs:**
- **test**: Runs on Python 3.8-3.12 across Ubuntu, macOS, and Windows
  - Installs the package
  - Tests imports
  - Validates plugin registration with MkDocs

- **lint**: Code quality checks using ruff

### CD (Continuous Deployment) - `cd.yml`

**Triggers:** Push to `main`, Pull Requests, Releases, Manual dispatch

**Purpose:** Build distribution packages and publish to PyPI on releases.

**Jobs:**
- **dist**: Builds and inspects the Python package using `hynek/build-and-inspect-python-package`
  - Runs on all triggers (for validation)
  - Creates source distribution (`.tar.gz`) and wheel (`.whl`)
  - Uploads as artifacts

- **publish**: Publishes to PyPI using trusted publishing
  - **Only runs on release events** (when you publish a GitHub release)
  - Uses PyPI's trusted publishing (no API tokens needed)
  - Requires the `release` environment
  - Downloads build artifacts from the `dist` job
  - Publishes to https://pypi.org/project/mkdocs-header-dropdown/

### Deploy Docs - `deploy-docs.yml`

**Purpose:** Deploys documentation site (existing workflow).

## Setup Required

### For CD Workflow (PyPI Publishing)

1. **Configure PyPI Trusted Publishing:**
   - Go to https://pypi.org/manage/account/publishing/
   - Add publisher for this repository
   - See `PUBLISHING.md` for detailed instructions

2. **Create GitHub Environment (optional but recommended):**
   - Repository Settings → Environments → New environment
   - Name it `release`
   - Add branch protection rules if desired

## Usage

### Running Tests

Tests run automatically on every push and PR. To manually trigger:

```bash
# Via GitHub UI: Actions tab → CI → Run workflow
# Or use GitHub CLI:
gh workflow run ci.yml
```

### Publishing a Release

1. Update version in `pyproject.toml` and `setup.py`
2. Commit and push changes
3. Create a git tag: `git tag v0.1.0 && git push origin v0.1.0`
4. Create a GitHub release (via UI or `gh release create`)
5. The CD workflow automatically publishes to PyPI

See `PUBLISHING.md` for complete instructions.

## Badges

Add these badges to your README:

```markdown
[![CI](https://github.com/cms-cat/mkdocs-header-dropdown/actions/workflows/ci.yml/badge.svg)](https://github.com/cms-cat/mkdocs-header-dropdown/actions/workflows/ci.yml)
[![CD](https://github.com/cms-cat/mkdocs-header-dropdown/actions/workflows/cd.yml/badge.svg)](https://github.com/cms-cat/mkdocs-header-dropdown/actions/workflows/cd.yml)
[![PyPI](https://img.shields.io/pypi/v/mkdocs-header-dropdown)](https://pypi.org/project/mkdocs-header-dropdown/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mkdocs-header-dropdown)](https://pypi.org/project/mkdocs-header-dropdown/)
```
