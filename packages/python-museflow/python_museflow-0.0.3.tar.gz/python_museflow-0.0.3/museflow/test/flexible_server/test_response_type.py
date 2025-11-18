import threading
import unittest
from http import HTTPStatus

import requests

from museflow.flexible_server import FlexibleServer, route_handler


class TestFlexibleServerResponseType(unittest.TestCase):
    """
    Verifies that FlexibleServer properly handles handler return types:

    - When the handler returns a string:
        - The response body is sent as-is
        - The Content-Type header is 'text/html'

    - When the handler returns a JSON-serializable object (E.G. dict):
        - The response body is JSON-encoded
        - The Content-Type header is 'application/json'

    This ensures that the server automatically adapts responses according to
    the return type of the handler, without requiring the handler to set headers manually
    """

    @classmethod
    def setUpClass(cls):
        cls.server = FlexibleServer()

        @route_handler
        def str_handler():
            return 'Hello world', HTTPStatus.OK

        @route_handler
        def json_handler():
            return {'message': 'Hello JSON'}, HTTPStatus.OK

        cls.server.add_route('GET', '/str', str_handler)
        cls.server.add_route('GET', '/json', json_handler)

        cls.thread = threading.Thread(
            target=cls.server.serve,
            kwargs={'host': 'localhost', 'port': 8010},
            daemon=True
        )
        cls.thread.start()
        import time
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()

    def test_string_response(self):
        res = requests.get('http://localhost:8010/str')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(res.headers['Content-Type'], 'text/html')
        self.assertEqual(res.text, 'Hello world')

    def test_json_response(self):
        res = requests.get('http://localhost:8010/json')
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual('application/json', res.headers['Content-Type'])
        data = res.json()
        self.assertEqual(data, {'message': 'Hello JSON'})
