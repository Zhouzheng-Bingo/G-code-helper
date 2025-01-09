
import threading

from api_backend import run_api
from utils.schedule import get_scheduler
from webui import run_webui

import os
# 设置环境变量
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

"""如果遇到FileNotFoundError: [Errno 2] No such file or directory: '...\\ # 启用本地开发环境.yaml'问题，
运行以下命令清除遗留的 PY_ENVIRONMENT 系统环境变量：
Remove-Item Env:PY_ENVIRONMENT
然后运行以下命令确认清理成功：
Get-ChildItem Env:PY_ENVIRONMENT
如果没有输出，说明清理成功。
"""

def create_app():
    # 创建并启动API后端线程
    api_backend_thread = threading.Thread(target=run_api)
    api_backend_thread.start()

    get_scheduler().start()

    run_webui()


if __name__ == '__main__':
    create_app()
