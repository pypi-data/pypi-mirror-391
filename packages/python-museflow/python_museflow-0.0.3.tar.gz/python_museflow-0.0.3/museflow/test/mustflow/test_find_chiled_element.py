import unittest

from museflow.element.inventory import html, head, body, div, h1
from museflow.museflow import Museflow


class TestFindChildElement(unittest.TestCase):
    def test_find_child_element(self):
        root = html().adopt([
            head(),
            body().adopt(
                div(_id='container')
            )
        ])

        container = root.find_child_element(_id='container')
        container.adopt(h1(content='Hello World'))

        with open('../cachet/simple.html', 'r') as fd:
            expected_html_text = fd.read()

        html_text = Museflow.render(root)
        self.assertEqual(expected_html_text, html_text)
