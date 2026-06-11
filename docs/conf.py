# Configuration file for the Sphinx documentation builder.

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("../"))

project = "modpoll2mqtt"
copyright = "2021-2026 Ying Shaodong; 2026 yoch"
author = "yoch"

_pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
_match = re.search(
    r'^version = "([^"]+)"', _pyproject.read_text(encoding="utf-8"), re.M
)
version = release = _match.group(1) if _match else "0.0.0"

extensions = [
    "sphinx.ext.githubpages",
    "sphinxarg.ext",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["assets"]
