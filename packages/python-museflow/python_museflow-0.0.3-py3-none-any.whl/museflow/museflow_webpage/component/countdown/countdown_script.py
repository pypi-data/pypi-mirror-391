# <-PY_SKIP->
from toolkit.pyjs_stubs import document, setTimeout

# <-PY_SKIP_END->


display = document.getElementById('countdown')

# FIX: Use a list to hold the count state. This avoids the 'global' keyword
# because we are mutating the list content, not reassigning the 'count' variable.
count = [10]


def tick(event=None):
    # Access the count via the list index
    current_count = count[0]

    display.textContent = current_count

    # Mutate the list content
    count[0] -= 1

    if count[0] < 0:
        count[0] = 10

    # We pass event=None in the signature to make it safe for direct call and setTimeout call
    setTimeout(tick, 1000)


tick()