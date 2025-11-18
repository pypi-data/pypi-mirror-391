import logging
import threading
import time
import unittest
from collections import Counter
from http import HTTPStatus
from http.client import HTTPConnection

from museflow.flexible_server import FlexibleServer, route_handler


class TestFlexibleServerLogging(unittest.TestCase):
    def test_logging_enabled(self):
        import logging
        from museflow.flexible_server import FlexibleServer

        logger = logging.getLogger('TestLogger')
        logger.setLevel(logging.INFO)
        logger.handlers = []

        server = FlexibleServer(logger=logger, log=True)

        # Capture logs for assertion
        with self.assertLogs(logger, level='DEBUG') as cm:
            server._logger.debug('DEBUG')
            server._logger.info('INFO')
            server._logger.warning('WARNING')
            server._logger.error('ERROR')

        self.assertEqual(
            Counter([
                'DEBUG:TestLogger:DEBUG',
                'INFO:TestLogger:INFO',
                'WARNING:TestLogger:WARNING',
                'ERROR:TestLogger:ERROR'
            ]),
            Counter(cm.output)
        )

    def test_logging_disabled(self):
        import logging
        from museflow.flexible_server import FlexibleServer

        logger = logging.getLogger('TestLogger')
        logger.setLevel(logging.DEBUG)
        logger.handlers = []

        class SpyHandler(logging.Handler):
            def __init__(self):
                super().__init__()
                self.records = []

            def emit(self, record):
                self.records.append(record)

        spy = SpyHandler()
        logger.addHandler(spy)

        server = FlexibleServer(logger=logger, log=False)

        server._logger.debug('DEBUG')
        server._logger.info('INFO')
        server._logger.warning('WARNING')
        server._logger.error('ERROR')

        self.assertEqual(0, len(spy.records), 'No logs should be emitted when log=False')

    def test_logging_enabled_for_requests(self):
        # Spy handler to capture logs
        logger = logging.getLogger('TestLogger')
        logger.setLevel(logging.DEBUG)
        spy_records = []

        class SpyHandler(logging.Handler):
            def emit(self, record):
                spy_records.append(record)

        logger.addHandler(SpyHandler())

        @route_handler
        def hello_handler():
            return 'ok', HTTPStatus.OK

        server = FlexibleServer(logger=logger, log=True)
        server.add_route('GET', '/', hello_handler)

        thread = threading.Thread(target=server.serve, daemon=True)
        thread.start()
        time.sleep(1)

        conn = HTTPConnection('localhost', 8001)
        conn.request('GET', '/')
        resp = conn.getresponse()
        resp.read()
        conn.close()

        server.shutdown()
        thread.join()

        self.assertGreater(len(spy_records), 0, 'Logs should be emitted when log=True')

    def test_logging_disabled_for_requests(self):
        logger = logging.getLogger('TestLogger')
        logger.setLevel(logging.DEBUG)
        spy_records = []

        class SpyHandler(logging.Handler):
            def emit(self, record):
                spy_records.append(record)

        logger.addHandler(SpyHandler())

        @route_handler
        def hello_handler():
            return 'ok', HTTPStatus.OK

        server = FlexibleServer(logger=logger, log=False)
        server.add_route('GET', '/', hello_handler)

        thread = threading.Thread(target=server.serve, daemon=True)
        thread.start()
        time.sleep(1)

        conn = HTTPConnection('localhost', 8001)
        conn.request('GET', '/')
        resp = conn.getresponse()
        resp.read()
        conn.close()

        server.shutdown()
        thread.join()

        self.assertEqual(0, len(spy_records), 'No logs should be emitted when log=False')
