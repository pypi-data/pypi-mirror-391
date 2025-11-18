import unittest

from museflow.museflow import Museflow


class TestMuseflowInterpret(unittest.TestCase):
    def test_interpret(self):
        with open('../cachet/simple.html') as fd:
            source_html_text = fd.read()

        root = Museflow.interpret(html_text=source_html_text)
        html_text = Museflow.render(root=root)
        self.assertEqual(source_html_text, html_text)

    def test_interpret_embedded_script(self):
        with open('../cachet/embedded_script.html') as fd:
            expected_html_text = fd.read()

        root = Museflow.interpret(html_text=expected_html_text)
        html_text = Museflow.render(root=root)
        self.assertEqual(expected_html_text, html_text)

    def test_interpret_embedded_style(self):
        with open('../cachet/embedded_style.html') as fd:
            expected_html_text = fd.read()

        root = Museflow.interpret(html_text=expected_html_text)
        html_text = Museflow.render(root=root)
        self.assertEqual(expected_html_text, html_text)

    def test_interpret_inline_attrs(self):
        with open('../cachet/inline_attrs.html', encoding='utf-8') as fd:
            source_html_text = fd.read().strip()

        root = Museflow.interpret(html_text=source_html_text)

        html_text = Museflow.render(root=root, indent=2).strip()

        self.assertEqual(source_html_text, html_text)
