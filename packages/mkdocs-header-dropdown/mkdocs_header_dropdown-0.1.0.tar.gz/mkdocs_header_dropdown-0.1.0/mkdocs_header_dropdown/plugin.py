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
