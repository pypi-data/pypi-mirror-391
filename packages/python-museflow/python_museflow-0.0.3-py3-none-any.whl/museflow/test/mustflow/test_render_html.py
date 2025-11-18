import os
import unittest
from pathlib import Path

from museflow.element.inventory import html, head, body, div, h1, img, br, hr, input_, meta, link
from museflow.element.style import Style
from museflow.museflow import Museflow


class TestRenderHTML(unittest.TestCase):
    def test_render(self):
        root = html().adopt([
            head(),
            body().adopt(
                div(_id='container').adopt(
                    h1(content='Hello World')
                )
            )
        ])

        with open('../cachet/simple.html', 'r') as fd:
            expected_html_text = fd.read()

        html_text = Museflow.render(root)
        self.assertEqual(expected_html_text, html_text)

    def test_render_file(self):
        root = html().adopt([
            head(),
            body().adopt(
                div(_id='container').adopt(
                    h1(content='Hello World')
                )
            )
        ])

        mf = Museflow()
        mf.render_file(root=root, target_file=Path('index.html'))

        with open('./index.html', 'r') as fd:
            actual_html_text = fd.read()

        with open('../cachet/simple.html', 'r') as fd:
            expected_html_text = fd.read()

        try:
            self.assertEqual(expected_html_text, actual_html_text)
        except Exception as e:
            raise e
        finally:
            if os.path.exists('./index.html'):
                os.remove('./index.html')

    def test_render_embedded_script(self):
        root = html().adopt([
            head(),
            body().adopt(
                div(_id='container').adopt(
                    h1(content='Hello World')
                )
            )
        ])

        mf = Museflow()
        py_script = mf.load_py_script(script_file=Path('../cachet/embedded_script.py'))

        with open('../cachet/embedded_script.html', 'r') as fd:
            expected_html_text = fd.read()

        html_text = Museflow.render(root=root, script=py_script)

        self.assertEqual(expected_html_text, html_text)

    def test_render_style(self):
        root = html().adopt([
            head(),
            body().adopt(
                div().adopt(
                    h1(
                        content='Hello World',
                        style=Style(
                            font_size='16px',
                            color='red'
                        )
                    )
                )
            )
        ])

        with open('../cachet/style.html', 'r') as fd:
            expected_html_text = fd.read()

        html_text = Museflow.render(root=root)

        self.assertIn('Hello World', html_text)
        self.assertIn('font-size: 16px', html_text)
        self.assertIn('color: red', html_text)
        self.assertEqual(expected_html_text, html_text)

    def test_style_update(self):
        base_style = Style(
            font_size='16px',
            color='red',
            margin='10px'
        )

        extra_style = Style(
            color='blue',
            padding='5px'
        )

        updated_style = base_style.update(extra_style)

        # Check merged attributes
        self.assertEqual('16px', updated_style.font_size)
        self.assertEqual('blue', updated_style.color)
        self.assertEqual('10px', updated_style.margin)
        self.assertEqual('5px', updated_style.padding)

        # Check that the base and extra are unchanged
        self.assertEqual('red', base_style.color)
        self.assertTrue(base_style.padding is None)
        self.assertEqual('blue', extra_style.color)
        self.assertEqual('5px', extra_style.padding)

    def test_void_elements_cannot_have_content(self):
        """ Void elements must not accept content or children """
        void_elements = [img, br, hr, input_, meta, link]
        for element in void_elements:
            try:
                element().adopt('Hello World')
            except RuntimeError:
                pass
            else:
                raise Exception('Void element should not adopt')

    def test_void_elements_render_self_closing(self):
        """ Void elements must render as self-closing tags without closing tags """
        element = img(_id='logo', src='logo.png')
        element_text = element.render()
        self.assertEqual('<img id="logo" src="logo.png">', element_text)

    def test_preprocess_script_imports(self):
        """ Ensure that imports are detected and inlined properly """
        mf = Museflow()
        py_script = mf.load_py_script(script_file=Path('../cachet/preprocess_script_imports/main.py'))

        root = html().adopt([
            head(),
            body().adopt([
                h1('Hello World'),
                div(_id='result')
            ])
        ])

        with open('../cachet/preprocess_script_imports/preprocess_script_imports.html') as fd:
            expected_html_text = fd.read()

        html_text = mf.render(root=root, script=py_script)

        self.assertEqual(expected_html_text, html_text)
