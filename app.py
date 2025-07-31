import threading
import os

# 设置环境变量
os.environ["PY_ENVIRONMENT"] = "local"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from api_backend import run_api
from utils.schedule import get_scheduler
from webui import run_webui
from model.preload_manager import get_preload_manager
from loguru import logger

import matplotlib
matplotlib.use('Agg')

"""如果遇到FileNotFoundError: [Errno 2] No such file or directory: '...\\ # 启用本地开发环境.yaml'问题，
运行以下命令清除遗留的 PY_ENVIRONMENT 系统环境变量：
Remove-Item Env:PY_ENVIRONMENT
然后运行以下命令确认清理成功：
Get-ChildItem Env:PY_ENVIRONMENT
如果没有输出，说明清理成功。
"""

def create_app():
    # 预加载所有模型
    logger.info("🚀 正在预加载模型，请稍候...")
    preload_manager = get_preload_manager()
    preload_manager.preload_all_models()
    logger.info("✅ 模型预加载完成，启动应用服务...")
    
    # 创建并启动API后端线程
    api_backend_thread = threading.Thread(target=run_api)
    api_backend_thread.start()

    get_scheduler().start()

    # 启动WebUI（已增强支持文本复制功能）
    logger.info("🎨 启动WebUI（支持文本复制功能）...")
    run_webui()


if __name__ == '__main__':
    create_app()
