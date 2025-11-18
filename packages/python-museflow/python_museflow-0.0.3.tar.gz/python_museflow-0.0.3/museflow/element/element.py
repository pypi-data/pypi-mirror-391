from typing import Any

from museflow.element.style import Style


class Element:
    def __init__(
            self,
            tag: str,
            _class: str = None,
            _id: str = None,
            name: str = None,
            style: Style = None,
            content: 'Element' or list or Any = None,
            href: str = None,
            attrs: dict = None,  # Arbitrary HTML attributes (E.G. alt, src, title, etc.)
            is_void_element: bool = False
    ):
        self.tag = tag
        self._class = _class
        self._id = _id
        self.name = name
        self.style = style
        self.content = content
        self.href = href
        self.attrs = attrs or dict()
        self.is_void_element = is_void_element

    def serialize_attributes(self) -> str:
        """ Serialize the element's attributes into an HTML-compatible string """
        attrs = []
        if self._class: attrs.append(f'class="{self._class}"')
        if self._id: attrs.append(f'id="{self._id}"')
        if self.name: attrs.append(f'name="{self.name}"')
        if self.style: attrs.append(f'style="{str(self.style)}"')

        # Special case: iframe with content -> render as srcdoc
        if self.tag == 'iframe':
            self.content = '<!-- IFrame -->'
            srcdoc = self.attrs.get('srcdoc', None)
            if srcdoc:
                normalize_srcdoc = str(srcdoc).replace("'", '"')
                flat_js = ' '.join(line.strip() for line in normalize_srcdoc.splitlines())
                attrs.append(f"srcdoc='{flat_js}'")
                self.attrs.pop('srcdoc')

        # Add all other arbitrary attributes
        for k, v in self.attrs.items():
            attrs.append(f'{k}="{v}"')

        return ' ' + ' '.join(attrs) if attrs else ''

    def render_content(self, indent: int = 2, level: int = 0) -> str:
        """ Recursively render the content of this element """
        if self.content is None:
            return ''

        if isinstance(self.content, list):
            lines = []
            for item in self.content:
                if isinstance(item, Element):
                    lines.append(item.render(indent=indent, level=level + 1))
                elif isinstance(self.content, str):
                    for line in item.split('\n'):
                        line_strip = line.strip()
                        if line_strip != '':
                            lines.append(f'{" " * (indent * (level + 1))}{line_strip}')

            return '\n'.join(lines)

        elif isinstance(self.content, Element):
            return self.content.render(indent=indent, level=level + 1)

        elif isinstance(self.content, str):
            lines = []
            for line in self.content.split('\n'):
                line_strip = line.strip()
                if line_strip != '':
                    lines.append(f'{" " * (indent * (level + 1))}{line_strip}')

            return '\n'.join(lines)

        return ' ' * (indent * (level + 1)) + str(self.content)

    def render(self, indent: int = 2, level: int = 0) -> str:
        """Render element with proper indentation, handling void and non-void elements."""

        if indent < 0:
            raise ValueError(f'Indent must be greater than or equal to 0, got: {indent}')

        if level < 0:
            raise ValueError(f'Level must be greater than or equal to 0, got: {level}')

        attrs = self.serialize_attributes()
        content = self.render_content(indent=indent, level=level)

        indent_space = ' ' * (indent * level)

        if self.is_void_element:
            # Void elements should never have content or a closing tag
            return f'{indent_space}<{self.tag}{attrs}>'

        # Non-void elements
        if content:
            return f'{indent_space}<{self.tag}{attrs}>\n{content}\n{indent_space}</{self.tag}>'
        else:
            return f'{indent_space}<{self.tag}{attrs}></{self.tag}>'

    def inject(self, item: Any):
        """
        Inserts an item at the top of the element's content
        If the element has no content, the item becomes the content
        If the content is a list, the item is inserted at index 0 (top)
        If the content is a single item, it is converted into a list with
        the new item placed first

        Raises:
            RuntimeError: If the element is a void element (cannot have children)

        Args:
            item (Any): The item to insert into the element's content

        Returns:
            self: Allows method chaining.

        Example:
            el = Element('first')
            el.inject('second')
            el.inject('third')
            # el.content => ['third', 'second', 'first']
        """
        if self.is_void_element:
            raise RuntimeError('Void elements cannot adopt children')

        if self.content is None:
            self.content = item
        elif isinstance(self.content, list):
            self.content.insert(0, item)
        else:
            self.content = [item, self.content]

        return self

    def adopt(self, item: Any):
        """
        Adopt another element or content as a child of this element

        This method allows dynamic composition of elements, supporting:
        - Single Element instances
        - Primitives (str, int, float, etc.)
        - Lists of Elements or primitives

        If the element already has content, the new item is appended, preserving
        existing content. This method returns self to allow method chaining.

        Parameters
        ----------
        item : Any
        The element or content to adopt. Can be a single Element, a primitive, or a list of Elements/primitives
        """
        if self.is_void_element:
            raise RuntimeError('Void elements cannot adopt children')

        if self.content is None:
            self.content = item
        elif isinstance(self.content, list):
            self.content.append(item)
        else:
            self.content = [self.content, item]
        return self

    def find_child_element(self, tag: str = None, _id: str = None, _class: str = None) -> 'Element' or None:
        """
        Recursively search for the first child element that matches the given criteria

        Args:
            tag (str, optional): Tag name to match
            _id (str, optional): Element ID to match
            _class (str, optional): Class name to match

        Returns:
            Element or None: The first matching element, or None if not found
        """
        if (
                (tag is None or self.tag == tag) and
                (_id is None or self._id == _id) and
                (_class is None or self._class == _class)
        ):
            return self

        if isinstance(self.content, Element):
            result = self.content.find_child_element(tag, _id, _class)
            if result:
                return result
        elif isinstance(self.content, list):
            for child in self.content:
                if isinstance(child, Element):
                    result = child.find_child_element(tag, _id, _class)
                    if result:
                        return result
        return None
