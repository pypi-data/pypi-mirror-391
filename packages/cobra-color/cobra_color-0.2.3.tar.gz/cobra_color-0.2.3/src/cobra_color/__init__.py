# src/cobra_color/__init__.py
"""
cobra-color
----

A lightweight Python package for terminal display enhancements.

_Example:_


- Render a text in the terminal:

```python
from cobra_color import ctext, smart_print

# Print directly from the terminal
print(ctext("Hello World!", fg="r", styles=["bold"]))

# Alternatively, you can use smart_print() to automatically support progress bar modes like tqdm and rich.
smart_print(ctext("Hello World!", fg="r", styles=["bold"]))
```

- Render an image in the terminal:

```python
from cobra_color.draw import fmt_image, smart_print

# ASCII art
smart_print(fmt_image("example.jpg", width=80, mode="ascii"))

# Half-block color (recommended for truecolor terminals)
smart_print(fmt_image("example.jpg", width=80, mode="half-color"))
```

- Render some text with fonts in the terminal:

```python
from cobra_color.draw import fmt_font, FontName, smart_print

# Borderless grayscale font
smart_print(fmt_font("Hello World!", font=FontName.LLDISCO,, mode="half-gray", trim_border=True))
```
"""

from . import draw

from .color import (ctext, compile_template)
from .output import (smart_print, set_console_func, ConsoleFunc)
from .format import (fmt_dict, fmt_list)


__author__ = "Zhen Tian"
__version__ = "0.2.3"

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
