from typing import Any

from museflow.element.element import Element
from museflow.element.style import Style


class ElementFactory:
    """ Factory for producing generic Museflow elements dynamically """

    def __init__(self, tag: str, is_void_element: bool = False):
        self.tag = tag
        self.is_void_element = is_void_element

    def produce(
            self,
            _class: str = None,
            _id: str = None,
            name: str = None,
            style: Style = None,
            content: Any = None,
            **attrs
    ) -> Element:
        return Element(
            tag=self.tag,
            _class=_class,
            _id=_id,
            name=name,
            style=style,
            content=content,
            attrs=attrs,
            is_void_element=self.is_void_element
        )
