import threading
import time
import unittest
from http import HTTPStatus
from http.client import HTTPConnection

from museflow.flexible_server import FlexibleServer, route_handler, FlexibleServerException


class TestFlexibleServerErrorHandling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        @route_handler
        def error_handler():
            raise RuntimeError('Handler error!')

        cls.server = FlexibleServer()
        cls.server.add_route('GET', '/error', error_handler)
        cls.thread = threading.Thread(target=cls.server.serve, daemon=True)
        cls.thread.start()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()

    def test_internal_server_error(self):
        conn = HTTPConnection('localhost', 8001)
        conn.request('GET', '/error')
        resp = conn.getresponse()
        self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, resp.status)
        content = resp.read().decode()
        self.assertIn('Internal Server Error', content)
        conn.close()

    def test_invalid_handler(self):
        self.server.add_route('GET', '/noncallable', 'not-a-function')

        # Nocallable Handler
        conn = HTTPConnection('localhost', 8001)
        conn.request('GET', '/noncallable')
        resp = conn.getresponse()
        self.assertEqual(HTTPStatus.BAD_REQUEST, resp.status)
        conn.close()

        # Unhallowed method
        @route_handler
        def invalid_sig():
            return 'ok', HTTPStatus.OK

        try:
            self.server.add_route('Unallowed', '/invalidsig', invalid_sig)
        except FlexibleServerException:
            pass
