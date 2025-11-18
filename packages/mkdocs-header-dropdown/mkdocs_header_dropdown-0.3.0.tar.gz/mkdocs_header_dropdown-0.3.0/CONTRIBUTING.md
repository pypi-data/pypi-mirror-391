# Contributing to MkDocs Header Dropdown Plugin

Thank you for your interest in contributing to the MkDocs Header Dropdown Plugin!

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if the issue already exists in [GitHub Issues](https://github.com/cms-cat/mkdocs-header-dropdown/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - MkDocs and plugin versions
   - Sample configuration (if applicable)

### Submitting Changes

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/mkdocs-header-dropdown.git
   cd mkdocs-header-dropdown
   ```

3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

4. **Make your changes**:
   - Follow the existing code style
   - Add tests if applicable
   - Update documentation if needed

5. **Test your changes**:
   ```bash
   # Install in development mode
   pip install -e .

   # Test with a sample MkDocs site
   cd /path/to/test/site
   mkdocs build
   mkdocs serve
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

   Use commit message prefixes:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for improvements to existing features
   - `Docs:` for documentation changes
   - `Refactor:` for code refactoring

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**:
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Describe your changes

## Development Setup

### Prerequisites

- Python 3.7 or higher
- MkDocs >= 1.4.0
- Material for MkDocs theme

### Installation

```bash
# Clone the repository
git clone https://github.com/cms-cat/mkdocs-header-dropdown.git
cd mkdocs-header-dropdown

# Install in development mode
pip install -e .

# Or with development dependencies (if we add them later)
pip install -e ".[dev]"
```

### Testing

To test your changes:

1. Create a test MkDocs site or use an existing one
2. Install the plugin in development mode
3. Configure the plugin in `mkdocs.yml`
4. Run `mkdocs serve` and verify functionality
5. Test with different configurations
6. Test with light and dark themes

## Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to classes and functions
- Keep functions focused and small
- Comment complex logic

## Documentation

When adding new features:

- Update README.md with basic usage
- Update USAGE.md with detailed examples
- Add examples to QUICKSTART.md if applicable
- Update CHANGELOG.md with your changes

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- MAJOR version for incompatible API changes
- MINOR version for new functionality (backwards compatible)
- PATCH version for bug fixes (backwards compatible)

## Release Process

Maintainers will handle releases:

1. Update version in `pyproject.toml` and `setup.py`
2. Update CHANGELOG.md
3. Create a git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. Push tag: `git push origin vX.Y.Z`
5. Create GitHub release from tag

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion on GitHub Discussions (if enabled)
- Contact the maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
