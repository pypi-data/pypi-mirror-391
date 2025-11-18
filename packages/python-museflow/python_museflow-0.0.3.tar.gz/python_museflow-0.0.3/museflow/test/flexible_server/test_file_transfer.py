import json
import os
import shutil
import tempfile
import threading
import unittest
import urllib
from http import HTTPStatus

import requests

from museflow.flexible_server import FlexibleServer, route_handler


class TestFlexibleServerFileUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = FlexibleServer()

        @route_handler
        def upload_with_body(body, files):
            data = json.loads(body) if body else None

            file_path = files.get('file')
            saved_file_path = os.path.join(tempfile.gettempdir(), 'uploaded_file.bin')
            shutil.copy(file_path, saved_file_path)

            return {'body': data, 'file': saved_file_path}, HTTPStatus.OK

        @route_handler
        def download_file(query):
            """ Serve an uploaded file from temp dir """
            filename = query.get('file')
            if not filename:
                return 'Missing "file" parameter', HTTPStatus.BAD_REQUEST

            filepath = os.path.join(tempfile.gettempdir(), filename)
            if not os.path.exists(filepath):
                return 'File not found', HTTPStatus.NOT_FOUND

            with open(filepath, 'rb') as fd:
                content = fd.read()
            return content, HTTPStatus.OK  # return bytes

        cls.server.add_route('GET', '/download', download_file)

        cls.server.add_route('POST', '/upload_with_body', upload_with_body)

        cls.thread = threading.Thread(
            target=cls.server.serve,
            kwargs={'host': 'localhost', 'port': 8001},
            daemon=True
        )
        cls.thread.start()

        import time
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()

    def test_file_and_json_body(self):
        content = os.urandom(1 * 1024 * 1024)
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(content)
        temp_file.close()

        json_body = {'first_name': 'Jane', 'last_name': 'Doe'}

        with open(temp_file.name, 'rb') as fd:
            files = {'file': ('file.bin', fd, 'application/octet-stream')}
            data = {'body': json.dumps(json_body)}

            res = requests.post('http://localhost:8001/upload_with_body', files=files, data=data)
            res_json = res.json()

        os.unlink(temp_file.name)

        # Verify body
        self.assertEqual(HTTPStatus.OK, res.status_code)
        self.assertEqual(res_json['body'], json_body)

        # Verify file
        with open(res_json['file'], 'rb') as fd:
            self.assertEqual(fd.read(), content)

    def test_download_uploaded_file(self):
        content = os.urandom(512 * 1024)
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(content)
        temp_file.close()

        json_body = {'first_name': 'John', 'last_name': 'Doe'}

        with open(temp_file.name, 'rb') as fd:
            files = {'file': ('file.bin', fd, 'application/octet-stream')}
            data = {'body': json.dumps(json_body)}
            res = requests.post('http://localhost:8001/upload_with_body', files=files, data=data)
            res_json = res.json()

        os.unlink(temp_file.name)

        filename = os.path.basename(res_json['file'])
        params = {'file': filename}
        url = f'http://localhost:8001/download?{urllib.parse.urlencode(params)}'  # noqa
        res_download = requests.get(url)

        self.assertEqual(res_download.status_code, HTTPStatus.OK)
        self.assertEqual(res_download.content, content)

        self.assertEqual(res_download.status_code, HTTPStatus.OK)
        self.assertEqual(res_download.content, content)
