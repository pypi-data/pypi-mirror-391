import threading
import unittest
from http import HTTPStatus
from http.client import HTTPConnection

from museflow.flexible_server import FlexibleServer, route_handler


class TestGlobalResponseHeaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        @route_handler
        def hello():
            return 'Hello', HTTPStatus.OK

        @route_handler
        def hello_with_custom_header():
            return 'Hello', HTTPStatus.OK, {'X-Custom-Header': 'CustomValue'}

        cls.global_headers = {
            'X-Test-Header': 'TestValue',
            'X-Powered-By': 'FlexibleServer'
        }

        cls.server = FlexibleServer(global_response_headers=cls.global_headers)
        cls.server.add_route('GET', '/', hello)
        cls.server.add_route('GET', '/custom', hello_with_custom_header)

        cls.thread = threading.Thread(target=cls.server.serve, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()

    def test_response_headers_present(self):
        conn = HTTPConnection('localhost', 8001)
        conn.request('GET', '/')
        resp = conn.getresponse()

        for key, value in self.global_headers.items():
            self.assertEqual(resp.getheader(key), value)

        conn.close()

    def test_global_headers_do_not_override_custom(self):
        from http.client import HTTPConnection

        conn = HTTPConnection('localhost', 8001)
        conn.request('GET', '/custom')
        resp = conn.getresponse()

        for key, value in self.global_headers.items():
            self.assertEqual(resp.getheader(key), value)

        self.assertEqual(resp.getheader('X-Custom-Header'), 'CustomValue')

        conn.close()
