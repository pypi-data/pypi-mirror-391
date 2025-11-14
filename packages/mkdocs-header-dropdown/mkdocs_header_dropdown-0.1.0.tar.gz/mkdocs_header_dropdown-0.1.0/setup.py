from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mkdocs-header-dropdown",
    version="0.1.0",
    author="CMS Common Analysis Tools",
    description="A MkDocs plugin to add configurable dropdown menus to the Material theme header",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cms-cat/mkdocs-header-dropdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Documentation",
        "Topic :: Text Processing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "mkdocs>=1.4.0",
    ],
    entry_points={
        "mkdocs.plugins": [
            "header-dropdown = mkdocs_header_dropdown.plugin:HeaderDropdownPlugin",
        ]
    },
)
