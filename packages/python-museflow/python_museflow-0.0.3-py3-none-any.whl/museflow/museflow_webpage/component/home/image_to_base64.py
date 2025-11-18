import base64
from pathlib import Path


def image_to_base64(image_path: Path):
    with image_path.open('rb') as fd:
        encoded_string = base64.b64encode(fd.read()).decode('utf-8')
    return encoded_string
