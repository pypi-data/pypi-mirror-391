# <-PY_SKIP->
from toolkit.pyjs_stubs import document

# <-PY_SKIP_END->

slider = document.getElementById('theme-slider')
body = document.getElementById('body')


def on_slider_input(event):
    value = slider.value  # 0 to 100
    shade = (value / 100) * 255
    body.style.backgroundColor = f'rgb({shade}, {shade}, {shade})'


slider.addEventListener('input', on_slider_input)
