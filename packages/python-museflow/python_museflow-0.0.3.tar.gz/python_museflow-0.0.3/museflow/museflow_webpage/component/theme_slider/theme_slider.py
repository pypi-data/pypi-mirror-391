from pathlib import Path

from museflow.element.inventory import html, head, body, div, input_
from museflow.element.style import Style
from museflow.museflow import Museflow
from museflow.museflow_webpage.style.palette import Palette


def create_slider():
    return div(
        _id='slider-container',
        style=Style(
            width='85%',
            height='100%',
            display='flex',
            justify_content='center',
            align_items='center',
        )
    ).adopt(
        input_(
            _id='theme-slider',
            type='range',
            min='0',
            max='100',
            value='50',
            style=Style(
                width='100%',
                accent_color=Palette.Charcoal,
                cursor='pointer'
            )
        )
    )


theme_slider_root = html().adopt([
    head(),
    body(
        _id='body',
        style=Style(
            height='100vh',
            transition='background-color 0.2s',
            display='flex',
            justify_content='center',
            cursor='default'
        )
    ).adopt([
        create_slider()
    ])
])

theme_slider_script = Museflow.load_py_script(Path(__file__).parent / 'theme_slider_script.py')
