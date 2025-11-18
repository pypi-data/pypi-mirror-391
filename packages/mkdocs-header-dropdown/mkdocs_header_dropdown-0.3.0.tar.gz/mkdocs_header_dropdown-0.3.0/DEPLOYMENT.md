# Deployment Guide - Sharing the Plugin Across Multiple Docs Sites

This guide explains how to deploy the `mkdocs-header-dropdown` plugin so that multiple documentation sites in your organization can use it.

## Recommended Approach for CMS/CERN

### Option 1: GitLab Repository (Recommended)

This is the best approach for internal CERN projects.

#### Step 1: Create a GitLab Repository

```bash
cd mkdocs-header-dropdown-plugin
git init
git add .
git commit -m "Initial commit: MkDocs header dropdown plugin"
```

Create a new project on GitLab:
- Go to https://gitlab.cern.ch
- Create new project: `mkdocs-header-dropdown`
- Under `cms-analysis` group (or your preferred group)

Push the code:
```bash
git remote add origin https://gitlab.cern.ch/cms-analysis/mkdocs-header-dropdown.git
git push -u origin main
```

#### Step 2: Using in Documentation Sites

In each documentation project:

1. **Add to requirements.txt**:
   ```
   git+https://gitlab.cern.ch/cms-analysis/mkdocs-header-dropdown.git@main
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Copy template files** to your docs project:
   ```bash
   # Copy the header dropdown partial
   mkdir -p overrides/partials
   cp /path/to/original/overrides/partials/header-dropdown.html overrides/partials/

   # Or if you want the full header:
   cp /path/to/original/overrides/partials/header.html overrides/partials/
   ```

4. **Configure in mkdocs.yml**:
   ```yaml
   plugins:
     - header-dropdown:
         dropdowns:
           - title: "CMS POG Docs"
             icon: "/assets/logo.png"
             links:
               - text: "Link 1"
                 url: "https://example.com"
                 target: "_blank"
   ```

#### Step 3: Version Management

Create tags for releases:
```bash
git tag v0.1.0
git push origin v0.1.0
```

Use specific versions in requirements:
```
git+https://gitlab.cern.ch/cms-analysis/mkdocs-header-dropdown.git@v0.1.0
```

### Option 2: Shared Template Repository

If you want to share both the plugin AND the template files across projects:

#### Create a Template Repository

```bash
# Create a new repository with both plugin and templates
mkdir mkdocs-cms-templates
cd mkdocs-cms-templates

# Create structure
mkdir -p plugin
mkdir -p templates/partials

