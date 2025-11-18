from pathlib import Path

from museflow.element.inventory import div, input_, html, body
from museflow.element.style import Style
from museflow.museflow import Museflow
from museflow.museflow_webpage.style.palette import Palette

dial_display = input_(
    _id='dial-display',
    value='',
    readonly=True,
    style=Style(
        width='192px',
        font_size='24px',
        text_align='center',
        margin_bottom='24px',
        border='2px solid Gainsboro',
        border_radius='5px',
        font_family='Arial, sans-serif',
        color=Palette.Charcoal,
        cursor='pointer'
    )
)

keys = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
]

keypad_rows = []
for row in keys:
    row_div = div(style=Style(display='flex', justify_content='center'))
    for key in row:
        btn = div(
            _id=f'key-{key}',
            content=key,
            style=Style(
                width='50px',
                height='50px',
                background='Gainsboro',
                display='flex',
                justify_content='center',
                align_items='center',
                font_size='20px',
                cursor='pointer',
                border_radius='10px',
                user_select='none',
                font_family='Arial, sans-serif',
                margin='5px'
            )
        )
        row_div.adopt(btn)
    keypad_rows.append(row_div)

dialer_root = html().adopt(
    body(
        _id='body',
        style=Style(
            display='flex',
            justify_content='center',
            align_items='center',
            height='100vh'
        )
    ).adopt(div(
        _id='dialer-root',
        style=Style(
            display='flex',
            flex_direction='column',
            align_items='center',
            height='100%'
        )
    ).adopt([dial_display] + keypad_rows))
)

dialer_script = Museflow.load_py_script(Path(__file__).parent / 'dialer_script.py')
