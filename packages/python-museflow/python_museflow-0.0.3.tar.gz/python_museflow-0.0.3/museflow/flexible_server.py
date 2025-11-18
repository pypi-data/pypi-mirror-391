import functools
import inspect
import json
import logging
import os
import signal
import ssl
import tempfile
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any
from typing import Callable, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import SubjectAlternativeName, DNSName
from cryptography.x509.oid import NameOID
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget

from museflow.element.inventory import html, div, h1, h3, p
from museflow.element.style import Style
from museflow.museflow import Museflow


class FlexibleServerException(Exception):
    def __init__(self, message: str):
        super().__init__(f'{self.__class__.__name__}: {message}')


HandlerType = Callable[[str, Optional[str], Dict[str, str]], Tuple[str, int]]

example = '''
#############
#  Example  #
#############

@route_handler
def hello_handler(request: str, body: Optional[str], query: Dict[str, str]):
    name = query.get("name", "World")
    return f"<h1>Hello, {name}!</h1>", 200
'''


class NullLogger(logging.Logger):
    def __init__(self, name='NullLogger'):
        super().__init__(name, level=logging.NOTSET)

    def handle(self, record):
        pass

    def log(self, level, msg, *args, **kwargs):
        record = self.makeRecord(self.name, level, fn='', lno=0, msg=msg, args=args, exc_info=None)
        self.handle(record)


def route_handler(func):
    """
    Decorator for HTTP handlers.
    Supports handler signatures like:
        def handler(body=None, files=None, request=None, query=None)
    """

    @functools.wraps(func)
    def wrapper(request, body, files, query):
        sig = inspect.signature(func)
        bound_args = {}
        for name in sig.parameters:
            if name == 'request':
                bound_args[name] = request
            elif name == 'body':
                bound_args[name] = body if body else None
            elif name == 'files':
                bound_args[name] = files if files else dict()
            elif name == 'query':
                bound_args[name] = {k: v[0] if isinstance(v, list) else v for k, v in query.items()}
            else:
                bound_args[name] = None

        result = func(**bound_args)

        if isinstance(result, tuple):
            if len(result) == 2:
                data, code = result
                headers = None
            elif len(result) == 3:
                data, code, headers = result
            elif len(result) == 4:
                data, code, headers, files = result
            else:
                raise FlexibleServerException(f'Handler returned invalid tuple: {result}')
        else:
            data, code, headers, files = result, HTTPStatus.OK, None, dict()

        return data, code, headers

    return wrapper


