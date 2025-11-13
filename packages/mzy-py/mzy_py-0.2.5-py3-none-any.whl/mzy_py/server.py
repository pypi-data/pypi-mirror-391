import os
import threading
import time
from flask import Flask, send_from_directory

__all__ = ["run_html_server"]

def run_html_server(*, html_file: str = "index.html",
                    port: int = 5000,
                    host: str = "127.0.0.1",
                    debug: bool = False,
                    ready_timeout: float = 5) -> None:
    """
    一键启动静态 HTML 文件微型服务器。

    参数
    ----
    html_file : str
        要托管的 HTML 文件名（可含相对路径）。
    port : int
        监听端口。
    host : str
        监听地址，0.0.0.0 允许局域网访问。
    debug : bool
        是否开启 Flask debug 模式。
    ready_timeout : float
        等待服务器启动的最大秒数，超时抛 RuntimeError。
    """
    if not os.path.isfile(html_file):
        raise FileNotFoundError(html_file)

    folder = os.path.dirname(html_file) or "."
    fname  = os.path.basename(html_file)
    app = Flask(__name__)

    @app.route("/")
    def index():
        return send_from_directory(folder, fname)

    def _run():
        app.run(host=host, port=port, debug=debug, use_reloader=False)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    # 简单等待服务器就绪
    url = f"http://{host}:{port}"
    start = time.time()
    while time.time() - start < ready_timeout:
        try:
            # 探测是否已能建立 TCP 连接
            import socket
            with socket.create_connection((host, port), timeout=0.5):
                break
        except (OSError, ConnectionRefusedError):
            time.sleep(0.2)
    else:
        raise RuntimeError(f"Server failed to start on {url}")

    print(f"HTML server is running at {url}")
    print("Press Ctrl+C to stop (notebook 请中断 kernel).")
    try:
        thread.join()          # 阻塞主线程，用户 Ctrl+C 即可退出
    except KeyboardInterrupt:
        print("\nServer shutdown.")