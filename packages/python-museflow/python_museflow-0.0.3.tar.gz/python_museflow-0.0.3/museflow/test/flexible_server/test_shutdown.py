import signal
import socket
import threading
import time
import unittest
from http import HTTPStatus

from museflow.flexible_server import FlexibleServer, route_handler


class TestFlexibleServerShutdown(unittest.TestCase):
    def test_server_thread_stops_on_shutdown(self):
        server = FlexibleServer()
        server.add_route('GET', '/', lambda query: ('ok', HTTPStatus.OK))

        thread = threading.Thread(target=server.serve, daemon=True)
        thread.start()
        time.sleep(1)

        server.shutdown()

        thread.join(timeout=2)
        self.assertFalse(thread.is_alive(), 'Server thread should stop after shutdown')

    def test_server_is_not_running_after_shutdown(self):
        server = FlexibleServer()
        server.add_route('GET', '/', lambda query: ('ok', HTTPStatus.OK))

        thread = threading.Thread(target=server.serve, daemon=True)
        thread.start()
        time.sleep(1)

        server.shutdown()
        self.assertFalse(server.is_running(), '__running should be False after shutdown')

    def test_port_released_after_shutdown(self):
        server = FlexibleServer()
        server.add_route('GET', '/', lambda query: ('ok', HTTPStatus.OK))

        thread = threading.Thread(target=server.serve, daemon=True)
        thread.start()
        time.sleep(1)

        server.shutdown()
        thread.join()
        time.sleep(1)

        sock = socket.socket()

        try:
            sock.bind(('localhost', 8001))
            bound = True
        except OSError:
            bound = False
        finally:
            sock.close()

        self.assertTrue(bound, 'Port should be released after shutdown')

    def test_keyboard_interrupt_shuts_down_server(self):
        # Simple handler
        @route_handler
        def hello_get():
            return 'ok', HTTPStatus.OK

        server = FlexibleServer()
        server.add_route('GET', '/', hello_get)

        def run_server():
            try:
                server.serve()
            except KeyboardInterrupt:
                pass

        t = threading.Thread(target=run_server)
        t.start()
        time.sleep(1)

        def raise_interrupt():
            t_id = t.ident
            import ctypes
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(t_id),
                ctypes.py_object(KeyboardInterrupt)
            )

        raise_interrupt()
        t.join(timeout=2)

        self.assertFalse(server.is_running(), 'Server should stop on KeyboardInterrupt')

    def test_signal_shutdown(self):
        for sig in [signal.SIGINT, signal.SIGTERM]:
            server = FlexibleServer()
            server.add_route('GET', '/', lambda query: ('ok', HTTPStatus.OK))

            thread = threading.Thread(target=server.serve, daemon=True)
            thread.start()
            time.sleep(1)

            server._handle_signal(sig)
            thread.join(timeout=2)
