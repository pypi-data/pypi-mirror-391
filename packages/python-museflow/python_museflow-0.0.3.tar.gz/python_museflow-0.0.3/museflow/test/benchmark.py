import multiprocessing
import time

import requests
import uvicorn  # noqa
from fastapi import FastAPI  # noqa
from flask import Flask  # noqa

from museflow.flexible_server import FlexibleServer, route_handler

#############
#   Flask   #
#############

flask_app = Flask(__name__)
flask_app.logger.disabled = True
flask_app.logger.propagate = False


@flask_app.route('/')
def flask_root():
    return 'Hello Flask'


def run_flask():
    flask_app.run(host='127.0.0.1', port=5000, use_reloader=False, debug=False)


################
#   Fast API   #
################

fastapi_app = FastAPI()


@fastapi_app.get('/')
def fastapi_root():
    return 'Hello FastAPI'


def run_fastapi():
    uvicorn.run(fastapi_app, host='127.0.0.1', port=5001)


#####################
#   Flexible Server #
#####################


@route_handler
def flexible_root():
    return 'Hello FlexibleServer', 200


flexible_server = FlexibleServer(log=False)
flexible_server.add_route('GET', '/', flexible_root)


def run_flexible():
    flexible_server.serve(host='127.0.0.1', port=5002)


def start_server(target):
    proc = multiprocessing.Process(target=target)
    proc.start()
    time.sleep(1)
    return proc


def benchmark(vendor: str, url: str, num_requests: int = 128):
    import time
    start = time.time()
    success = 0
    for _ in range(num_requests):
        # noinspection PyBroadException
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                success += 1
        except Exception:
            pass
    end = time.time()
    print(f'Vendor: {vendor} - {url}: {success}/{num_requests} Succeeded in {end - start:.2f}s')


if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', force=True)

    flask_proc = start_server(run_flask)
    fastapi_proc = start_server(run_fastapi)
    flexible_proc = start_server(run_flexible)

    try:
        benchmark('Flexible Server', 'http://127.0.0.1:5000/')
        benchmark('Fast API', 'http://127.0.0.1:5001/')
        benchmark('Flask', 'http://127.0.0.1:5002/')
    finally:
        for p in [flask_proc, fastapi_proc, flexible_proc]:
            p.terminate()
            p.join()

# - - - - - - - - - - - - - - - - - - - - - - - #
# Benchmark Nov 4 2025:
# - Flexible Server Version: Beta
# - Fast API Version: 0.121.0, Uvicorn Version: 0.38.0
# - Flask Version: 3.1.2, Werkzeug Version: 3.1.3
# - Pip Version: 23.2.1 (Python 3.12)

# [128 Requests]
# Vendor: Flexible Server - http://127.0.0.1:5000/: 128/128 Succeeded in 1.14s
# Vendor: Fast API - http://127.0.0.1:5001/: 128/128 Succeeded in 1.15s
# Vendor: Flask - http://127.0.0.1:5002/: 128/128 Succeeded in 0.95s

# [1024 Requests]
# Vendor: Flexible Server - http://127.0.0.1:5000/: 1024/1024 Succeeded in 8.35s
# Vendor: Fast API - http://127.0.0.1:5001/: 1024/1024 Succeeded in 8.33s
# Vendor: Flask - http://127.0.0.1:5002/: 1024/1024 Succeeded in 8.64s

# [1024 * 4 Requests]
# Vendor: Flexible Server - http://127.0.0.1:5000/: 4096/4096 Succeeded in 33.81s
# Vendor: Fast API - http://127.0.0.1:5001/: 4096/4096 Succeeded in 35.55s
# Vendor: Flask - http://127.0.0.1:5002/: 4096/4096 Succeeded in 31.17s

# [1024 * 8 Requests]
# Vendor: Flexible Server - http://127.0.0.1:5000/: 8192/8192 Succeeded in 63.14s
# Vendor: Fast API - http://127.0.0.1:5001/: 8192/8192 Succeeded in 66.60s
# Vendor: Flask - http://127.0.0.1:5002/: 8192/8192 Succeeded in 62.98s

# [1024 * 12 Requests]
# Vendor: Flexible Server - http://127.0.0.1:5000/: 12288/12288 Succeeded in 102.34s
# Vendor: Fast API - http://127.0.0.1:5001/: 12288/12288 Succeeded in 100.56s
# Vendor: Flask - http://127.0.0.1:5002/: 12288/12288 Succeeded in 95.75s

# - - - - - - - - - - - - - - - - - - - - - - - #
