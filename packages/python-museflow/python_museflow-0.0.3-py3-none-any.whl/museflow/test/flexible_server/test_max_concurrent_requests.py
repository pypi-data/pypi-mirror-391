import threading
import unittest
from http import HTTPStatus
from http.client import HTTPConnection

from museflow.flexible_server import FlexibleServer, route_handler


class TestFlexibleServerMaxConcurrentRequests(unittest.TestCase):
    @staticmethod
    @route_handler
    def hello_get(query):
        name = query.get('name', 'World')
        return f'<h1>Hello (GET), {name}!</h1>', HTTPStatus.OK

    def setUp(self):
        self.server = FlexibleServer(max_concurrent_requests=0)
        self.server.add_route('GET', '/', TestFlexibleServerMaxConcurrentRequests.hello_get)
        self.thread = threading.Thread(target=lambda: self.server.serve(host='localhost', port=8020))
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(timeout=2)

    def test_requests_rejected_when_limit_zero(self):
        results = []

        def make_request():
            conn = HTTPConnection('localhost', 8020)
            conn.request('GET', '/')
            res = conn.getresponse()
            results.append(res.status)
            conn.close()

        threads = [threading.Thread(target=make_request) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertTrue(any(status == HTTPStatus.SERVICE_UNAVAILABLE for status in results), f'Expected *SOME 503s, got {results}')