class _FlexibleHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa
        logger = getattr(self.server, 'logger', None)
        if logger:
            logger.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))

    """ HTTP request handler supporting dynamic routes and methods """

    def __send_response(self, status: int, response_body=None, headers: dict | None = None):
        """
        Sends HTTP response with support for:
          - Handler-provided headers
          - Global server headers (added only if not already set)
          - Automatic Content-Type for str/json
          - Supports str, bytes, dict/list (JSON), and iterables
        """
        self.send_response(status)

        headers = headers or {}
        global_headers = getattr(self.server, 'global_response_headers', {}) or {}

        sent_keys = set()
        for k, v in headers.items():
            self.send_header(k, v)
            sent_keys.add(k.lower())

        for k, v in global_headers.items():
            if k.lower() not in sent_keys:
                self.send_header(k, v)

        if 'content-type' not in sent_keys:
            if isinstance(response_body, (dict, list)):
                self.send_header('Content-Type', 'application/json')
            else:
                self.send_header('Content-Type', 'text/html')

        if response_body is None:
            response_body = b''
        elif isinstance(response_body, (dict, list)):
            response_body = json.dumps(response_body).encode('utf-8')
        elif isinstance(response_body, str):
            response_body = response_body.encode('utf-8')
        elif isinstance(response_body, bytes):
            pass
        elif hasattr(response_body, '__iter__'):
            for chunk in response_body:
                if isinstance(chunk, str):
                    chunk = chunk.encode('utf-8')
                self.wfile.write(chunk)
            return
        else:
            response_body = str(response_body).encode('utf-8')

        self.end_headers()

        self.wfile.write(response_body)

    def __parse_multipart(self):
        content_type = self.headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            raise FlexibleServerException('Not a multipart/form-data request')

        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except ValueError:
            content_length = 0

        if content_length <= 0:
            return None, {}

        parser = StreamingFormDataParser(headers=self.headers)

        files = {}
        value_target = ValueTarget()
        parser.register('body', value_target)

        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.close()
        file_target = FileTarget(tmp_file.name)
        parser.register('file', file_target)
        files['file'] = tmp_file.name

        remaining = content_length
        chunk_size = 4096
        while remaining > 0:
            read_size = min(chunk_size, remaining)
            chunk = self.rfile.read(read_size)
            if not chunk:
                break
            parser.data_received(chunk)
            remaining -= len(chunk)

        body = value_target.value.decode() if value_target.value else None
        return body, files

    def _handle_request(self):
        """
        Process a single HTTP request lifecycle including routing, body handling,
        timeout management, and response dispatching

        This method is called automatically by the BaseHTTPRequestHandler's
        HTTP method handlers (do_GET, do_POST, etc.) and provides a flexible,
        dynamic routing mechanism supporting multiple HTTP verbs

        Steps performed:
          1. **Concurrency Control**
             - Uses a semaphore to limit the number of concurrent requests if configured

          2. **Routing**
             - Parses the request path and query parameters
             - Looks up the registered handler for the HTTP method and path

          3. **Request Body Handling**
             - Determines the request body length from the `Content-Length` header
             - If the handler declares a `body_file` parameter:
                 - Reads the request body in chunks from `self.rfile` to a temporary file
                 - Provides the path to this file to the handler
             - If the handler declares a `body` parameter:
                 - Reads the request body into memory and decodes it as UTF-8
                 - Provides the string to the handler
             - If the request is `multipart/form-data` (file uploads):
                 - Can parse fields and files efficiently
                 - Files are streamed to temporary files to avoid excessive memory usage
                 - Fields are collected in a dictionary for the handler
             - Only reads as much as specified by the `Content-Length` header

          4. **Timeout Handling**
             - If configured, executes the handler in a separate thread with a timeout
             - Returns a `504 Gateway Timeout` if the handler exceeds the allowed duration

          5. **Response Handling**
             - Calls the handler with the prepared parameters
             - Sends the returned status code and response body through `self.wfile`
             - Supports string, bytes, or iterable responses

          6. **Error Handling**
             - Catches exceptions raised by the handler or during request processing
             - Returns a `500 Internal Server Error` along with the traceback for debugging

          7. **Cleanup**
             - Releases the semaphore if used
             - Ensures temporary files are closed and can be deleted later by the caller

        Returns:
            None
            Sends the HTTP response directly through `self.wfile`
        """
        semaphore = getattr(self.server, 'request_semaphore', None)
        request_timeout = getattr(self.server, 'request_timeout', None)
        request_size_limit = getattr(self.server, 'request_size_limit', None)

        try:
            if semaphore and not semaphore.acquire(timeout=5):
                return self.__send_response(HTTPStatus.SERVICE_UNAVAILABLE, 'Server is busy')

            parsed_path = urlparse(self.path)
            path = parsed_path.path
            query_params = parse_qs(parsed_path.query)
            handler = self.server.routes.get((self.command, path))  # noqa

            if handler is None:
                return self.__send_response(HTTPStatus.NOT_FOUND, 'Not Found')
            if not callable(handler):
                return self.__send_response(HTTPStatus.BAD_REQUEST, 'Invalid handler')

            # Determine request length
            try:
                length = int(self.headers.get('Content-Length', 0))
            except ValueError:
                length = 0

            if request_size_limit is not None and length > request_size_limit:
                return self.__send_response(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, 'Request entity too large')

            content_type = self.headers.get('Content-Type', '')
            body = None
            if content_type.startswith('multipart/form-data'):
                body, files = self.__parse_multipart()
            else:
                if length > 0:
                    body_data = self.rfile.read(length)
                    body = body_data.decode('utf-8', errors='ignore')
                files = dict()

            if request_timeout is not None:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        handler,
                        request=self,
                        body=body,
                        files=files,
                        query=query_params
                    )
                    try:
                        response_body, status, handler_headers = future.result(timeout=request_timeout)
                    except TimeoutError:
                        return self.__send_response(HTTPStatus.GATEWAY_TIMEOUT, 'Request timed out')
            else:
                response_body, status, handler_headers = handler(
                    request=self,
                    body=body,
                    files=files,
                    query=query_params
                )

            return self.__send_response(status, response_body, handler_headers)

        except Exception as e:
            tb_str = traceback.format_exc()
            response_body = f'Internal Server Error:\n{str(e)}\n\nTraceback:\n{tb_str}'
            return self.__send_response(HTTPStatus.INTERNAL_SERVER_ERROR, response_body)

        finally:
            if semaphore:
                semaphore.release()

    # noinspection PyPep8Naming
    def do_GET(self):
        self._handle_request()

    # noinspection PyPep8Naming
    def do_POST(self):
        self._handle_request()

    # noinspection PyPep8Naming
    def do_PUT(self):
        self._handle_request()

    # noinspection PyPep8Naming
    def do_DELETE(self):
        self._handle_request()

    # noinspection PyPep8Naming
    def do_PATCH(self):
        self._handle_request()


