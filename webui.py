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

# 1.不准确 Pocketsphinx
# def audio_to_text(audio_path):
#     model_path = "D:/Anaconda/download/envs/gcode/Lib/site-packages/speech_recognition/pocketsphinx-data/zh-CN/zh_cn.cd_cont_5000"
#
#     ps = Pocketsphinx(
#         hmm=model_path,
#         lm="D:/Anaconda/download/envs/gcode/Lib/site-packages/speech_recognition/pocketsphinx-data/zh-CN/zh_cn.lm.bin",
#         dic="D:/Anaconda/download/envs/gcode/Lib/site-packages/speech_recognition/pocketsphinx-data/zh-CN/zh_cn.dic"
#     )
#
#     ps.decode(audio_file=audio_path)
#     return ps.hypothesis()
# 2.很慢
# def audio_to_text(audio_path):
#     model = whisper.load_model("large")  # 可选：tiny, base, small, medium, large，越来越慢
#     result = model.transcribe(audio_path)
#     return result["text"]
def audio_to_text(audio_path):
    # 可选：tiny, base, small, medium, large
    # model = whisper.load_model("medium")
    # result = model.transcribe(audio_path)
    # return result["text"]
    
    # 始终返回固定文本
    # 这里演示用的，做硬编码的
    # return "我要使用外圆工艺加工一个外圆，Cn是2，L是100，Tr是0.5，Cr是1，F是300"
    return "我要使用外圆工艺加工一个外圆，每次进刀量0.5毫米，总共进两刀，进刀量总共是一毫米，加工长度是100毫米，加工速度是300毫米每分"


# 清空音频输入
def reset_audio_input():
    return None

# 包裹 chat_with_gcode 的固定输入版本
def fixed_input_wrapper(user_input, history):
    fixed_input = "我要使用外圆工艺加工一个外圆，Cn是2，L是100，Tr是0.5，Cr是1，F是300"
    # 逐步生成结果
    for partial_result in chat_with_gcode(fixed_input, history):
        yield partial_result

def run_webui():
    with gr.Blocks() as demo:
        with gr.Row():  # 横向布局
            audio_input = gr.Audio(source="microphone", type="filepath", label="语音输入", scale=1)
            reset_button = gr.Button("重新输入", scale=0)  # 添加按钮

        chat_app = gr.ChatInterface(
            # chat_with_gcode,
            fixed_input_wrapper,
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
