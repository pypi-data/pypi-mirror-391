"""
Copyright (C) 2025, Jabez Winston C

Author  : Jabez Winston C <jabezwinston@gmail.com>
License : MIT
Date    : 14-Nov-2025

projdump2md - Dump Project files to Markdown file
"""

__version__ = "0.1.0"
__author__ = "Jabez Winston"
__email__ = "jabezwinston@gmail.com"

from .cli import dump_to_markdown, collect_files, generate_tree

__all__ = ["dump_to_markdown", "collect_files", "generate_tree"]
