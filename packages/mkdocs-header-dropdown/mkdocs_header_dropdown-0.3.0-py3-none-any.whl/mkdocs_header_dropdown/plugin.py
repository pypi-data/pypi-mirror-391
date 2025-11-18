"""
MkDocs Header Dropdown Plugin

A plugin to add configurable dropdown menus to the MkDocs Material theme header.
"""
import os
import yaml
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.config.defaults import MkDocsConfig


class HeaderDropdownPlugin(BasePlugin):
    """
    Plugin that adds configurable dropdown menus to the header.

    Configuration in mkdocs.yml:

    plugins:
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
    """

    config_scheme = (
        ('config_file', config_options.Type(str, default=None)),
        ('dropdowns', config_options.Type(list, default=[])),
    )

    def _generate_links_from_yaml(self, data, parent_key=None):
        """
        Recursively generate dropdown links from YAML structure.

        Special keys:
        - 'fallback' or 'url': Used as the top-level URL (clickable parent)
        - Other string values: Create submenu items
        - Nested dicts: Flatten into parent's submenu (no intermediate level)

        Args:
            data: Dict or string from YAML
            parent_key: Name of the parent key (used for display text)

        Returns:
            List of link configurations or single link dict
        """
        links = []

        if isinstance(data, dict):
            # Check for URL at this level
            parent_url = data.get('fallback') or data.get('url')

            # Collect submenu items from other keys
            submenu = []
            for key, value in data.items():
                if key in ('fallback', 'url'):
                    continue  # Skip these, used for parent URL

                if isinstance(value, str):
                    # Direct URL value - format the display name
                    display_name = key.replace('_', ' ')  # Convert Run2 -> Run 2
                    submenu.append({
                        'text': display_name,
                        'url': value,
                        'target': '_blank'
                    })
                elif isinstance(value, dict):
                    # Nested dict - flatten it one level up
                    # Don't create an intermediate item, just add its children directly
                    for nested_key, nested_value in value.items():
                        if nested_key in ('fallback', 'url'):
                            continue
                        if isinstance(nested_value, str):
                            # Format display name for era-specific docs
                            display_name = nested_key.replace('-NanoAODv', ' (v').replace('NanoAODv', 'v')
                            if not display_name.endswith(')') and 'v' in display_name:
                                display_name += ')'
                            submenu.append({
                                'text': display_name,
                                'url': nested_value,
                                'target': '_blank'
                            })

            # Return parent link with submenu
            if parent_key:
                link = {
                    'text': f"{parent_key}",
                    'target': '_blank'
                }
                if parent_url:
                    link['url'] = parent_url
                if submenu:
                    link['submenu'] = submenu
                return link

            # Top level - return all items as list
            return submenu

        return links

    def on_config(self, config: MkDocsConfig, **kwargs) -> MkDocsConfig:
        """
        Add dropdown configuration to the MkDocs config's extra section.
        This makes it available in templates via config.extra.header_dropdowns
        """
        if not config.extra:
            config.extra = {}

        # Collect dropdowns from various sources
        dropdowns = []

        # 1. Load from config file if specified
        config_file = self.config.get('config_file')
        if config_file:
            config_file_path = os.path.join(config.docs_dir, '..', config_file)
            if os.path.exists(config_file_path):
                with open(config_file_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if 'dropdowns' in file_config:
                        # Check if any dropdown wants auto-generated links
                        for dropdown in file_config['dropdowns']:
                            # If a dropdown has auto_generate_from, load and generate links
                            if 'auto_generate_from' in dropdown:
                                auto_config = dropdown['auto_generate_from']
                                yaml_file = auto_config.get('file')
                                yaml_key = auto_config.get('key', None)

                                if yaml_file:
                                    yaml_file_path = os.path.join(config.docs_dir, '..', yaml_file)
                                    if os.path.exists(yaml_file_path):
                                        with open(yaml_file_path, 'r') as yf:
                                            yaml_data = yaml.safe_load(yf)

                                            # Navigate to specified key if provided
                                            if yaml_key:
                                                for key_part in yaml_key.split('.'):
                                                    yaml_data = yaml_data.get(key_part, {})

                                            # Generate links from YAML structure
                                            if isinstance(yaml_data, dict):
                                                generated_links = []
                                                for top_key, top_value in yaml_data.items():
                                                    link = self._generate_links_from_yaml(top_value, top_key)
                                                    if link:
                                                        generated_links.append(link)

                                                # Merge with existing links
                                                dropdown['links'] = dropdown.get('links', []) + generated_links

                                del dropdown['auto_generate_from']  # Remove the marker
                        dropdowns.extend(file_config['dropdowns'])
            else:
                raise FileNotFoundError(f"Config file not found: {config_file_path}")

        # 2. Add dropdowns from mkdocs.yml
        dropdowns.extend(self.config.get('dropdowns', []))

        # Add the dropdowns to extra so templates can access them
        config.extra['header_dropdowns'] = dropdowns

        return config

    def on_env(self, env, config, files):
        """
        Add plugin's template directory to the Jinja2 environment's search path.
        This runs after the theme environment is set up.
        """
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(plugin_dir, 'templates')

        if os.path.exists(templates_dir):
            # Add to the beginning of the loader search path
            env.loader.searchpath.insert(0, templates_dir)

        return env

    def on_page_context(self, context, page, config, nav):
        """
        Add dropdown data to the page context for template rendering.
        """
        context['header_dropdowns'] = config.extra.get('header_dropdowns', [])
        return context
