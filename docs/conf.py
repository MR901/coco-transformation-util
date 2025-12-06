# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'CTU - COCO Transformation Util'
copyright = '2025, CTU Maintainers'
author = 'CTU Maintainers'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys

# Ensure project root is on sys.path so autodoc can import `ctu`
sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'myst_parser',
]

# Autodoc / Autosummary configuration
autosummary_generate = True
autodoc_member_order = 'bysource'
autodoc_mock_imports = [
    'cv2',
    'numpy',
    'matplotlib',
    'matplotlib.pyplot',
]

# Recognize both .rst and .md sources
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Napoleon (NumPy/Google style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_attr_annotations = False

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

try:
    import sphinx_rtd_theme  # type: ignore
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
except Exception:
    html_theme = 'alabaster'
html_static_path = ['_static']

# MyST configuration
myst_enable_extensions = [
    'colon_fence',
    'linkify',
]

# Intersphinx mapping for cross-references
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', {}),
    'numpy': ('https://numpy.org/doc/stable/', {}),
    'matplotlib': ('https://matplotlib.org/stable/', {}),
}

# Reduce sidebar depth/clutter
html_theme_options = {
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 2,
    'titles_only': True,
}
