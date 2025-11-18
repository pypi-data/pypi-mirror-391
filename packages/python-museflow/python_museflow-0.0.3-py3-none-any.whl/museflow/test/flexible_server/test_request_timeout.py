import threading
import time
import unittest
from http.client import HTTPConnection
from http import HTTPStatus

from museflow.flexible_server import FlexibleServer, route_handler


class TestFlexibleServerRequestTimeout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        @route_handler
        def slow_handler():
            time.sleep(3)
            return 'done', HTTPStatus.OK

        # Start the server with a short timeout (1 second)
        cls.server = FlexibleServer(request_timeout=1)
        cls.server.add_route('GET', '/', slow_handler)

        cls.thread = threading.Thread(target=cls.server.serve, daemon=True)
        cls.thread.start()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()

    def test_request_timeout_exceeded(self):
        conn = HTTPConnection('localhost', 8001, timeout=5)
        conn.request('GET', '/')
        resp = conn.getresponse()
        content = resp.read().decode()

        # Verify timeout response
        self.assertEqual(HTTPStatus.GATEWAY_TIMEOUT, resp.status)
        self.assertIn('Request timed out', content)

        conn.close()
