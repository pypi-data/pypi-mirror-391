# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
# import recommonmark
# from recommonmark.transform import AutoStructify
from molecularprofiles.version import __version__

version = __version__
release = __version__

# -- Project information -----------------------------------------------------

project = "molecularprofiles"
copyright = "2020, Molecularprofiles Project"
author = "Molecularprofiles Project"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx_paramlinks",
    "myst_parser",
    "sphinxarg.ext",
    "nbsphinx",
    "numpydoc",
    "sphinx_design",
]

myst_enable_extensions = [
    "linkify",
]

myst_heading_anchors = 3

# Default options for autodoc directives
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# autosectionlabel_prefix_document = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document.
master_doc = "index"

# Ignore example notebook errors
nbsphinx_allow_errors = True
nbsphinx__timeout = 200  # allow max 2 minutes to build each notebook

numpydoc_show_class_members = False

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_theme_options = dict(
    navigation_with_keys=False,
    show_nav_level=0,
    logo=dict(
        image_light="_static/cta.png",
        image_dark="_static/cta_dark.png",
        alt_text="ctao-logo",
    ),
)
html_sidebars = {"**": []}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
