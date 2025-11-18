# Docker Setup for mkdocs-header-dropdown

This document explains how the plugin is integrated into Docker images for documentation builds.

## Overview

The plugin is available in two ways:
1. **PyPI package** - `mkdocs-header-dropdown` (published at https://pypi.org/project/mkdocs-header-dropdown/)
2. **Docker image** - Pre-installed in the `ghcr.io/cms-cat/mkdocs-material` image

## Docker Image Integration

### Repository Structure

The Docker image is maintained in: `/home/anovak/code/mkdocs-material`

Key files:
- `Dockerfile` - Builds the image with mkdocs-material and plugins
- `requirements.txt` - Contains `mkdocs-material==9.7.0`
- `requirements-plugins.txt` - Contains all MkDocs plugins including `mkdocs-header-dropdown==0.1.0`

### Plugin Installation in Docker

The plugin is installed via `requirements-plugins.txt`:

```txt
mkdocs-header-dropdown==0.1.0
```

When the Docker image is built:
1. Installs mkdocs-material from `requirements.txt`
2. Installs all plugins from `requirements-plugins.txt` (if `WITH_PLUGINS=true`)
3. The plugin is installed from PyPI automatically

## Using the Docker Image

### Production Use (Remote Image)

The published Docker image is available at `ghcr.io/cms-cat/mkdocs-material`.

Use `serve.sh` in the cat-docs repository:

```bash
./serve.sh [port] [host]
```

This pulls and runs the latest published image.

### Development Use (Local Image)

For testing changes before publishing the Docker image:

1. **Build the local image:**
   ```bash
   cd /home/anovak/code/mkdocs-material
   docker build -t mkdocs-material-local:latest .
   ```

2. **Use the local image:**
   ```bash
   cd /home/anovak/code/cat-docs
   ./serve-local-docker.sh [port] [host]
   ```

### Serve Scripts Comparison

| Script | Image Used | Purpose |
|--------|-----------|---------|
| `serve.sh` | `ghcr.io/cms-cat/mkdocs-material` (remote) | Production use with published image |
| `serve-local-docker.sh` | `mkdocs-material-local:latest` (local) | Testing with locally-built image |
| `serve-local.sh` | None (uses local Python) | Development without Docker |

## Updating the Plugin in Docker

When a new version of the plugin is released:

### 1. Update requirements-plugins.txt

```bash
cd /home/anovak/code/mkdocs-material
# Edit requirements-plugins.txt to update version
vim requirements-plugins.txt
# Change: mkdocs-header-dropdown==0.1.0
# To:     mkdocs-header-dropdown==0.2.0
```

### 2. Commit the change

```bash
git add requirements-plugins.txt
git commit -m "chore: Update mkdocs-header-dropdown to 0.2.0"
git push
```

### 3. Rebuild and publish the Docker image

This is typically automated via CI/CD when you push to the repository.

If building manually:
```bash
docker build -t ghcr.io/cms-cat/mkdocs-material:latest .
docker push ghcr.io/cms-cat/mkdocs-material:latest
```

### 4. Update cat-docs requirements.txt

```bash
cd /home/anovak/code/cat-docs
# Edit requirements.txt
vim requirements.txt
# Change: mkdocs-header-dropdown~=0.1.0
# To:     mkdocs-header-dropdown~=0.2.0
```

## Verification

After building the Docker image, verify the plugin is installed:

```bash
docker run --rm mkdocs-material-local:latest pip list | grep mkdocs-header-dropdown
```

Expected output:
```
mkdocs-header-dropdown    0.1.0
```

## Troubleshooting

### Plugin not found error

If you see:
```
ERROR - Config value 'plugins': The "header-dropdown" plugin is not installed
```

**Solution:** Rebuild the Docker image with the plugin in requirements-plugins.txt

```bash
cd /home/anovak/code/mkdocs-material
docker build -t mkdocs-material-local:latest .
```

### Version mismatch

If the wrong version is installed, check:
1. `requirements-plugins.txt` has the correct version
2. Docker build cache - try `docker build --no-cache`
3. You're using the correct image (local vs remote)

## Related Files

In `mkdocs-material` repository:
- `Dockerfile` - Docker image definition
- `requirements.txt` - MkDocs Material version
- `requirements-plugins.txt` - All plugins including mkdocs-header-dropdown

In `cat-docs` repository:
- `requirements.txt` - Python dependencies (for local development)
- `serve.sh` - Uses remote Docker image
- `serve-local-docker.sh` - Uses local Docker image
- `serve-local.sh` - Uses local Python (no Docker)
- `mkdocs.yml` - MkDocs configuration with plugin settings

## Resources

- Plugin PyPI page: https://pypi.org/project/mkdocs-header-dropdown/
- Plugin GitHub: https://github.com/cms-cat/mkdocs-header-dropdown
- Docker image: ghcr.io/cms-cat/mkdocs-material
