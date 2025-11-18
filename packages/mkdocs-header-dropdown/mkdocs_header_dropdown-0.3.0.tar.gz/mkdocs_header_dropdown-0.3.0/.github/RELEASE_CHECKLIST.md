# Release Checklist

Quick reference for publishing a new release to PyPI.

## Pre-Release

- [ ] All tests passing on main branch
- [ ] CHANGELOG.md updated with release notes
- [ ] Version bumped in:
  - [ ] `pyproject.toml` (line 7)
  - [ ] `setup.py` (line 8)
- [ ] Changes committed and pushed to main

## Release Process

### 1. Create Git Tag

```bash
# Replace 0.1.0 with your version
VERSION="0.1.0"
git tag v${VERSION}
git push origin v${VERSION}
```

### 2. Create GitHub Release

**Option A: GitHub CLI**
```bash
gh release create v${VERSION} \
  --title "v${VERSION}" \
  --notes-file CHANGELOG.md
```

**Option B: GitHub Web UI**
1. Go to https://github.com/cms-cat/mkdocs-header-dropdown/releases/new
2. Choose tag: `v0.1.0`
3. Release title: `v0.1.0`
4. Copy release notes from CHANGELOG.md
5. Click "Publish release"

### 3. Verify Automatic Publishing

The CD workflow automatically:
- ✅ Builds source and wheel distributions
- ✅ Runs quality checks
- ✅ Publishes to PyPI

Monitor progress:
https://github.com/cms-cat/mkdocs-header-dropdown/actions/workflows/cd.yml

## Post-Release

- [ ] Verify package appears on PyPI: https://pypi.org/project/mkdocs-header-dropdown/
- [ ] Test installation: `pip install mkdocs-header-dropdown==${VERSION}`
- [ ] Verify plugin works in a test project
- [ ] Update documentation if needed
- [ ] Announce release (optional)

## First Release Only

Before the very first release, configure PyPI Trusted Publishing:

1. Go to https://pypi.org/manage/account/publishing/
2. Add pending publisher:
   - **PyPI Project Name**: `mkdocs-header-dropdown`
   - **Owner**: `cms-cat`
   - **Repository**: `mkdocs-header-dropdown`
   - **Workflow**: `cd.yml`
   - **Environment**: `release`

## Troubleshooting

### Workflow Failed
- Check Actions tab for error details
- Common issues:
  - PyPI trusted publishing not configured
  - Version already exists on PyPI (bump version)
  - Build errors (test with `python -m build` locally)

### Package Not Appearing on PyPI
- Verify the release was published (not just created as draft)
- Check workflow completed successfully
- Wait a few minutes for PyPI to index

### Import Errors After Installation
- Verify templates included: `python -m zipfile -l dist/*.whl`
- Check MANIFEST.in includes all necessary files

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features (backward compatible)
- **PATCH** (0.0.X): Bug fixes

Examples:
- `0.1.0` → `0.1.1`: Bug fix
- `0.1.0` → `0.2.0`: New feature
- `0.9.0` → `1.0.0`: Stable release or breaking change

## Quick Commands

```bash
# Check current version
grep '^version = ' pyproject.toml

# Test build locally
python -m build
twine check dist/*

# Clean build artifacts
rm -rf dist/ build/ *.egg-info

# View releases
gh release list

# View workflow runs
gh run list --workflow=cd.yml
```

## Resources

- Full guide: `PUBLISHING.md`
- Workflow details: `.github/workflows/README.md`
- PyPI package: https://pypi.org/project/mkdocs-header-dropdown/
- GitHub releases: https://github.com/cms-cat/mkdocs-header-dropdown/releases
