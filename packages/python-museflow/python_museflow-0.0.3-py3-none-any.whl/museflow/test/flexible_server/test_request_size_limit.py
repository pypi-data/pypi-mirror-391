import threading
import unittest
from http import HTTPStatus
from http.client import HTTPConnection

from museflow.flexible_server import FlexibleServer, route_handler


class TestFlexibleServerRequestSizeLimit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        @route_handler
        def echo_handler(body):
            return body or '', HTTPStatus.OK

        cls.server = FlexibleServer(request_size_limit=10)
        cls.server.add_route('POST', '/', echo_handler)

        cls.thread = threading.Thread(target=cls.server.serve, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()

    def test_request_too_large(self):
        conn = HTTPConnection('localhost', 8001)
        # Send 20 bytes, exceeding the 10-byte limit
        conn.request('POST', '/', body='x' * 20)
        resp = conn.getresponse()
        content = resp.read().decode()
        self.assertEqual(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, resp.status)
        self.assertIn('Request entity too large', content)
        conn.close()

    def test_request_within_limit(self):
        conn = HTTPConnection('localhost', 8001)
        # Send 5 bytes, within the limit
        conn.request('POST', '/', body='abcde')
        resp = conn.getresponse()
        content = resp.read().decode()
        self.assertEqual(HTTPStatus.OK, resp.status)
        self.assertEqual('abcde', content)
        conn.close()
