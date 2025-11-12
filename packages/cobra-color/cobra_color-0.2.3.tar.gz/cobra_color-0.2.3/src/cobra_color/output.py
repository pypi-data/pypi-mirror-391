# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
import sys
import builtins
from typing import (Any, Optional, Callable, Union)

# import
try:
    from tqdm import tqdm  # type: ignore
except ImportError:
    tqdm = None

try:
    from rich.console import Console  # type: ignore
except ImportError:
    Console = None


_GLOBAL_CONSOLE_FUNC: Optional[ConsoleFunc] = None  # output function


def set_console_func(func: Callable[..., Any], **kwargs: Any):
    r"""
    Set a global console for smart_print function.

    Parameters
    ----------
        func : Callable[..., Any]
            A console output function or method, which should accept string input as the first argument.

        **kwargs : Any
            Additional keyword arguments to be passed to the console function during each call.
    """
    global _GLOBAL_CONSOLE_FUNC
    _GLOBAL_CONSOLE_FUNC = ConsoleFunc(func, **kwargs)


def _get_global_console():
    r"""
    Get the global console function.
    """
    # set default console
    if _GLOBAL_CONSOLE_FUNC is None and Console is not None:
        set_console_func(Console().print, end="", markup=False, highlight=False)

    return _GLOBAL_CONSOLE_FUNC


class ConsoleFunc():
    r"""
    A wrapper for console output functions with preset keyword arguments.
    """
    def __init__(self, func: Callable[..., Any], **kwargs: Any):
        self.__func = func
        self.__kwargs = kwargs

    def __call__(self, *args, **kwargs) -> Any:
        all_kwargs = self.__kwargs.copy()
        all_kwargs.update(kwargs)
        return self.__func(*args, **all_kwargs)


def smart_print(
    *values: object,
    sep: str = " ",
    end: str = "\n",
    file: Optional[Any] = None,
    flush: bool = False,
    console_func: Optional[Union[Callable[..., Any], ConsoleFunc]] = None
):
    r"""
    A smart print function that works well with progress bars from `tqdm` and `rich` consoles.

    Parameters
    ----------
        *values : object
            Values to be printed.

        sep : str, default to `" "`
            Separator between values.

        end : str, default to `"\n"`
            End character after printing.

        file : Optional[Any], default to `None`
            The file-like object to write to. If `None`, defaults to `sys.stdout`.

        flush : bool, default to `False`
            Whether to forcibly flush the stream.

        console_func : Optional[Union[Callable[..., Any], ConsoleFunc]], default to `None`
            A console output function or method to use for printing.
            - `None`: Use the global console if set;
            - `Callable[..., Any]` or `ConsoleFunc`: Use the provided function.
    """
    # format string
    formatted_str = sep.join(map(str, values)) + end
    # determine output function and kwargs
    if console_func is not None:
        # Use provided console
        if not isinstance(console_func, ConsoleFunc):
            console_func = ConsoleFunc(console_func, end="")
        used_func = console_func
    else:
        if tqdm is not None and getattr(tqdm, "_instances", None):
            # Use tqdm write
            used_func = ConsoleFunc(tqdm.write, end="")
        else:
            # Use global console
            used_func = _get_global_console()

    def _default_print():
        builtins.print(formatted_str, file=file or sys.stdout, flush=flush)

    # output
    if used_func is None:
        _default_print()
    else:
        try:
            used_func(formatted_str)
        except Exception:
            _default_print()
