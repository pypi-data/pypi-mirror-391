# Quick Start Guide - MkDocs Header Dropdown Plugin

## What This Plugin Does

The `mkdocs-header-dropdown` plugin allows you to add configurable dropdown menus to your MkDocs Material theme header. This is perfect for organizations with multiple documentation sites that need cross-linking navigation.

## Installation & Setup (5 Minutes)

### Step 1: Install the Plugin

```bash
# For local development
pip install -e /path/to/mkdocs-header-dropdown-plugin

# OR from Git repository (once published)
pip install git+https://gitlab.cern.ch/cms-analysis/mkdocs-header-dropdown.git
```

### Step 2: Add Plugin Configuration

Add this to your `mkdocs.yml`:

```yaml
plugins:
  - search
  - header-dropdown:
      dropdowns:
        - title: "CMS POG Docs"
          icon: "/assets/CMSlogo_white_nolabel_1024_May2014.png"
          links:
            - text: "Analysis Corrections | CrossPOG"
              url: "https://cms-analysis-corrections.docs.cern.ch/"
              target: "_blank"
            - text: "BTV Docs"
              url: "https://btv-wiki.docs.cern.ch/"
              target: "_blank"
```

### Step 3: Copy Template Files

```bash
# Create overrides directory if it doesn't exist
mkdir -p overrides/partials

# Copy the dropdown template
cp /path/to/plugin/templates/partials/header-dropdown.html overrides/partials/
```

If you don't have a custom header already, also copy the header template:

```bash
cp /path/to/plugin/templates/partials/header.html overrides/partials/
```

If you DO have a custom header, add this line where you want the dropdown:

```jinja
{% include "partials/header-dropdown.html" %}
```

### Step 4: Configure Theme

Make sure your `mkdocs.yml` has:

```yaml
theme:
  name: material
  custom_dir: overrides
```

### Step 5: Build or Serve

```bash
# Build the site
mkdocs build

# Or serve locally
mkdocs serve
```

## For This Project (cat-docs)

### Local Development

Use the new local serve script:

```bash
./serve-local.sh
```

This script:
- Uses your locally installed plugin
- Initializes submodules if needed
- Generates correction digest
- Starts the dev server on http://127.0.0.1:8000

### Using Docker

The original `serve.sh` has been updated to work with the plugin:

```bash
./serve.sh
```

This script:
- Mounts the plugin directory into the Docker container
- Installs the plugin in the container
- Runs mkdocs serve

## Troubleshooting

### "Plugin is not installed" Error

**Solution**: Make sure you installed the plugin in your current Python environment:
```bash
pip install -e /path/to/mkdocs-header-dropdown-plugin
```

Verify installation:
```bash
pip list | grep mkdocs-header-dropdown
```

### Dropdown Not Showing

**Solution**:
1. Check that you copied `header-dropdown.html` to `overrides/partials/`
2. Verify you have `custom_dir: overrides` in your theme config
3. Make sure your header includes `{% include "partials/header-dropdown.html" %}`

### Submodule Issues

If you get file not found errors related to systematics:

```bash
git submodule update --init --recursive
```

## Next Steps

- See [USAGE.md](USAGE.md) for detailed configuration options
- See [DEPLOYMENT.md](DEPLOYMENT.md) for sharing across projects
- See [README.md](README.md) for full documentation

## Example Configuration

Here's a complete example with multiple dropdowns:

```yaml
theme:
  name: material
  custom_dir: overrides

plugins:
  - search
  - header-dropdown:
      dropdowns:
        # Primary dropdown for POG docs
        - title: "CMS POG Docs"
          icon: "/assets/cms-logo.png"
          links:
            - text: "Analysis Corrections"
              url: "https://cms-analysis-corrections.docs.cern.ch/"
              target: "_blank"
            - text: "BTV Wiki"
              url: "https://btv-wiki.docs.cern.ch/"
              target: "_blank"
            - text: "Muon Wiki"
              url: "https://muon-wiki.docs.cern.ch/"
              target: "_blank"

        # Secondary dropdown for tools
        - title: "Tools"
          links:
            - text: "GitLab"
              url: "https://gitlab.cern.ch/cms-analysis"
              target: "_blank"
            - text: "GitHub"
              url: "https://github.com/cms-cat"
              target: "_blank"
```

## Support

- Issues: https://gitlab.cern.ch/cms-analysis/mkdocs-header-dropdown/issues
- Email: cms-phys-conveners-CAT@cern.ch
