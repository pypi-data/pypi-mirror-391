"""
Museflow PYJS Fake Browser Stubs

This module provides a lightweight, Python-only simulation of the browser DOM
to support Museflow development and testing. It defines:
- Element: a fake DOM element with `id`, `tag`, `children`, `value`, and event bindings
- Document: a fake global document object with methods like `getElementById`, `createElement`, and `querySelector`
- document: a pre-instantiated global Document instance

These stubs are intended for:
- Offline testing of Python scripts
- Autocomplete and static type checking in IDEs (PyCharm, VSCode)
- Avoiding the need for a real browser environment during development
"""

from typing import Any, Callable, List, Optional


class Element:
    # noinspection PyShadowingBuiltins, PyUnusedLocal
    def __init__(self, id: str = '', tag: str = '', value: Any = None):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def appendChild(self, child: 'Element'):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def removeChild(self, child: 'Element'):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def addEventListener(self, event: str, handler: Callable):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def bind(self, event: str, handler: Callable):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def setAttribute(self, attr: str, value: Any):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def getAttribute(self, attr: str) -> Optional[Any]:
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def removeAttribute(self, attr: str):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def click(self):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def focus(self):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def blur(self):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def remove(self):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def cloneNode(self, deep: bool = True):
        pass


class Document:
    # noinspection PyMethodMayBeStatic, PyPep8Naming, PyShadowingBuiltins
    def getElementById(self, id: str) -> Element:
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming, PyUnusedLocal
    def getElementsByClassName(self, className: str) -> List[Element]:
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming, PyUnusedLocal
    def getElementsByTagName(self, tag: str) -> List[Element]:
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def querySelector(self, selector: str) -> Element:
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming, PyUnusedLocal
    def querySelectorAll(self, selector: str) -> List[Element]:
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def createElement(self, tag: str) -> Element:
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def createTextNode(self, text: str) -> Element:
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def write(self, html: str):
        pass


# Pre-Instantiated Global Document
document = Document()


class Console:
    @staticmethod
    def log(*args):
        pass

    @staticmethod
    def warn(*args):
        pass

    @staticmethod
    def error(*args):
        pass

    @staticmethod
    def info(*args):
        pass


console = Console()


# noinspection PyShadowingBuiltins, PyUnusedLocal
def alert(message):
    pass


# noinspection PyMethodMayBeStatic, PyPep8Naming, PyUnusedLocal
def setTimeout(callback: Callable, delay: int, *args) -> int:
    pass


# noinspection PyMethodMayBeStatic, PyPep8Naming, PyUnusedLocal
def setInterval(callback: Callable, interval: int, *args) -> int:
    pass


# noinspection PyMethodMayBeStatic, PyPep8Naming, PyUnusedLocal
def clearTimeout(timer_id: int):
    pass


# noinspection PyMethodMayBeStatic, PyPep8Naming, PyUnusedLocal
def clearInterval(timer_id: int):
    pass


# Window / globals
window = None
navigator = None
location = None

parentNode = None
children = []


# Event
# noinspection PyPep8Naming, PyUnusedLocal
def dispatchEvent(event):
    pass


# noinspection PyPep8Naming, PyUnusedLocal
def stopPropagation():
    pass


# noinspection PyPep8Naming, PyUnusedLocal
def preventDefault():
    pass


class Event:
    # noinspection PyMethodMayBeStatic, PyPep8Naming, PyUnusedLocal
    def __init__(self, type: str):
        pass


class CustomEvent(Event):
    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def __init__(self, type: str, detail: Any = None):  # noqa
        pass


# Timing / animation
def requestAnimationFrame(callback: Callable):
    pass


# Storage
class Storage:
    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def getItem(self, key: str) -> Any:
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def setItem(self, key: str, value: Any):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def removeItem(self, key: str):
        pass

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def clear(self):
        pass


localStorage = Storage()
sessionStorage = Storage()


# noinspection PyPep8Naming, PyUnusedLocal
def JSON_stringify(obj: Any) -> str:
    pass


# noinspection PyPep8Naming, PyUnusedLocal
def JSON_parse(s: str) -> Any:
    pass


# noinspection PyPep8Naming, PyUnusedLocal
def console_debug(*args):
    pass


# noinspection PyPep8Naming, PyUnusedLocal
def console_table(*args):
    pass


def encodeURIComponent(s: str) -> str:
    pass


def decodeURIComponent(s: str) -> str:
    pass
