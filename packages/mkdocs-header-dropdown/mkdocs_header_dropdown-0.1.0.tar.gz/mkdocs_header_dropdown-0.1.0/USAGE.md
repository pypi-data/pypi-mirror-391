# MkDocs Header Dropdown Plugin - Usage Guide

## Overview

The MkDocs Header Dropdown Plugin allows you to create reusable dropdown navigation menus in the header of your MkDocs Material-themed documentation sites. This is particularly useful for organizations with multiple documentation sites that need to cross-link to each other.

## Quick Start

### 1. Install the Plugin

For local development:
```bash
pip install -e /path/to/mkdocs-header-dropdown-plugin
```

From a Git repository:
```bash
pip install git+https://gitlab.cern.ch/cms-analysis/mkdocs-header-dropdown.git
```

### 2. Configure Your mkdocs.yml

Add the plugin to your `mkdocs.yml` file with your dropdown configuration:

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

### 3. Update Your Header Template

You have two options:

#### Option A: Replace Your Entire Header (Recommended)

Copy the `overrides/partials/header.html` from this project to your project's `overrides/partials/` directory. This provides a clean, complete header implementation with dropdown support.

#### Option B: Add to Existing Header

If you already have a custom header, add this line where you want the dropdown to appear (typically after the search interface):

```jinja
<!-- Header dropdown menus from plugin -->
{% include "partials/header-dropdown.html" %}
```

Also copy the `overrides/partials/header-dropdown.html` file from this project to your `overrides/partials/` directory.

### 4. Set Up Theme Overrides

Make sure your `mkdocs.yml` has the custom directory configured:

```yaml
theme:
  name: material
  custom_dir: overrides
```

### 5. Build and Test

```bash
mkdocs build
# or
mkdocs serve
```

## Configuration Reference

### Plugin Configuration

The plugin accepts a single `dropdowns` parameter, which is a list of dropdown configurations.

```yaml
plugins:
  - header-dropdown:
      dropdowns:
        - [dropdown configuration 1]
        - [dropdown configuration 2]
```

### Dropdown Configuration

Each dropdown supports the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | The text displayed on the dropdown button |
| `icon` | string | No | Path to an icon image (relative to docs directory) |
| `links` | list | Yes | List of links to display in the dropdown menu |

### Link Configuration

Each link in the `links` list supports:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | The link text |
| `url` | string | Yes | The target URL (can be relative or absolute) |
| `target` | string | No | HTML target attribute (e.g., `_blank` for new tab) |

## Advanced Examples

### Multiple Dropdowns

You can add multiple dropdown menus to your header:

```yaml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "CMS POG Docs"
          icon: "/assets/cms-logo.png"
          links:
            - text: "BTV Docs"
              url: "https://btv-wiki.docs.cern.ch/"
              target: "_blank"
            - text: "JetMet TWiki"
              url: "https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetMET"
              target: "_blank"

        - title: "External Resources"
          links:
            - text: "GitHub Organization"
              url: "https://github.com/cms-cat"
              target: "_blank"
            - text: "GitLab Organization"
              url: "https://gitlab.cern.ch/cms-analysis"
              target: "_blank"
```

### Dropdown Without Icon

You can create a text-only dropdown by omitting the `icon` field:

```yaml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Related Docs"
          links:
            - text: "Documentation 1"
              url: "https://example.com/docs1"
            - text: "Documentation 2"
              url: "https://example.com/docs2"
```

### Internal Links

You can use relative URLs for internal navigation:

```yaml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Quick Links"
          links:
            - text: "Getting Started"
              url: "/getting-started/"
            - text: "API Reference"
              url: "/api/"
```

## Sharing the Plugin Across Projects

### Method 1: Git Repository

1. Create a Git repository for the plugin:
   ```bash
   cd mkdocs-header-dropdown-plugin
   git init
   git add .
   git commit -m "Initial plugin release"
   git remote add origin https://gitlab.cern.ch/your-org/mkdocs-header-dropdown.git
   git push -u origin main
   ```

2. In other projects, install from Git:
   ```bash
   pip install git+https://gitlab.cern.ch/your-org/mkdocs-header-dropdown.git
   ```

3. Add to each project's `requirements.txt`:
   ```
   git+https://gitlab.cern.ch/your-org/mkdocs-header-dropdown.git
   ```

### Method 2: PyPI (for Public Release)

1. Build the package:
   ```bash
   cd mkdocs-header-dropdown-plugin
   python -m build
   ```

2. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```

3. Install in projects:
   ```bash
   pip install mkdocs-header-dropdown
   ```

### Method 3: Local Network Share

For internal use without a package repository:

1. Place the plugin on a shared network location
2. In each project, install with:
   ```bash
   pip install -e /path/to/shared/mkdocs-header-dropdown-plugin
   ```

## Customization

### Styling

The dropdown uses CSS variables from the Material theme for colors and styling. If you need custom styling, add CSS to your `extra_css` files:

```css
/* custom.css */
.md-header__dropdown-content {
    min-width: 250px !important;
}

.md-header__dropdown-content a {
    font-size: 0.8rem !important;
}
```

Then include it in `mkdocs.yml`:

```yaml
extra_css:
  - stylesheets/custom.css
```

### JavaScript Behavior

The dropdown includes both hover and click interactions by default. The behavior is defined in the `header-dropdown.html` template and can be customized by modifying that file.

## Troubleshooting

### Plugin Not Found Error

**Problem**: `The "header-dropdown" plugin is not installed`

**Solution**: Make sure you've installed the plugin:
```bash
pip install -e /path/to/mkdocs-header-dropdown-plugin
```

### Dropdown Not Appearing

**Problem**: The dropdown doesn't show up in the header

**Solutions**:
1. Verify you've copied the `header-dropdown.html` partial to `overrides/partials/`
2. Check that your header template includes the line:
   ```jinja
   {% include "partials/header-dropdown.html" %}
   ```
3. Ensure `custom_dir: overrides` is set in your theme configuration

### Configuration Not Loading

**Problem**: Dropdown shows but links are missing

**Solutions**:
1. Verify your YAML indentation is correct
2. Check that the plugin is listed before other plugins that might interfere
3. Ensure the `dropdowns` configuration is under the `header-dropdown` plugin entry

### Recursion Error

**Problem**: `RecursionError: maximum recursion depth exceeded`

**Solution**: Make sure any Jinja2 template tags in HTML comments are escaped:
```jinja
{%raw%}{% include "..." %}{%endraw%}
```

## Migration Guide

### From Hardcoded Dropdown to Plugin

If you currently have a hardcoded dropdown in your header:

1. Extract your dropdown configuration into the plugin format in `mkdocs.yml`
2. Replace your hardcoded HTML with `{% include "partials/header-dropdown.html" %}`
3. Copy the `header-dropdown.html` template to your overrides directory
4. Test the build

Example transformation:

**Before** (in header.html):
```html
<div class="md-header__option">
  <button>Links</button>
  <div class="dropdown">
    <a href="https://example.com">Example</a>
  </div>
</div>
```

**After** (in mkdocs.yml):
```yaml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Links"
          links:
            - text: "Example"
              url: "https://example.com"
              target: "_blank"
```

**After** (in header.html):
```jinja
{% include "partials/header-dropdown.html" %}
```

## Support

For issues, feature requests, or contributions, please visit:
https://gitlab.cern.ch/cms-analysis/mkdocs-header-dropdown/issues
