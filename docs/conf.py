# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath("../"))

project = "modpoll2mqtt"
copyright = "2021-2026 Ying Shaodong; 2026 yoch"
author = "yoch"

extensions = [
    "sphinxarg.ext",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["assets"]
