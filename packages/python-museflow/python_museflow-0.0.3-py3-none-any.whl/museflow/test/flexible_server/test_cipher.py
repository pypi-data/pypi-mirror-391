import os
import tempfile
import threading
import unittest
from http import HTTPStatus

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.x509 import load_pem_x509_certificate

from museflow.flexible_server import FlexibleServer, route_handler


class TestFlexibleServerCipher(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_generate_key(self):
        key_file = os.path.join(self.temp_dir.name, 'key.pem')
        key = FlexibleServer.generate_key(key_file=key_file)
        self.assertTrue(os.path.exists(key_file))

        with open(key_file, 'rb') as f:
            loaded_key = serialization.load_pem_private_key(f.read(), password=None)
        self.assertEqual(key.private_numbers(), loaded_key.private_numbers())

    def test_generate_certificate(self):
        key_file = os.path.join(self.temp_dir.name, 'key.pem')
        cert_file = os.path.join(self.temp_dir.name, 'cert.pem')
        key = FlexibleServer.generate_key(key_file=key_file)

        cert = FlexibleServer.generate_certificate(
            cert_file=cert_file,
            key=key,
            common_name='localhost',
            organization='TestOrg',
            country_code='US',
        )
        self.assertTrue(os.path.exists(cert_file))

        with open(cert_file, 'rb') as f:
            loaded_cert = load_pem_x509_certificate(f.read())

        self.assertEqual(cert.serial_number, loaded_cert.serial_number)
        self.assertEqual(cert.subject, loaded_cert.subject)

    def test_self_signed_ssl_context_with_existing_files(self):
        key_file = os.path.join(self.temp_dir.name, 'key.pem')
        cert_file = os.path.join(self.temp_dir.name, 'cert.pem')
        key = FlexibleServer.generate_key(key_file)
        FlexibleServer.generate_certificate(
            cert_file=cert_file,
            key=key,
            common_name='localhost',
            organization='TestOrg',
            country_code='US'
        )
        with FlexibleServer.self_signed_ssl_context() as ctx:
            self.assertEqual(['cert_file', 'key_file', 'ca_file'], list(ctx.keys()))

    def test_https_server_with_flexible_server(self):
        def request(url: str):
            return requests.get(url, verify=False)

        key_file = os.path.join(self.temp_dir.name, 'key.pem')
        cert_file = os.path.join(self.temp_dir.name, 'cert.pem')

        key = FlexibleServer.generate_key(key_file=key_file)
        FlexibleServer.generate_certificate(
            cert_file=cert_file,
            key=key,
            common_name='localhost',
            organization='TestOrg',
            country_code='US'
        )

        server = FlexibleServer()

        @route_handler
        def root():
            return '<h1>Hello HTTPS</h1>', HTTPStatus.OK

        server.add_route('GET', '/', root)

        # Create SSL context
        with FlexibleServer.self_signed_ssl_context() as ctx:
            thread = threading.Thread(
                target=lambda: server.serve(
                    cert_file=ctx['cert_file'],
                    key_file=ctx['key_file']
                ),
                daemon=True
            )
            thread.start()

            try:
                res = request('https://localhost:8001/')
                self.assertEqual(HTTPStatus.OK, res.status_code)
                self.assertIn('Hello HTTPS', res.text)
            finally:
                server.shutdown()
                thread.join()
