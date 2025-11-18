# <-PY_SKIP->
from toolkit.pyjs_stubs import document
# <-PY_SKIP_END->

display = document.getElementById('dial-display')


def clear_input(event):
    display.value = ''

display.addEventListener('click', clear_input)

keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#']

def make_onclick(key):
    def onclick(event):
        display.value += key
    return onclick

for key in keys:
    btn = document.getElementById(f'key-{key}')
    btn.addEventListener('click', make_onclick(key))
