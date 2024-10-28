import os

import gradio as gr

from config.config import Config
from env import get_app_root
from qa.interaction import chat_with_gcode

__AVATAR = (
    os.path.join(get_app_root(), "resource/avatar/user.png"),
    os.path.join(get_app_root(), "resource/avatar/gcode_assistant.png")
)

def run_webui():
    chat_app = gr.ChatInterface(
        chat_with_gcode,
        chatbot=gr.Chatbot(height=400, avatar_images=__AVATAR),
        textbox=gr.Textbox(placeholder="请输入你的问题", container=False, scale=7),
        title="G代码编程助手📒",
        description="您可以咨询关于GJ306数控系统和G代码编程的问题",
        theme="default",
        examples=[
            "您好",
            "G00指令的作用是什么？",
            "如何使用G76螺纹切削循环？",
            "G代码中的G71和G72有什么区别？",
            "请提供GJ306系统的参考手册",
            "如何设置刀具补偿？",
            "M代码和G代码有什么区别？",
            "如何编写子程序？",
            "请生成一个简单的车削程序示例",
            "如何在GJ306系统中进行坐标系设定？"
        ],
        cache_examples=False,
        retry_btn=None,
        submit_btn="发送",
        stop_btn="停止",
        undo_btn="删除当前",
        clear_btn="清除所有",
        concurrency_limit=4,
    )

    chat_app.launch(
        server_name="0.0.0.0",
        server_port=int(Config.get_instance().get_with_nested_params("server", "ui_port")),
        share=Config.get_instance().get_with_nested_params("server", "ui_share"),
        max_threads=10
    )

if __name__ == "__main__":
    run_webui()
