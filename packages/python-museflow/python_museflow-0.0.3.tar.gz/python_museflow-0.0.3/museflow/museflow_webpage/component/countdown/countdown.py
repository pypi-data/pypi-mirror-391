from pathlib import Path

from museflow.element.inventory import html, head, body, div, style
from museflow.element.style import Style
from museflow.museflow import Museflow
from museflow.museflow_webpage.style.palette import Palette

# --- NEW: Define the spinning ring and the animation ---

# 1. Define the CSS animation keyframes
SPIN_ANIMATION = """
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
"""

# 2. Define the style for the visual ring
ring_style = Style(
    width='75px',
    height='75px',
    border='5px solid WhiteSmoke',
    border_top=f'5px solid {Palette.Charcoal}',
    border_radius='50%',
    position='absolute',
    animation='spin 2.5s linear infinite',
)

spinning_ring = div(
    _id='spinner-ring',
    style=ring_style
)


countdown_display = div(
    _id='countdown',
    style=Style(
        font_size='32px',
        text_align='center',
        font_family='Arial, sans-serif',
        font_weight='bold',
        color=Palette.Charcoal,
        z_index='10',
        position='relative'
    )
).adopt('10')

countdown_container = div(
    _id='countdown-container',
    style=Style(
        display='flex',
        justify_content='center',
        align_items='center',
        width='100px',
        height='100px',
        position='relative'
    )
).adopt([
    spinning_ring,
    countdown_display
])

countdown_root = html().adopt([
    head().adopt(style().adopt(Style.raw(SPIN_ANIMATION))),
    body(
        _id='body',
        style=Style(
            height='100vh',
            display='flex',
            justify_content='center',
            align_items='center',
            cursor='default'
        )
    ).adopt([
        countdown_container # Use the new container here
    ])
])

countdown_script = Museflow.load_py_script(Path(__file__).parent / 'countdown_script.py')