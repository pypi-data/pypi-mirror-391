# MkDocs Header Dropdown Plugin

Add configurable dropdown menus to your MkDocs Material theme header for easy cross-documentation navigation.

## Features

- **Simple Configuration**: Define dropdown menus in YAML - no template overrides needed
- **Shared Configs**: Load from external files via git submodules - perfect for organizations
- **Nested Menus**: Create multi-level submenus with automatic arrow indicators
- **Customizable**: Add icons, customize titles, and style to match your theme
- **Theme Integration**: Works seamlessly with Material theme's light and dark modes
- **Accessible**: Keyboard-friendly navigation and screen reader support

## Live Demo

Look at the header above to see the plugin in action! The dropdowns demonstrate:

- **CMS POG Docs**: External links with icon (shared config via git submodule)
- **Examples**: Internal site links (direct mkdocs.yml configuration)
- **Resources**: Mixed with nested menu (hover over "Documentation" to see submenu)

## Quick Start

### For Organizations (Shared Links)

Perfect when multiple documentation sites need the same navigation:

```bash
# Add shared config as git submodule
git submodule add https://github.com/your-org/docs-common.git
```

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      config_file: "docs-common/header-dropdown.yml"
```

### For Standalone Projects

Ideal for single projects with unique navigation:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Documentation"
          links:
            - text: "Getting Started"
              url: "/getting-started/"
            - text: "User Guide"
              url: "/guide/"
        - title: "Resources"
          links:
            - text: "GitHub"
              url: "https://github.com/your-org/your-project"
              target: "_blank"
```

## Installation

```bash
pip install git+https://github.com/cms-cat/mkdocs-header-dropdown-plugin.git
```

## Documentation

- **[Getting Started](getting-started.md)** - Installation and basic setup
- **[Configuration Examples](examples.md)** - Real-world configuration patterns
- **[Nested Menus](nested-menus.md)** - Creating multi-level submenus
- **[GitHub Repository](https://github.com/cms-cat/mkdocs-header-dropdown-plugin)** - Source code and issues

## Use Cases

- **Organization-wide navigation**: Share common links across all documentation sites
- **Multi-project documentation**: Link between related projects
- **External resources**: Quick access to wikis, support portals, and tools
- **Contextual navigation**: Group related documentation by category
