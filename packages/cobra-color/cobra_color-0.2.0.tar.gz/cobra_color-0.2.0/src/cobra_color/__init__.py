# src/cobra_color/__init__.py
"""
cobra-color
----

A lightweight Python package for terminal display enhancements.

_Example:_
>>> from cobra_color import ctext
"""
from . import draw

from .color import (ctext, compile_template)
from .output import (smart_print, set_console_func, ConsoleFunc)

from .format import fmt_dict, fmt_list


__author__ = "Zhen Tian"
__version__ = "0.1.0"

__all__ = [
    "draw",  # module
    "ctext",
    "compile_template",
    "smart_print",
    "set_console_func",
    "ConsoleFunc",
    "fmt_dict",
    "fmt_list"
]