class FlexibleServer:
    """ HTTP server with flexible routing and serve() method """

    def __init__(
            self,
            logger: logging.Logger = None,
            log: bool = True,
            request_size_limit: int = None,
            max_concurrent_requests: int = None,
            request_timeout: float = None,
            global_response_headers: dict[str, str] = None
    ):
        # FlexibleServer must be instantiated in the main thread due to Python’s signal handling limitations
        # Attempting to create it in a background thread will raise an exception
        if threading.current_thread() is not threading.main_thread():
            raise FlexibleServerException('FlexibleServer must be instantiated in the main thread!')

        ###############
        #   Logging   #
        ###############

        # _logger attribute is intended for internal use by the server's signal handlers !
        # It is protected rather than private to allow testing
        if log:
            if logger:
                self._logger = logger
            else:
                self._logger = NullLogger()
        else:
            self._logger = NullLogger()

        self._logger.propagate = False

        ###############
        #    HTTPD    #
        ###############

        self.__httpd = None

        # Thread-safe routes dictionary
        # Allows adding new routes at runtime while the server is actively serving requests
        self.__routes = {}
        self._routes_lock = threading.Lock()

        self.__request_size_limit = request_size_limit
        if self.__request_size_limit is not None:
            self._logger.warning(
                'Setting "request_size_limit" is intended for development or testing'
                'In production, it is recommended to enforce request size limits at the proxy or load balancer'
            )

        self.__max_concurrent_requests = max_concurrent_requests
        if self.__max_concurrent_requests is not None:
            self._logger.warning(
                'Setting "max_concurrent_requests" is intended for development or testing'
                'In production, it is recommended to enforce concurrent request limits at the proxy or load balancer'
            )

        self.__request_timeout = request_timeout
        if self.__request_timeout is not None:
            self._logger.warning(
                'Setting "request_timeout" is intended for development or testing'
                'In production, it is recommended to enforce request timeouts at the proxy or load balancer'
            )

        self.__global_response_headers = global_response_headers
        if self.__global_response_headers is not None:
            self._logger.warning(
                'Setting "global_response_headers" is intended for development or testing'
                'In production, it is recommended to configure headers like security headers (CSP, HSTS, etc.) at the proxy or load balancer'
            )

        ##############
        #   Server   #
        ##############

        self.__server_thread = None
        self.__running = None

        signal.signal(signal.SIGINT, self._handle_signal)  # noqa - (Ctrl+C from the terminal)
        signal.signal(signal.SIGTERM, self._handle_signal)  # noqa - (Standard termination signal used by systemd, kill PID)

    def _handle_signal(self, signum, frame=None):  # noqa
        """
        Handle OS signals (SIGINT, SIGTERM) to gracefully shut down the server
        This method is intended for internal use by the server's signal handlers !
        It is protected rather than private to allow testing
        """
        logging.info(f'\nReceived signal {signum} Shutting down gracefully ..')
        self.shutdown(10)

    def add_route(self, method: str, path: str, handler: Callable):
        """ Register a handler for a specific HTTP method and path """

        allowed_methods = {'GET', 'POST', 'PUT', 'PATCH', 'DELETE'}

        method = method.upper()
        if method not in allowed_methods:
            raise FlexibleServerException(f'Invalid HTTP method "{method}" - Allowed methods: {",".join(allowed_methods)}')

        with self._routes_lock:
            self.__routes[(method.upper(), path)] = handler

    def serve(
            self,
            host: str = 'localhost',
            port: int = 8001,
            cert_file: str = None,
            key_file: str = None,
            ca_file: str = None,
    ) -> None:
        """ Serve the FlexibleServer, supporting graceful shutdown on SIGINT/SIGTERM """
        if self.__httpd:
            raise FlexibleServerException(f'Server is already running! {host}:{port}')

        self.__httpd = ThreadingHTTPServer((host, port), _FlexibleHTTPRequestHandler)  # noqa

        # Propagation
        self.__httpd.logger = self._logger
        self.__httpd.routes = self.__routes
        self.__httpd.request_size_limit = self.__request_size_limit
        if self.__max_concurrent_requests is not None:
            # Semaphore is a synchronization primitive used in multithreaded programming to control access to a limited resource
            # It lets you limit how many threads can run a piece of code at the same time
            self.__httpd.request_semaphore = threading.Semaphore(self.__max_concurrent_requests)
        self.__httpd.request_timeout = self.__request_timeout
        self.__httpd.global_response_headers = self.__global_response_headers or dict()

        self.__running = True

        # HTTPS
        try:
            if cert_file and key_file:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
                context.load_cert_chain(certfile=cert_file, keyfile=key_file)
                if ca_file:
                    context.load_verify_locations(cafile=ca_file)
                self.__httpd.socket = context.wrap_socket(self.__httpd.socket, server_side=True)
                logging.info(f'HTTPS enabled on https://{host}:{port}')
            else:
                logging.info(f'Serving HTTP on http://{host}:{port}')
        except Exception as e:
            raise FlexibleServerException(f'Error configuring SSL: {e}')

        # Start serving in a background thread
        def serve_thread():
            try:
                self.__httpd.serve_forever()
            except Exception as e:  # noqa
                if self.__running:
                    raise FlexibleServerException(f'Error serving: {e}')
            finally:
                self.__httpd.server_close()

        self.__server_thread = threading.Thread(target=serve_thread, daemon=True)
        self.__server_thread.start()

        try:
            while self.__running:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info('\nKeyboard interrupt received')
            self.shutdown(10)

    def shutdown(self, graceful_timeout: int = 10) -> None:
        """ Gracefully stop the server with timeout """
        if not self.__httpd or not self.__running:
            return

        logging.info(f'Initiating graceful shutdown (timeout={graceful_timeout}s) ..')
        self.__running = False
        self.__httpd.shutdown()
        self.__server_thread.join(timeout=graceful_timeout)

    def is_running(self) -> bool:
        return bool(self.__running and self.__httpd)

    def generate_swagger(self, title='FlexibleServer API', version='1.0.0', target_file: Path = None):
        """ Generate Swagger/OpenAPI spec and render HTML page using Museflow elements """
        try:
            method_colors = {
                'GET': '#28a74575',  # Green
                'POST': '#007bff75',  # Blue
                'PUT': '#ffc10775',  # Yellow
                'DELETE': '#dc354575',  # Red
                'PATCH': '#17a2b875'  # Teal
            }

            content = []
            for (method, path), handler in self.__routes.items():
                route_card = div(
                    style=Style(
                        border='1px solid #ddd',
                        border_radius='8px',
                        padding='12px',
                        margin='8px 0',
                        background_color=method_colors.get(method.upper(), '#555'),
                        box_shadow='0 2px 5px rgba(0,0,0,0.05)',
                        transition='transform 0.2s',
                    ),
                ).adopt([
                    p(content=f'Path: {path}', style=Style(font_size='18px')),
                    p(content=f'Method: {method}', style=Style(font_size='18px')),
                    p(content=f'Handler: {handler.__name__}', style=Style(font_size='18px')),
                    p(content=handler.__doc__ or 'No description', style=Style(
                        white_space='pre-wrap',
                        background_color='#f6f8fa',
                        border_radius='4px',
                        border='1px solid #eee',
                        font_size='14px'
                    ))
                ])
                content.append(route_card)

            scrollable_container = div(
                style=Style(
                    max_height='70vh',
                    overflow_y='auto',
                    padding='8px'
                )
            ).adopt(content)

            root = html().adopt(
                div(style=Style(font_family='Arial, sans-serif', max_width='90%', margin='0 auto')).adopt([
                    h1(content=title, style=Style(text_align='center', margin_bottom='4px')),
                    h3(content=version, style=Style(text_align='center', margin_bottom='12px', color='#666')),
                    div(_id='swagger-ui').adopt([scrollable_container])
                ])
            )

            Museflow.render_file(root=root, target_file=target_file)
            logging.info(f'Swagger successfully generated at: {target_file}')
        except Exception as e:
            raise FlexibleServerException(f'Error generating Swagger: {e}')

    ################
    #    Cipher    #
    ################

    @staticmethod
    def generate_key(
            key_file: str = 'key.pem',
            key_size: int = 2048,
            public_exponent: int = 65537,
            password: str = None
    ) -> rsa.RSAPrivateKey:
        """
        Generate a private RSA key and save it to a file

        Args:
            key_file: Path to save the private key (PEM format)
            key_size: Size of the RSA key (default 2048)
            public_exponent: Public exponent of the RSA key
            password: Optional password to encrypt the key (str)

        Return: rsa.RSAPrivateKey object
        """
        try:
            private_key = rsa.generate_private_key(
                public_exponent=public_exponent,
                key_size=key_size
            )

            encryption_algo = serialization.NoEncryption()
            if password:
                encryption_algo = serialization.BestAvailableEncryption(password.encode())

            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=encryption_algo
            )

            with open(key_file, 'wb') as fd:
                fd.write(pem)

            return private_key
        except Exception as e:
            raise FlexibleServerException(f'Failed to generate private key: {e}')

    @staticmethod
    def generate_certificate(
            cert_file: str,
            key: rsa.RSAPrivateKey,
            common_name: str,
            country_code: str,
            organization: str = None,
            state: str = None,
            locality: str = None,
            expectancy: int = 365,
            self_signed: bool = True,
            issuer_cert: x509.Certificate = None,
            issuer_key: Any = None,
            san: Optional[list] = None
    ) -> x509.Certificate:
        try:
            subject_attrs = [
                x509.NameAttribute(NameOID.COUNTRY_NAME, country_code),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name)
            ]
            if organization:
                subject_attrs.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization))  # noqa
            if state:
                subject_attrs.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state))  # noqa
            if locality:
                subject_attrs.append(x509.NameAttribute(NameOID.LOCALITY_NAME, locality))  # noqa

            subject = x509.Name(subject_attrs)
            issuer = subject if self_signed else issuer_cert.subject

            builder = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.now(timezone.utc) - timedelta(minutes=1))
                .not_valid_after(datetime.now(timezone.utc) + timedelta(days=expectancy))
                .add_extension(x509.BasicConstraints(ca=False if not self_signed else True, path_length=None), critical=True)
            )

            san_names = san or [common_name]
            builder = builder.add_extension(SubjectAlternativeName([DNSName(n) for n in san_names]), critical=False)

            sign_key = key if self_signed else issuer_key
            cert = builder.sign(private_key=sign_key, algorithm=hashes.SHA256())

            with open(cert_file, 'wb') as fd:
                fd.write(cert.public_bytes(Encoding.PEM))

            return cert
        except Exception as e:
            raise FlexibleServerException(f'failed to create SSL certificate: {e}')

    @staticmethod
    @contextmanager
    def self_signed_ssl_context() -> dict:
        """
        Context manager that generates temporary self-signed SSL certificates for HTTPS testing

        This is useful for local development or test servers without needing pre-existing
        certificate/key files.

        The context yields a dictionary containing:
           - 'cert_file': Path to the temporary certificate file (PEM)
           - 'key_file': Path to the temporary private key file (PEM)
           - 'ca_file': Always None, no CA verification is performed

        Cleanup:
           Temporary files are automatically deleted when exiting the context.

        Yields:
           dict: Dictionary containing 'cert_file', 'key_file', and 'ca_file' paths.

        Raises:
           FlexibleServerException: If key/certificate generation fails.

        Usage:
           with FlexibleServer.self_signed_ssl_context() as ssl_data:
               cert_path = ssl_data['cert_file']
               key_path = ssl_data['key_file']
        """
        temp_dir = tempfile.TemporaryDirectory()
        try:
            cert_file = os.path.join(temp_dir.name, 'cert.pem')
            key_file = os.path.join(temp_dir.name, 'key.pem')

            key = FlexibleServer.generate_key(key_file)
            FlexibleServer.generate_certificate(
                cert_file=cert_file,
                key=key,
                common_name='localhost',
                country_code='NA',
                san=['localhost', '127.0.0.1']
            )

            yield {
                'cert_file': cert_file,
                'key_file': key_file,
                'ca_file': None
            }

        except Exception as e:
            raise FlexibleServerException(f'Failed to create SSL context: {e}')
        finally:
            temp_dir.cleanup()
