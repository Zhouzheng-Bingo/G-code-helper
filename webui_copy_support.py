import os
import gradio as gr
import whisper
import tempfile
import numpy as np
import soundfile as sf
import json
import shutil
from config.config import Config
from env import get_app_root
from qa.interaction import chat_with_gcode

__AVATAR = (
    os.path.join(get_app_root(), "resource/avatar/user.png"),
    os.path.join(get_app_root(), "resource/avatar/gcode_assistant.png")
)

def audio_to_text(audio_path):
    # 可选：tiny, base, small, medium, large
    model = whisper.load_model("tiny")
    result = model.transcribe(audio_path)
    return result["text"]

# 清空音频输入
def reset_audio_input():
    return None

def run_webui():
    # 自定义CSS来支持文本选择和复制
    custom_css = """
    /* 确保所有文本都可以选择 */
    .message, .message * {
        user-select: text !important;
        -webkit-user-select: text !important;
        -moz-user-select: text !important;
        -ms-user-select: text !important;
    }
    
    /* 代码块样式优化 */
    pre, code {
        user-select: text !important;
        -webkit-user-select: text !important;
        background-color: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
        border-radius: 4px !important;
        padding: 8px !important;
        font-family: 'Courier New', monospace !important;
        position: relative;
    }
    
    /* 选中文本高亮 */
    ::selection {
        background-color: #007bff !important;
        color: white !important;
    }
    
    ::-moz-selection {
        background-color: #007bff !important;
        color: white !important;
    }
    
    /* 聊天气泡样式 */
    .message-wrap {
        user-select: text !important;
        -webkit-user-select: text !important;
    }
    
    /* 确保整个聊天区域可选择 */
    .chatbot {
        user-select: text !important;
        -webkit-user-select: text !important;
    }
    
    /* 禁用某些不必要的样式覆盖 */
    .chatbot .message {
        pointer-events: auto !important;
        user-select: text !important;
    }
    """
    
    with gr.Blocks(css=custom_css, title="G代码编程助手") as demo:
        with gr.Row():  # 横向布局
            audio_input = gr.Audio(source="microphone", type="filepath", label="语音输入", scale=1)
            reset_button = gr.Button("重新输入", scale=0)  # 添加按钮

        chat_app = gr.ChatInterface(
            chat_with_gcode,
            title="G代码编程助手📒",
            description="您可以咨询关于GJ306数控系统和G代码编程的问题。**提示：所有文本内容都支持选择和复制**",
            theme="default",
            show_copy_button=True,  # 启用内置复制按钮
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
                "如何在GJ306系统中进行坐标系设定？",
                "我要使用外圆工艺加工一个外圆，每次进刀量0.5毫米，总共进两刀，进刀量总共是一毫米，加工长度是100毫米，加工速度是300毫米每分"
            ],
            cache_examples=False
        )

        # 绑定语音输入到 G 代码助手
        audio_input.change(
            fn=audio_to_text,
            inputs=audio_input,
            outputs=chat_app.textbox
        )

        # 绑定"重新输入"按钮，点击后清空 audio_input
        reset_button.click(
            fn=reset_audio_input,
            inputs=[],
            outputs=audio_input
        )

    # 正确的位置，.queue() 应放在 demo 上
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=int(Config.get_instance().get_with_nested_params("server", "ui_port")),
        share=Config.get_instance().get_with_nested_params("server", "ui_share"),
        max_threads=10
    )


if __name__ == "__main__":
    run_webui()