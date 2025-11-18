import threading
import time
import unittest
from http import HTTPStatus
from http.client import HTTPConnection

from museflow.flexible_server import FlexibleServer, route_handler


class TestFlexibleServerCrud(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        @route_handler
        def hello_get(query):
            name = query.get('name', 'World')
            return f'<h1>Hello (GET), {name}!</h1>', HTTPStatus.OK

        @route_handler
        def hello_post(body):
            data = body or dict()
            return f'<h1>Hello (POST), body={data}</h1>', HTTPStatus.OK

        @route_handler
        def hello_put(body):
            return f'<h1>Updated resource with data: {body}</h1>', HTTPStatus.OK

        @route_handler
        def hello_delete(query):
            resource_id = query.get('id', 'unknown')
            return f'<h1>Deleted resource {resource_id}</h1>', HTTPStatus.OK

        @route_handler
        def hello_patch(body, query):
            import json
            updated_fields = {}
            if body:
                try:
                    updated_fields = json.loads(body)
                except json.JSONDecodeError:
                    return 'Invalid JSON body', HTTPStatus.BAD_REQUEST

            updated_field_names = ', '.join(updated_fields.keys()) if updated_fields else 'none'
            return f'User {query.get("id", "unknown")} updated fields: {updated_field_names}', HTTPStatus.OK

        # Start server in a separate thread
        cls.server = FlexibleServer()
        cls.server.add_route('GET', '/', hello_get)
        cls.server.add_route('POST', '/', hello_post)
        cls.server.add_route('PUT', '/', hello_put)
        cls.server.add_route('DELETE', '/', hello_delete)
        cls.server.add_route('PATCH', '/', hello_patch)

        cls.thread = threading.Thread(target=cls.server.serve, daemon=True)
        cls.thread.start()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()

    def test_flexible_server_get_route(self):
        conn = HTTPConnection('localhost', 8001)
        conn.request('GET', '/?name=Alice')
        resp = conn.getresponse()
        content = resp.read().decode()
        self.assertEqual(HTTPStatus.OK, resp.status)
        self.assertIn('Hello (GET), Alice', content)
        conn.close()

    def test_flexible_server_post_route(self):
        conn = HTTPConnection('localhost', 8001)
        body = '{"foo":"bar"}'
        headers = {'Content-Type': 'application/json'}
        conn.request('POST', '/', body=body, headers=headers)
        resp = conn.getresponse()
        content = resp.read().decode()
        self.assertEqual(HTTPStatus.OK, resp.status)
        self.assertIn('body={"foo":"bar"}', content)
        conn.close()

    def test_flexible_server_put_route(self):
        conn = HTTPConnection('localhost', 8001)
        body = 'update data'
        conn.request('PUT', '/', body=body)
        resp = conn.getresponse()
        content = resp.read().decode()
        self.assertEqual(HTTPStatus.OK, resp.status)
        self.assertIn('Updated resource with data: update data', content)
        conn.close()

    def test_flexible_server_delete_route(self):
        conn = HTTPConnection('localhost', 8001)
        conn.request('DELETE', '/?id=123')
        resp = conn.getresponse()
        content = resp.read().decode()
        self.assertEqual(HTTPStatus.OK, resp.status)
        self.assertIn('Deleted resource 123', content)
        conn.close()

    def test_flexible_server_patch_route(self):
        conn = HTTPConnection('localhost', 8001)
        body = '{"name":"Alice"}'
        headers = {'Content-Type': 'application/json'}
        conn.request('PATCH', '/?id=123', body=body, headers=headers)
        resp = conn.getresponse()
        content = resp.read().decode()
        self.assertEqual(HTTPStatus.OK, resp.status)
        self.assertIn('User 123 updated fields: name', content)
        conn.close()
