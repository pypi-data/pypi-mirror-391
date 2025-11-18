"""
Represents inline styles for a Museflow element (CSS compatible)

This class provides a structured way to define and manage style properties for a Museflow element
Each attribute corresponds to a CSS property and will be rendered as part of the element's 'style' attribute

Example
-------
>>> style = Style(color="red", font_size="16px", margin="10px")
>>> str(style)
'color: red; font-size: 16px; margin: 10px'
"""


class Style:
    RAW_CSS_CONTENT = '__raw_css_content__'

    def __init__(
            self,
            # Text
            color=None,
            font=None,
            font_family=None,
            font_size=None,
            font_style=None,
            font_variant=None,
            font_weight=None,
            letter_spacing=None,
            line_height=None,
            text_align=None,
            text_decoration=None,
            text_transform=None,
            text_overflow=None,
            white_space=None,
            word_break=None,
            word_spacing=None,
            # Box model
            width=None,
            min_width=None,
            max_width=None,
            height=None,
            min_height=None,
            max_height=None,
            margin=None,
            margin_top=None,
            margin_bottom=None,
            margin_left=None,
            margin_right=None,
            padding=None,
            padding_top=None,
            padding_bottom=None,
            padding_left=None,
            padding_right=None,
            border=None,
            border_width=None,
            border_style=None,
            border_color=None,
            border_radius=None,
            outline=None,
            box_sizing=None,
            box_shadow=None,
            # Background
            background=None,
            background_color=None,
            background_image=None,
            background_repeat=None,
            background_size=None,
            background_position=None,
            background_clip=None,
            background_origin=None,
            background_attachment=None,
            # Flexbox
            display=None,
            flex=None,
            flex_direction=None,
            flex_wrap=None,
            flex_flow=None,
            justify_content=None,
            align_items=None,
            align_content=None,
            align_self=None,
            order=None,
            flex_grow=None,
            flex_shrink=None,
            flex_basis=None,
            # Grid
            grid=None,
            grid_area=None,
            grid_template=None,
            grid_template_rows=None,
            grid_template_columns=None,
            grid_template_areas=None,
            grid_row=None,
            grid_row_start=None,
            grid_row_end=None,
            grid_column=None,
            grid_column_start=None,
            grid_column_end=None,
            grid_auto_flow=None,
            grid_auto_rows=None,
            grid_auto_columns=None,
            gap=None,
            row_gap=None,
            column_gap=None,
            # Positioning
            position=None,
            top=None,
            bottom=None,
            left=None,
            right=None,
            z_index=None,
            overflow=None,
            overflow_x=None,
            overflow_y=None,
            # Effects
            opacity=None,
            visibility=None,
            cursor=None,
            pointer_events=None,
            transform=None,
            transition=None,
            transition_delay=None,
            transition_duration=None,
            transition_property=None,
            transition_timing_function=None,
            animation=None,
            animation_name=None,
            animation_duration=None,
            animation_timing_function=None,
            animation_delay=None,
            animation_iteration_count=None,
            animation_direction=None,
            # Filters
            _filter=None,
            backface_visibility=None,
            backface_filter=None,
            # Misc
            content=None,
            user_select=None,
            box_decoration_break=None,
            writing_mode=None,
            vertical_align=None,
            clip=None,
            counter_reset=None,
            counter_increment=None,
            quotes=None,
            hyphens=None,
            will_change=None,
            overscroll_behavior=None,
            # Extra
            **kwargs
    ):

        local_vars = locals()

        if _filter is not None:
            self.__dict__['filter'] = _filter

        for attr, value in local_vars.items():
            if attr not in ('self', 'kwargs', '_filter') and value is not None:
                setattr(self, attr, value)

        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def parse_inline_style(style_str: str) -> dict:
        style_kwargs = dict()
        for part in style_str.split(';'):
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip().replace('-', '_')
                value = value.strip()
                style_kwargs[key] = value
        return style_kwargs

    def render(self) -> str:
        parts = []
        if self.RAW_CSS_CONTENT in self.__dict__:
            return self.__dict__[self.RAW_CSS_CONTENT]

        for attr, value in self.__dict__.items():
            css_attr = attr.replace('_', '-')
            parts.append(f'{css_attr}: {value}')
        return '; '.join(parts)

    def update(self, other: 'Style') -> 'Style':
        combined_attrs = self.__dict__.copy()
        combined_attrs.update(other.__dict__)

        if self.RAW_CSS_CONTENT in combined_attrs:
            del combined_attrs[self.RAW_CSS_CONTENT]

        return Style(**combined_attrs)

    @staticmethod
    def raw(css_content: str) -> 'Style':
        """
        Creates a Style instance that holds raw CSS content (like @keyframes or full blocks)
        to be inserted directly into a <style> tag
        """
        raw_style = Style()
        setattr(raw_style, Style.RAW_CSS_CONTENT, css_content)
        return raw_style

    def __str__(self):
        return self.render()

    def __repr__(self):
        return self.__str__()

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return None

    def __add__(self, other: 'Style'):
        self.__dict__.update(other.__dict__)
        return self
