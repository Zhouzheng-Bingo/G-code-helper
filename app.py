
import threading

from api_backend import run_api
from utils.schedule import get_scheduler
from webui import run_webui

import os
# 设置环境变量
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def create_app():
    # 创建并启动API后端线程
    api_backend_thread = threading.Thread(target=run_api)
    api_backend_thread.start()

    get_scheduler().start()

    run_webui()


if __name__ == '__main__':
    create_app()
