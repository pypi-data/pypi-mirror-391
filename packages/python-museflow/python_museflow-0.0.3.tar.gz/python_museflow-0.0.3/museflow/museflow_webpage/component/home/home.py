from pathlib import Path

from museflow.element.inventory import html, head, body, div, h1, p, iframe, img
from museflow.element.style import Style
from museflow.museflow import Museflow
from museflow.museflow_webpage.component.countdown.countdown import countdown_root, countdown_script
from museflow.museflow_webpage.component.dialer.dialer import dialer_root, dialer_script
from museflow.museflow_webpage.component.home.image_to_base64 import image_to_base64
from museflow.museflow_webpage.component.theme_slider.theme_slider import theme_slider_root, theme_slider_script
from museflow.museflow_webpage.style.palette import Palette
from museflow.museflow_webpage.style.style import row, column


def create_logo():
    return div(
        _id='logo',
        style=Style(
            font_size='28px',
            font_weight='bold',
            color='white',
            font_family='Arial, sans-serif',
        )
    ).adopt(
        h1(content='Museflow')
    )


def create_header():
    return div(
        _id='header',
        style=Style(
            width='100%',
            display='flex',
            justify_content='center',
            background_color=Palette.GunmetalBlue,
            box_shadow='0 2px 4px rgba(0,0,0,0.1)'
        )
    ).adopt(
        create_logo()
    )


def create_introduction_section():
    return div(
        _id='main',
        style=column() + Style(height='176px', width='100%', margin='24px 0')
    ).adopt([
        h1(
            content='Welcome to Museflow',
            style=Style(
                text_align='center',
                font_size='24px',
                color=Palette.Charcoal,
                margin_bottom='24px'
            )
        ),
        p(
            content='Build full-stack web applications entirely in Python, without HTML, CSS, or JavaScript',
            style=Style(
                font_size='16px',
                color=Palette.Charcoal
            )
        )
    ])


def create_component_card(title, root_element, script_element):
    return div(
        style=column() + Style(width='25%')
    ).adopt([
        p(
            content=title,
            style=Style(
                font_size='14px',
                color='white',
                background=Palette.Charcoal,
                font_style='italic',
                padding='6px',
                font_weight='bold',
                border_radius='10px',
                margin_bottom='24px',
                margin_top='24px'
            )
        ),
        iframe(
            srcdoc=Museflow.render(
                root=root_element,
                script=script_element
            ),
            style=Style(
                width='100%',
                height='100%',
                border='1px solid WhiteSmoke',
                border_radius='10px'
            )
        ),
    ])


def create_component_examples():
    return div(
        style=row() + Style(
            background='white',
            margin_bottom='24px'
        )
    ).adopt([
        create_component_card('Theme Slider', theme_slider_root, theme_slider_script),
        create_component_card('Countdown', countdown_root, countdown_script),
        create_component_card('Dialer', dialer_root, dialer_script),
    ])


def create_image_snippet_card(
        title: str,
        image_filename: str,
        image_width_px: int = None,
        image_height_px: int = None
):
    image_path = Path(__file__).parent.resolve() / 'code_snippet' / image_filename

    return div(
        style=column() + Style(
            width='40%',
            margin_bottom='24px',
            margin_top='24px'
        )
    ).adopt([
        p(
            content=title,
            style=Style(
                font_size='14px',
                color=Palette.Charcoal,
                border=f'1px solid {Palette.Charcoal}',
                font_style='italic',
                padding='6px',
                font_weight='bold',
                border_radius='10px',
                margin_bottom='24px',
                margin_top='0'
            )
        ),
        img(
            src='data:image/png;base64,' + image_to_base64(image_path),
            style=Style(
                width=f'{image_width_px}px' or 'auto',
                height=f'{image_height_px}px' or 'auto',
                border_radius='10px',
                background='Gainsboro'
            )
        )
    ])


def create_tree_simple_section():
    museflow_html_tree_paragraph = '''
    The cornerstone of Museflow's frontend is the ability to construct the entire HTML Tree using native Python objects
    By representing every element as a Python object, developers gain full programmatic control
    This approach allows for dynamic content generation, conditional rendering, and component composition using standard Python features like -
    loops, functions, and classes, all while eliminating context switching between Python logic and declarative HTML syntax
    '''

    return [
        div(
            style=Style(background='white')
        ).adopt([
            p(
                content='Turn your Python logic into fully structured, production-ready HTML - Museflow transforms complex trees into beautiful web pages in a single line of code',
                style=Style(
                    width='100%',
                    text_align='center',
                    background='Teal',
                    color='white',
                    padding='16px 0',
                    margin='0'
                )
            ),
            div(style=row()).adopt(
                div(
                    style=Style(
                        margin_top='24px',
                        background='gainsboro',
                        border_radius='10px',
                        padding='8px'
                    )
                ).adopt([
                    *[
                        p(
                            content=line,
                            style=Style(
                                width='100%',
                                text_align='left',
                                margin='0',
                                padding='2px'
                            )
                        ) for line in museflow_html_tree_paragraph.splitlines()
                    ],
                ]),
            ),
            div(
                style=row() + Style(align_items='flex-start')
            ).adopt([
                create_image_snippet_card(
                    'Museflow Tree - Input (Python)',
                    'museflow-tree-simple-input.png',
                    image_width_px=512
                ),
                create_image_snippet_card(
                    'Museflow Tree - Output (HTML)',
                    'museflow-tree-simple-output.png',
                    image_width_px=512
                ),
            ])
        ])
    ]


