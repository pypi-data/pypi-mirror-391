# MkDocs Header Dropdown Plugin

A MkDocs plugin that adds configurable dropdown menus to the Material theme header. This plugin allows you to create cross-documentation navigation menus that can be shared across multiple documentation sites.

## Installation

### From Source (Local Development)

```bash
pip install -e /path/to/mkdocs_header_dropdown
```

### From Git Repository

```bash
pip install git+https://github.com/cms-cat/mkdocs-header-dropdown.git
```

## Quick Start

### Option 1: Using a Shared Config (Recommended for Organizations)

If you're part of an organization with shared documentation links:

```bash
# Add the shared config as a git submodule
git submodule add https://github.com/your-org/docs-common.git
```

```yaml
# mkdocs.yml
plugins:
  - search
  - header-dropdown:
      config_file: "docs-common/header-dropdown.yml"
```

### Option 2: Direct Configuration

For standalone projects:

```yaml
# mkdocs.yml
plugins:
  - search
  - header-dropdown:
      dropdowns:
        - title: "Documentation"
          links:
            - text: "Getting Started"
              url: "/getting-started/"
            - text: "User Guide"
              url: "/guide/"
            - text: "API Reference"
              url: "/api/"
        - title: "External Links"
          links:
            - text: "GitHub Repository"
              url: "https://github.com/your-org/your-project"
              target: "_blank"
```

**That's it!** The plugin automatically provides the necessary templates. No manual template overrides required.

## Configuration Options

### Plugin Configuration

The plugin supports two ways to configure dropdowns, which can be combined:

1. **`config_file`** (string, optional): Load dropdown configuration from a YAML file
   - Path is relative to the repository root
   - Useful for sharing configuration across multiple repositories via git submodules

2. **`dropdowns`** (list, optional): Define dropdowns directly in mkdocs.yml

Both sources are merged together, allowing you to extend shared configs with repository-specific dropdowns.

### Dropdown Configuration

Each dropdown in the `dropdowns` list supports:

- `title` (string, required): The text displayed on the dropdown button
- `icon` (string, optional): Path to an icon image displayed next to the title
- `links` (list, required): List of links in the dropdown menu

### Link Configuration

Each link in the `links` list supports:

- `text` (string, required): The text displayed for the link
- `url` (string, optional): The URL the link points to (not needed if using `submenu`)
- `target` (string, optional): The target attribute (e.g., `_blank` for new tab)
- `submenu` (list, optional): List of nested links for a submenu (see Nested Dropdowns below)

## Example: Using Shared Config File

For multiple repositories that share the same dropdown configuration (e.g., via git submodule):

**Step 1**: Create a shared config repository with `header-dropdown.yml`:
```yaml
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

**Step 2**: Add as git submodule and reference in `mkdocs.yml`:
```bash
git submodule add https://github.com/your-org/cms-docs-config.git
```

```yaml
plugins:
  - header-dropdown:
      config_file: "cms-docs-config/header-dropdown.yml"
```

## Example: Multiple Dropdowns

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
        - title: "External Resources"
          links:
            - text: "GitHub"
              url: "https://github.com/cms-cat"
              target: "_blank"
            - text: "GitLab"
              url: "https://gitlab.cern.ch/cms-analysis"
              target: "_blank"
```

## Example: Nested Dropdowns

Create submenus by using `submenu` instead of `url`:

```yaml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Resources"
          links:
            - text: "GitHub"
              url: "https://github.com/example"
            - text: "Documentation"  # This will show an arrow
              submenu:
                - text: "User Guide"
                  url: "/guide/"
                  target: "_blank"
                - text: "API Reference"
                  url: "/api/"
                - text: "Tutorials"
                  url: "/tutorials/"
```

Nested dropdowns:
- Show an arrow indicator (▶) automatically
- Appear to the right on hover
- Support multiple levels of nesting
- Work with keyboard navigation
```

## Features

- **Shared configuration**: Load dropdown config from external YAML files via git submodules
- **Flexible configuration**: Mix shared configs with repository-specific dropdowns
- **Nested dropdowns**: Create multi-level submenus with arrow indicators
- **Multiple dropdown menus**: Support for any number of dropdowns
- **Configurable icons and titles**: Customize appearance
- **Hover and click interactions**: User-friendly interactions
- **Responsive design**: Works on all screen sizes
- **Theme integration**: Works with Material theme's light and dark modes
- **Accessible**: Keyboard-friendly navigation
- **No manual overrides**: Plugin automatically provides necessary templates

## Requirements

- MkDocs >= 1.4.0
- Material for MkDocs theme

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.
