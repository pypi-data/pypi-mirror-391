# Getting Started

This page demonstrates additional content in the example site.

## Installation

Install the plugin from GitHub:

```bash
pip install git+https://github.com/cms-cat/mkdocs-header-dropdown-plugin.git
```

## Basic Configuration

The minimal configuration requires just the plugin and at least one dropdown:

```yaml
# mkdocs.yml
plugins:
  - search
  - header-dropdown:
      dropdowns:
        - title: "Documentation"
          links:
            - text: "Home"
              url: "/"
            - text: "Getting Started"
              url: "/getting-started/"
```

## Adding Icons

You can add icons to your dropdowns. The icon path should be relative to your docs directory:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "My Project"
          icon: "/assets/logo.png"  # Located at docs/assets/logo.png
          links:
            - text: "Home"
              url: "/"
            - text: "Documentation"
              url: "/docs/"
```

## Multiple Dropdowns

Add as many dropdowns as you need:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Documentation"
          links:
            - text: "User Guide"
              url: "/guide/"
            - text: "API Reference"
              url: "/api/"
            - text: "Examples"
              url: "/examples/"
        - title: "Resources"
          links:
            - text: "GitHub Repository"
              url: "https://github.com/your-org/your-project"
              target: "_blank"
            - text: "Issue Tracker"
              url: "https://github.com/your-org/your-project/issues"
              target: "_blank"
```

## Using Shared Configuration

For multiple documentation sites sharing the same navigation:

**Step 1:** Create a shared config repository (`your-org/docs-common`):

```yaml
# header-dropdown.yml
dropdowns:
  - title: "Company Resources"
    icon: "company-logo.png"
    links:
      - text: "Internal Wiki"
        url: "https://wiki.company.com"
        target: "_blank"
      - text: "Support Portal"
        url: "https://support.company.com"
        target: "_blank"
```

**Step 2:** Add as git submodule to your documentation repo:

```bash
git submodule add https://github.com/your-org/docs-common.git
```

**Step 3:** Reference in `mkdocs.yml`:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      config_file: "docs-common/header-dropdown.yml"
```

**Live Example**: The "CMS POG Docs" dropdown in this site's header is loaded from the [cms-docs-common](https://github.com/cms-cat/cms-docs-common) repository via git submodule!

## Mixing Configuration Sources

You can combine shared config with site-specific dropdowns:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      config_file: "docs-common/header-dropdown.yml"  # Shared organization links
      dropdowns:  # Project-specific additions
        - title: "This Project"
          links:
            - text: "About"
              url: "/about/"
            - text: "Changelog"
              url: "/changelog/"
            - text: "Contributing"
              url: "/contributing/"
```

Both shared and project-specific dropdowns will appear in the header - check this example site to see it in action!

## Nested Dropdowns

You can create nested dropdowns (submenus) by using the `submenu` key instead of `url`:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Resources"
          links:
            - text: "GitHub Repository"
              url: "https://github.com/your-org/your-project"
              target: "_blank"
            - text: "Documentation"  # This will have an arrow →
              submenu:
                - text: "User Guide"
                  url: "/guide/"
                - text: "API Reference"
                  url: "/api/"
                - text: "Tutorials"
                  url: "/tutorials/"
            - text: "Community"  # Another nested menu
              submenu:
                - text: "Forum"
                  url: "https://forum.example.com"
                  target: "_blank"
                - text: "Chat"
                  url: "https://chat.example.com"
                  target: "_blank"
```

**Live Example**: Hover over the "Resources" dropdown in this site's header, then hover over "Documentation" to see a nested submenu appear to the right!

Features:
- **Arrow indicator** (▶) shows which items have submenus
- **Submenus appear on hover** to the right
- Works with both mouse and keyboard navigation
- Multiple levels of nesting supported
