# Nested Menus

Create multi-level dropdown submenus for hierarchical navigation.

## What are Nested Menus?

Nested menus (submenus) allow you to create hierarchical dropdown navigation. When a user hovers over a menu item with a submenu, an additional menu appears to the right with more options.

**Try it now**: Look at the header, hover over "Resources" → "Documentation" to see a live example!

## Basic Nested Menu

Use the `submenu` key instead of `url` to create a nested menu:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Resources"
          links:
            - text: "Documentation"  # This item has a submenu
              submenu:
                - text: "User Guide"
                  url: "/guide/"
                - text: "API Reference"
                  url: "/api/"
                - text: "Tutorials"
                  url: "/tutorials/"

            - text: "GitHub"  # Regular link
              url: "https://github.com/example"
              target: "_blank"
```

## Visual Indicators

Items with submenus automatically show:
- **Arrow indicator** (▶) to the right
- **Hover highlighting** that indicates more content
- **Submenu** that appears to the right on hover

## Multiple Nested Menus

You can have several nested items in the same dropdown:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Documentation"
          links:
            - text: "Getting Started"
              url: "/"

            - text: "Tutorials"
              submenu:
                - text: "Basic Tutorial"
                  url: "/tutorials/basic/"
                - text: "Advanced Tutorial"
                  url: "/tutorials/advanced/"

            - text: "How-To Guides"
              submenu:
                - text: "Installation"
                  url: "/howto/install/"
                - text: "Configuration"
                  url: "/howto/config/"

            - text: "Reference"
              submenu:
                - text: "API"
                  url: "/reference/api/"
                - text: "CLI"
                  url: "/reference/cli/"
```

## Multi-Level Nesting

Submenus can contain their own submenus for deeper hierarchies:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Resources"
          links:
            - text: "Documentation"
              submenu:
                - text: "Python"
                  submenu:
                    - text: "Getting Started"
                      url: "/python/start/"
                    - text: "API Reference"
                      url: "/python/api/"

                - text: "JavaScript"
                  submenu:
                    - text: "Getting Started"
                      url: "/js/start/"
                    - text: "API Reference"
                      url: "/js/api/"
```

## When to Use Nested Menus

### Good Use Cases

✅ **Categorizing documentation** by topic or type
✅ **Grouping related links** (e.g., all tutorials together)
✅ **Organizing by language** or platform
✅ **Reducing clutter** in long dropdown menus

### When to Avoid

❌ **Single item** submenus (just use a regular link)
❌ **Too many levels** (3+ levels gets confusing)
❌ **Very long** sublists (break into separate dropdowns)

## Best Practices

### Keep It Shallow

Aim for 2 levels maximum in most cases:

```yaml
✅ Good:
  - Dropdown → Item → Submenu

❌ Too deep:
  - Dropdown → Item → Submenu → Sub-submenu → Sub-sub-submenu
```

### Use Clear Labels

Make it obvious what's in the submenu:

```yaml
✅ Good:
  - text: "Tutorials"  # Clear what you'll find
    submenu: [...]

❌ Unclear:
  - text: "More"  # What kind of "more"?
    submenu: [...]
```

### Limit Submenu Length

Keep submenus to 3-7 items for scannability:

```yaml
✅ Good:
  submenu:
    - text: "Option 1"
    - text: "Option 2"
    - text: "Option 3"
    - text: "Option 4"

❌ Too long:
  submenu:
    - text: "Option 1"
    - text: "Option 2"
    ... (15 more items)
```

### Mix Regular and Nested Items

You can combine both in the same dropdown:

```yaml
# mkdocs.yml
plugins:
  - header-dropdown:
      dropdowns:
        - title: "Help"
          links:
            - text: "Quick Start"  # Regular link
              url: "/quickstart/"

            - text: "Guides"  # Nested menu
              submenu:
                - text: "Installation"
                  url: "/guides/install/"
                - text: "Configuration"
                  url: "/guides/config/"

            - text: "FAQ"  # Regular link
              url: "/faq/"
```

## Accessibility

Nested menus work with:
- **Mouse hover**: Submenu appears on hover
- **Keyboard navigation**: Use Tab and arrow keys
- **Screen readers**: Proper ARIA labels included
- **Touch devices**: Tap to open submenu

## Styling

Nested menus automatically:
- Match your Material theme colors
- Support light and dark modes
- Position correctly to avoid overflow
- Show smooth transitions
