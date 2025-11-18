import asyncio
import importlib
import inspect
import logging
import sys
import threading
import time
from http import HTTPStatus
from pathlib import Path

import websockets

from museflow.element.inventory import script, head
from museflow.flexible_server import FlexibleServer, NullLogger, route_handler
from museflow.museflow import Museflow

LIVE_RELOAD_SCRIPT = '''
/* Museflow Live Reload */
if(!window._museflowReloader){
    window._museflowReloader=true;
    const ws=new WebSocket('ws://localhost:8765');
    ws.onmessage=(event)=>{if(event.data==='reload')window.location.reload();}
}
'''


class MuseflowDevServerException(Exception):
    def __init__(self, message: str):
        super().__init__(f'{self.__class__.__name__}: {message}')


class MuseflowDevServer:
    _instance = None
    _is_running = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __postprocess_html(self, target_file: Path):
        """ Inject live-reload script into generated HTML """
        if not target_file.exists():
            return

        try:
            html_text = target_file.read_text(encoding='utf-8')
            root = Museflow.interpret(html_text=html_text)

            head_tag = root.find_child_element(tag='head')
            if head_tag is None:
                root.inject(head.adopt(script(content=LIVE_RELOAD_SCRIPT)))
            else:
                head_tag.inject(script(content=LIVE_RELOAD_SCRIPT))

            target_file.write_text(Museflow.render(root), encoding='utf-8')

        except Exception as e:
            self.logger.warning(f'Postprocess failed: {e}')

    def __run_render_module_file(self, render_module_file: Path, target_file: Path):
        try:
            spec = importlib.util.spec_from_file_location('__caller__', render_module_file)  # noqa
            module = importlib.util.module_from_spec(spec)  # noqa
            sys.modules['__caller__'] = module
            spec.loader.exec_module(module)
            self.logger.info(f'Module executed: {render_module_file}')

            self.__postprocess_html(target_file)

        except Exception as e:
            self.logger.error(f'Render error: {e}', exc_info=True)

    async def __notify_reload(self):
        for ws in list(self._ws_clients):
            try:
                await ws.send('reload')
            except Exception:
                self._ws_clients.remove(ws)

    async def __ws_handler(self, websocket):
        self._ws_clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self._ws_clients.remove(websocket)

    def serve(
            self,
            render_module_file: Path,
            project_to_watch: Path,
            target_file: Path,
            port: int = 8001,
            log: bool = True,
            watch_interval: float = 0.5,
    ):
        if self._is_running:
            return
        self._is_running = True

        # Logger setup
        self.logger = logging.getLogger('Museflow Dev Server') if log else NullLogger()
        if log and not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        self._ws_clients = set()
        self._ws_loop = asyncio.new_event_loop()

        def start_ws():
            asyncio.set_event_loop(self._ws_loop)

            async def runner():
                async with websockets.serve(self.__ws_handler, 'localhost', 8765):
                    self.logger.info('Live Reload WebSocket listening on ws://localhost:8765')
                    await asyncio.Future()

            self._ws_loop.run_until_complete(runner())

        threading.Thread(target=start_ws, daemon=True).start()

        render_module_file = Path(render_module_file).resolve()
        project_to_watch = Path(project_to_watch).resolve()
        target_file = Path(target_file).resolve()
        caller_file = Path(inspect.stack()[1].filename).resolve()

        # Prevent recursion if the render module calls serve()
        if caller_file == render_module_file:
            raise MuseflowDevServerException('Development server must not be started inside the render module !')

        all_py_files = [f.resolve() for f in project_to_watch.rglob('*.py') if f.resolve() != caller_file]
        file_mtimes = {f: f.stat().st_mtime for f in all_py_files if f.exists()}

        self.logger.info(f'Render module: {render_module_file}')
        self.logger.info(f'Watching files: {len(all_py_files)} Python files')

        # Initial render
        self.__run_render_module_file(render_module_file, target_file)

        stop_flag = threading.Event()

        def watcher():
            while not stop_flag.is_set():
                changed = False
                for f in all_py_files:
                    if f.exists():
                        mtime = f.stat().st_mtime
                        if file_mtimes.get(f) != mtime:
                            file_mtimes[f] = mtime
                            changed = True

                if changed:
                    self.logger.info('Detected change, reloading modules...')
                    for name, mod in list(sys.modules.items()):
                        if mod is None:
                            continue
                        mod_file = getattr(mod, '__file__', None)
                        if mod_file and Path(mod_file).resolve().is_relative_to(project_to_watch):
                            try:
                                importlib.reload(mod)
                            except Exception as e:
                                self.logger.warning(f'Could not reload {name}: {e}')

                    self.__run_render_module_file(render_module_file, target_file)
                    asyncio.run_coroutine_threadsafe(self.__notify_reload(), self._ws_loop)

                time.sleep(watch_interval)

        threading.Thread(target=watcher, daemon=True).start()

        server = FlexibleServer(logger=self.logger, log=log)

        @route_handler
        def serve_html():
            try:
                return target_file.read_text(encoding='utf-8'), HTTPStatus.OK, {'Content-Type': 'text/html'}
            except Exception as e:
                return f'Error reading HTML: {e}', HTTPStatus.INTERNAL_SERVER_ERROR, {}

        server.add_route('GET', f'/{target_file.name}', serve_html)
        self.logger.info(f'Serving on http://localhost:{port}/{target_file.name}')

        try:
            server.serve(host='localhost', port=port)
        finally:
            stop_flag.set()
