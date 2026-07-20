"""Sphinx configuration for the pyberlab documentation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyberlab

project = "pyberlab"
author = "pyberlab contributors"
copyright = "2026, pyberlab contributors"
release = pyberlab.__version__
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

templates_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
root_doc = "index"

autodoc_default_options = {
    "member-order": "bysource",
    "show-inheritance": True,
}
autodoc_typehints = "description"
napoleon_google_docstring = False
napoleon_numpy_docstring = True

html_theme = "alabaster"
html_title = "pyberlab documentation"