# Copy plugin
cp -r /path/to/mkdocs-header-dropdown-plugin/* plugin/

# Copy templates
cp /path/to/overrides/partials/header-dropdown.html templates/partials/
cp /path/to/overrides/partials/header.html templates/partials/
```

Create a `setup.sh` script:
```bash
#!/bin/bash
# setup.sh - Set up MkDocs with CMS templates

set -e

echo "Installing mkdocs-header-dropdown plugin..."
pip install -e ./plugin

echo "Copying template files..."
mkdir -p overrides/partials
cp templates/partials/header-dropdown.html overrides/partials/
cp templates/partials/header.html overrides/partials/

echo "Setup complete!"
echo "Now add the plugin configuration to your mkdocs.yml"
```

Push to GitLab:
```bash
git init
git add .
git commit -m "Initial commit: CMS MkDocs templates"
git remote add origin https://gitlab.cern.ch/cms-analysis/mkdocs-cms-templates.git
git push -u origin main
```

#### Using the Template Repository

In each docs project:

```bash
# Clone the templates
git clone https://gitlab.cern.ch/cms-analysis/mkdocs-cms-templates.git /tmp/templates

# Run setup
cd /tmp/templates
./setup.sh

# Templates are now in your project
cd -
```

### Option 3: Git Submodule

For tighter integration, use git submodules:

```bash
# In your docs repository
git submodule add https://gitlab.cern.ch/cms-analysis/mkdocs-header-dropdown.git vendor/mkdocs-header-dropdown

# Install from submodule
pip install -e vendor/mkdocs-header-dropdown

# Copy templates
cp vendor/mkdocs-header-dropdown/templates/partials/* overrides/partials/
```

Update submodules in CI/CD:
```yaml
# .gitlab-ci.yml
before_script:
  - git submodule update --init --recursive
  - pip install -e vendor/mkdocs-header-dropdown
```

## CI/CD Integration

### GitLab CI Example

Create `.gitlab-ci.yml` in your docs repository:

```yaml
image: python:3.11

stages:
  - build
  - deploy

build:
  stage: build
  before_script:
    - pip install -r requirements.txt
  script:
    - mkdocs build
  artifacts:
    paths:
      - site/
    expire_in: 1 hour

deploy:
  stage: deploy
  dependencies:
    - build
  script:
    - echo "Deploy to your hosting service"
  only:
    - main
```

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Documentation

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Build documentation
        run: mkdocs build

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```

## Centralized Configuration

For consistency across all CMS documentation sites, create a shared configuration file:

### Create `cms-common-config.yml`

```yaml
# Common configuration for all CMS docs sites
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
            - text: "JetMet TWiki"
              url: "https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetMET"
              target: "_blank"
            - text: "E/Gamma TWiki"
              url: "https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaPOG"
              target: "_blank"
            - text: "MUO Docs"
              url: "https://muon-wiki.docs.cern.ch/guidelines/"
              target: "_blank"
            - text: "TAU TWiki"
              url: "https://twiki.cern.ch/twiki/bin/view/CMS/Tau"
              target: "_blank"
```

### Using Inherited Configuration

In each project's `mkdocs.yml`:

```yaml
# Option 1: YAML merge (requires PyYAML)
INHERIT: https://raw.githubusercontent.com/cms-analysis/mkdocs-config/main/cms-common-config.yml

# Option 2: Manual merge in CI/CD
# See below

site_name: "My Project Documentation"
# ... rest of your config
```

### CI/CD Script for Config Merging

```bash
#!/bin/bash
# merge-config.sh

# Download common config
curl -o cms-common.yml https://raw.githubusercontent.com/cms-analysis/mkdocs-config/main/cms-common-config.yml

# Merge with local config (using yq or custom script)
yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' mkdocs.yml cms-common.yml > mkdocs-merged.yml

# Build with merged config
mkdocs build -f mkdocs-merged.yml
```

## Maintenance

### Updating the Plugin

When you update the plugin:

1. Make changes in the plugin repository
2. Test locally
3. Commit and tag:
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   git tag v0.2.0
   git push origin main v0.2.0
   ```

4. Update requirements in docs projects:
   ```
   # requirements.txt
   git+https://gitlab.cern.ch/cms-analysis/mkdocs-header-dropdown.git@v0.2.0
   ```

### Communication

When making changes:
1. Document in CHANGELOG.md
2. Update version in pyproject.toml
3. Notify teams via mailing list or Mattermost
4. Update example configurations

## Monitoring

Track which projects are using the plugin:

```bash
# Search across GitLab projects
# Use GitLab API or web interface to find projects with the plugin in requirements.txt
```

## Troubleshooting

### Plugin Version Conflicts

If different docs sites need different plugin versions:

1. Use version tags in requirements:
   ```
   git+https://gitlab.cern.ch/cms-analysis/mkdocs-header-dropdown.git@v0.1.0
   ```

2. Maintain backward compatibility
3. Document breaking changes in CHANGELOG

### Template Drift

To prevent template files from diverging:

1. Include templates in the plugin package
2. Or use a version check in CI:
   ```bash
   # Check template version
   grep "version:" overrides/partials/header-dropdown.html
   ```

## Best Practices

1. **Semantic Versioning**: Use semver for plugin versions
2. **Testing**: Test plugin with multiple docs projects before releasing
3. **Documentation**: Keep README and USAGE.md up to date
4. **Changelog**: Maintain a detailed CHANGELOG.md
5. **Examples**: Provide example configurations
6. **Communication**: Announce updates to all teams

## Support

For issues or questions:
- GitLab Issues: https://gitlab.cern.ch/cms-analysis/mkdocs-header-dropdown/issues
- Mattermost: #cms-cat channel
- Email: cms-phys-conveners-CAT@cern.ch
