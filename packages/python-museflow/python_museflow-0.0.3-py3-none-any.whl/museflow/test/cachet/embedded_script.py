# <-PY_SKIP->
from toolkit.pyjs_stubs import document
# <-PY_SKIP_END->

container = document.getElementById('container')

name_input = document.createElement('input')
name_input.id = 'name'
name_input.placeholder = 'Type your name ..'
container.appendChild(name_input)

button = document.createElement('button')
button.textContent = 'Say Hello'
container.appendChild(button)

output = document.createElement('p')
container.appendChild(output)


def greet(event):
    name = name_input.value or 'World'
    output.textContent = f'Hello, {name}!'


button.addEventListener('click', greet)
