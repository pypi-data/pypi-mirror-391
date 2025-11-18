from museflow.element.style import Style


def horizontal_line_seperator(color='WhiteSmoke', thickness='1px', width: str = '100%') -> Style:
    return Style(
        background_color=color,
        height=thickness,
        width=width
    )


def row():
    return Style(
        display='flex',
        justify_content='center',
        align_items='center',
        text_align='center',
        flex_direction='row',
        width='100%'
    )

def column():
    return Style(
        display='flex',
        justify_content='center',
        align_items='center',
        text_align='center',
        flex_direction='column',
        height='100%'
    )
