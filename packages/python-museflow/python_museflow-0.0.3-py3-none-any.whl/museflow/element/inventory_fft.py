FACTORY_MAP = {}
import museflow

for name, obj in vars(museflow.element.inventory).items():
    if callable(obj):
        FACTORY_MAP[name] = obj


def factory_for_tag(tag: str):
    """
    Retrieve the ElementFactory produce callable for a given HTML tag from the inventory

    This function dynamically looks up the corresponding element factory in the
    `element.inventory` module. It handles Python keyword conflicts (E.G. 'input' -> 'input_')
    and returns the produce callable, which preserves the factory's defaults such as `is_void_element`

    Parameters:
        tag (str): The HTML tag name to retrieve (e.g., 'div', 'input', 'span')

    Returns:
        Callable: The `produce` callable for creating an Element instance with the
                  factory defaults applied. Returns None if the tag is not found in inventory

    Example:
        produce_div = factory_for_tag('div')
        el = produce_div(_id='container', content='Hello World')
        print(el.render())  # <div id="container">Hello World</div>
    """
    inventory_tag = f'{tag}_' if f'{tag}_' in FACTORY_MAP else tag
    return FACTORY_MAP.get(inventory_tag)
