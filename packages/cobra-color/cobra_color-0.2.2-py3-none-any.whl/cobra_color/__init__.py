# src/cobra_color/__init__.py
"""
cobra-color
----

A lightweight Python package for terminal display enhancements.

_Example:_
- Render a text in the terminal:

```python
from cobra_color import ctext

print(ctext("Hello World!", fg="r", styles=["bold"]))
```

- Render an image in the terminal:

```python
from cobra_color.draw import fmt_image

# ASCII art
print(fmt_image("example.jpg", width=80, mode="ascii"))

# Half-block color (recommended for truecolor terminals)
print(fmt_image("example.jpg", width=80, mode="half-color"))
```

- Render some text with fonts in the terminal:

```python
from cobra_color.draw import fmt_font, FontName

# Borderless grayscale font
print(fmt_font("Hello World!", font=FontName.LLDISCO,, mode="half-gray", trim_border=True))
```
"""
from . import draw

from .color import (ctext, compile_template)
from .output import (smart_print, set_console_func, ConsoleFunc)

from .format import fmt_dict, fmt_list


__author__ = "Zhen Tian"
__version__ = "0.2.2"

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
