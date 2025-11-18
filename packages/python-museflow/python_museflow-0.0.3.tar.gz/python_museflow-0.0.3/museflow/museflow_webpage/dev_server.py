from pathlib import Path

from museflow_dev_server import MuseflowDevServer

MuseflowDevServer().serve(
    project_to_watch=Path(__file__).parent.resolve(),
    render_module_file=Path('component/home/home.py'),
    target_file=Path('../museflow.html'),
    port=8001,
    log=True,
    watch_interval=0.5
)
