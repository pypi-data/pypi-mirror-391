# Configuration Examples

Real-world configuration patterns and examples for the header dropdown plugin.

## Basic Single Dropdown

The simplest setup with one dropdown menu:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Docs"
          links:
            - text: "Home"
              url: "/"
            - text: "Getting Started"
              url: "/getting-started/"
            - text: "API Reference"
              url: "/api/"
```

## With Icons

Add visual branding to your dropdowns:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "My Project"
          icon: "/assets/logo.png"
          links:
            - text: "Documentation"
              url: "/docs/"
            - text: "Tutorials"
              url: "/tutorials/"
```

## Multiple Dropdowns

Organize different types of links:

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

        - title: "Community"
          links:
            - text: "Forum"
              url: "https://forum.example.com"
              target: "_blank"
            - text: "Discord"
              url: "https://discord.gg/example"
              target: "_blank"

        - title: "Project"
          links:
            - text: "GitHub"
              url: "https://github.com/org/project"
              target: "_blank"
            - text: "Changelog"
              url: "/changelog/"
            - text: "License"
              url: "/license/"
```

## Organization-Wide Shared Config

For companies or organizations with multiple documentation sites:

**Step 1: Create shared repository** (`your-org/docs-common`)

```yaml
# header-dropdown.yml
dropdowns:
  - title: "Company Resources"
    icon: "company-logo.png"
    links:
      - text: "Employee Portal"
        url: "https://portal.company.com"
        target: "_blank"
      - text: "Internal Wiki"
        url: "https://wiki.company.com"
        target: "_blank"
      - text: "Support Desk"
        url: "https://support.company.com"
        target: "_blank"
```

**Step 2: Use in each documentation site**

```bash
git submodule add https://github.com/your-org/docs-common.git
```

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      config_file: "docs-common/header-dropdown.yml"
```

## Mixed: Shared + Project-Specific

Combine organization-wide links with project-specific navigation:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      config_file: "docs-common/header-dropdown.yml"  # Shared links
      dropdowns:  # Project-specific links
        - title: "This Project"
          links:
            - text: "Overview"
              url: "/"
            - text: "Architecture"
              url: "/architecture/"
            - text: "Contributing"
              url: "/contributing/"
```

## With Nested Submenus

Create hierarchical navigation:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Documentation"
          links:
            - text: "Getting Started"
              url: "/getting-started/"

            - text: "Guides"
              submenu:
                - text: "Installation"
                  url: "/guides/installation/"
                - text: "Configuration"
                  url: "/guides/configuration/"
                - text: "Deployment"
                  url: "/guides/deployment/"

            - text: "Reference"
              submenu:
                - text: "API"
                  url: "/reference/api/"
                - text: "CLI"
                  url: "/reference/cli/"
                - text: "Config File"
                  url: "/reference/config/"

            - text: "FAQ"
              url: "/faq/"
```

## Multi-Level Nesting

Nested menus can have their own submenus:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Resources"
          links:
            - text: "Documentation"
              submenu:
                - text: "User Guides"
                  url: "/guides/"
                - text: "API Reference"
                  url: "/api/"
                - text: "Video Tutorials"
                  url: "/videos/"

            - text: "Community"
              submenu:
                - text: "Discussion Forum"
                  url: "https://forum.example.com"
                  target: "_blank"
                - text: "Chat Platforms"
                  submenu:
                    - text: "Discord"
                      url: "https://discord.gg/example"
                      target: "_blank"
                    - text: "Slack"
                      url: "https://example.slack.com"
                      target: "_blank"
```

## External Links Only

Perfect for linking to external resources:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Related Projects"
          links:
            - text: "Main Website"
              url: "https://example.com"
              target: "_blank"
            - text: "GitHub Organization"
              url: "https://github.com/example-org"
              target: "_blank"
            - text: "npm Package"
              url: "https://npmjs.com/package/example"
              target: "_blank"
```

## Tips

- Use `target: "_blank"` for external links to open in new tabs
- Keep dropdown titles short (1-2 words)
- Group related links together
- Use nested menus to avoid overwhelming long lists
- Add icons to make dropdowns more recognizable
- Share configs via git submodules for consistency across sites