def create_script_simple_section():
    museflow_script_paragraph = '''
    A core technical innovation of Museflow is its automatic Python-to-JavaScript compilation
    Through its custom-built compiler, developers can write all their interactive, client-side logic—including event handlers,
    DOM manipulation, and dynamic updates—in pure Python
    When the page is rendered, Museflow seamlessly compiles this Python code into production-ready JavaScript and embeds it directly into the HTML tree
    This capability entirely eliminates the need to manually write or debug JavaScript, 
    ensuring a streamlined, single-language development experience from frontend interactivity to backend API logic
    '''

    return [
        div(
            style=Style(background='white')
        ).adopt([
            p(
                content="Museflow's custom compiler automatically transforms Python into production-ready JavaScript, completely eliminating the need for a separate scripting language",
                style=Style(
                    width='100%',
                    text_align='center',
                    background='Teal',
                    color='white',
                    padding='16px 0',
                    margin='0'
                )
            ),
            div(style=row()).adopt(
                div(
                    style=Style(
                        margin_top='24px',
                        background='gainsboro',
                        border_radius='10px',
                        padding='8px'
                    )
                ).adopt([
                    *[
                        p(
                            content=line,
                            style=Style(
                                width='100%',
                                text_align='left',
                                margin='0',
                                padding='2px'
                            )
                        ) for line in museflow_script_paragraph.splitlines()
                    ],
                ]),
            ),
            div(
                style=row() + Style(align_items='flex-start')
            ).adopt([
                create_image_snippet_card(
                    'Script - Input (Python)',
                    'museflow-pre-compiled-script-simple.png',
                    image_width_px=512
                ),
                create_image_snippet_card(
                    'Script - Output (JavaScript)',
                    'museflow-compiled-script-simple.png',
                    image_width_px=512
                ),
            ])
        ])
    ]


def create_flexible_server_section():
    flexible_server_paragraph = '''
    Museflow's Flexible Server is a robust, Python-native backend solution designed to run full-stack applications without reliance on external web servers
    It handles all standard HTTP requests and APIs, while providing crucial, production-ready capabilities such as graceful shutdown, 
    configurable request size and concurrency limits, and per-request timeouts
    This integration ensures developers maintain a seamless, all-Python environment from the presentation layer to the core server infrastructure
    '''

    return [
        div(
            style=Style(background='white')
        ).adopt([
            p(
                content="Run your entire backend and API in pure Python; Flexible Server delivers production-ready routing and comprehensive concurrency controls",
                style=Style(
                    width='100%',
                    text_align='center',
                    background='Teal',
                    color='white',
                    padding='16px 0',
                    margin='0'
                )
            ),
            div(style=row()).adopt(
                div(
                    style=Style(
                        margin_top='24px',
                        background='gainsboro',
                        border_radius='10px',
                        padding='8px'
                    )
                ).adopt([
                    *[
                        p(
                            content=line,
                            style=Style(
                                width='100%',
                                text_align='left',
                                margin='0',
                                padding='2px'
                            )
                        ) for line in flexible_server_paragraph.splitlines()
                    ],
                ]),
            ),
            div(
                style=row() + Style(align_items='flex-start')
            ).adopt([
                create_image_snippet_card(
                    'Flexible Server - Init',
                    'flexible-server-init.png',
                    image_width_px=512
                ),
                create_image_snippet_card(
                    'Flexible Server - Routes',
                    'flexible-server-routes.png',
                    image_width_px=512
                ),
            ])
        ])
    ]


def create_dev_server_section():
    dev_server_paragraph = '''
    Museflow's Development Server is designed to provide an unparalleled developer experience by automating the feedback loop
    It actively watches your entire project structure, automatically triggering the full render process whenever any Python source file changes
    By serving the resulting HTML on a local web server and supporting live-reloading in the browser, 
    the Development Server ensures that every code change is instantly reflected in the running application, 
    allowing developers to focus purely on writing Python without manual refresh cycles
    '''

    return [
        div(
            style=Style(background='white')
        ).adopt([
            p(
                content="Write your code and see instant results - the Development Server automatically watches, compiles, and serves every code change",
                style=Style(
                    width='100%',
                    text_align='center',
                    background='Teal',
                    color='white',
                    padding='16px 0',
                    margin='0'
                )
            ),
            div(style=row()).adopt(
                div(
                    style=Style(
                        margin_top='24px',
                        background='gainsboro',
                        border_radius='10px',
                        padding='8px'
                    )
                ).adopt([
                    *[
                        p(
                            content=line,
                            style=Style(
                                width='100%',
                                text_align='left',
                                margin='0',
                                padding='2px'
                            )
                        ) for line in dev_server_paragraph.splitlines()
                    ],
                ]),
            ),
            div(
                style=row() + Style(align_items='flex-start')
            ).adopt([
                create_image_snippet_card(
                    'Dev Server - Init',
                    'dev-server-init.png',
                    image_width_px=512
                ),
                create_image_snippet_card(
                    'Dev Server - Module',
                    'dev-server-module.png',
                    image_width_px=512
                ),
            ])
        ])
    ]


root = html().adopt([
    head(),
    body(
        style=Style(
            font_family='Arial, sans-serif',
            margin='0',
            padding='0',
            background=Palette.GhostWhite,
        )
    ).adopt([
        create_header(),
        create_introduction_section(),
        create_component_examples(),
        *create_tree_simple_section(),
        *create_script_simple_section(),
        *create_flexible_server_section(),
        *create_dev_server_section()
    ])
])

Museflow.render_file(root=root, script=None, target_file=Path(__file__).parent.resolve() / 'home.html')
