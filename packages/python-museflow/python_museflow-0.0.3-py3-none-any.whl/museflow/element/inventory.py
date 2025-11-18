"""
HTML Element Inventory

Provides a convenient set of pre-configured HTML element factories using ElementFactory
Each element constructor returns an Element instance that can be composed hierarchically

Usage:
    from inventory import div, span, strong

    # Build elements
    my_div = div(_id="container").adopt(
        span(content="Hello ").adopt(strong(content="World!"))
    )

    print(my_div.render())

Note:
    Elements marked as void (e.g., <img>, <br>, <input>, etc.)
    cannot contain child elements or text content
"""

from museflow.element.element_factory import ElementFactory

# Root HTML Element
html = ElementFactory('html').produce
head = ElementFactory('head').produce
body = ElementFactory('body').produce
title = ElementFactory('title').produce

# Inline / Textual Elements
span = ElementFactory('span').produce
strong = ElementFactory('strong').produce
em = ElementFactory('em').produce
b = ElementFactory('b').produce
i = ElementFactory('i').produce
u = ElementFactory('u').produce
small = ElementFactory('small').produce
mark = ElementFactory('mark').produce
a = ElementFactory('a').produce
code = ElementFactory('code').produce
pre = ElementFactory('pre').produce
blockquote = ElementFactory('blockquote').produce
p = ElementFactory('p').produce

# Headings
h1 = ElementFactory('h1').produce
h2 = ElementFactory('h2').produce
h3 = ElementFactory('h3').produce
h4 = ElementFactory('h4').produce
h5 = ElementFactory('h5').produce
h6 = ElementFactory('h6').produce

# Structural / Containers
div = ElementFactory('div').produce
section = ElementFactory('section').produce
article = ElementFactory('article').produce
header = ElementFactory('header').produce
footer = ElementFactory('footer').produce
main = ElementFactory('main').produce
aside = ElementFactory('aside').produce
nav = ElementFactory('nav').produce

# Lists
ul = ElementFactory('ul').produce
ol = ElementFactory('ol').produce
li = ElementFactory('li').produce

# Tables
table = ElementFactory('table').produce
thead = ElementFactory('thead').produce
tbody = ElementFactory('tbody').produce
tfoot = ElementFactory('tfoot').produce
tr = ElementFactory('tr').produce
td = ElementFactory('td').produce
th = ElementFactory('th').produce
caption = ElementFactory('caption').produce

# Forms
form = ElementFactory('form').produce
input_ = ElementFactory('input', is_void_element=True).produce
textarea = ElementFactory('textarea').produce
button = ElementFactory('button').produce
label = ElementFactory('label').produce
select = ElementFactory('select').produce
option = ElementFactory('option').produce
fieldset = ElementFactory('fieldset').produce
legend = ElementFactory('legend').produce

# Media
img = ElementFactory('img', is_void_element=True).produce
video = ElementFactory('video').produce
audio = ElementFactory('audio').produce
canvas = ElementFactory('canvas').produce
svg = ElementFactory('svg').produce
figure = ElementFactory('figure').produce
figcaption = ElementFactory('figcaption').produce

# Misc / Semantic
br = ElementFactory('br', is_void_element=True).produce
hr = ElementFactory('hr', is_void_element=True).produce
meta = ElementFactory('meta', is_void_element=True).produce
link = ElementFactory('link', is_void_element=True).produce
source = ElementFactory('source', is_void_element=True).produce
track = ElementFactory('track', is_void_element=True).produce
col = ElementFactory('col', is_void_element=True).produce
base = ElementFactory('base', is_void_element=True).produce
wbr = ElementFactory('wbr', is_void_element=True).produce
template = ElementFactory('template').produce
details = ElementFactory('details').produce
summary = ElementFactory('summary').produce
iframe = ElementFactory('iframe').produce

# Script
script = ElementFactory('script').produce

# Style
style = ElementFactory('style').produce
