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

def format_message_with_copy_buttons(message):
    """
    为消息中的代码块添加复制按钮
    """
    import re
    
    # 检测G代码块（通常以G、M、N开头的行）
    gcode_pattern = r'```(?:gcode|G代码)?\n((?:[GMN]\d+[^\n]*\n?)+)```'
    
    def add_copy_button(match):
        code = match.group(1).strip()
        # 生成唯一ID
        import hashlib
        code_id = hashlib.md5(code.encode()).hexdigest()[:8]
        
        return f'''
<div class="code-block-container">
    <div class="code-header">
        <span class="code-label">G代码</span>
        <button class="copy-btn" onclick="copyToClipboard('code_{code_id}')">📋 复制</button>
    </div>
    <pre class="code-content" id="code_{code_id}">{code}</pre>
</div>
'''
    
    # 替换G代码块
    formatted_message = re.sub(gcode_pattern, add_copy_button, message, flags=re.MULTILINE)
    
    # 检测普通代码块
    general_code_pattern = r'```(\w+)?\n(.*?)```'
    
    def add_general_copy_button(match):
        lang = match.group(1) or '代码'
        code = match.group(2).strip()
        import hashlib
        code_id = hashlib.md5(code.encode()).hexdigest()[:8]
        
        return f'''
<div class="code-block-container">
    <div class="code-header">
        <span class="code-label">{lang}</span>
        <button class="copy-btn" onclick="copyToClipboard('code_{code_id}')">📋 复制</button>
    </div>
    <pre class="code-content" id="code_{code_id}">{code}</pre>
</div>
'''
    
    # 替换普通代码块
    formatted_message = re.sub(general_code_pattern, add_general_copy_button, formatted_message, flags=re.DOTALL)
    
    return formatted_message

def enhanced_chat_with_gcode(message, history):
    """增强的聊天函数，支持复制功能"""
    # 调用原始的聊天函数
    response_generator = chat_with_gcode(message, history)
    
    # 处理流式响应
    for partial_response in response_generator:
        # 为响应添加复制按钮
        formatted_response = format_message_with_copy_buttons(partial_response)
        yield formatted_response

# 自定义CSS样式
custom_css = """
<style>
.code-block-container {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    margin: 10px 0;
    overflow: hidden;
}

.code-header {
    background-color: #343a40;
    color: white;
    padding: 8px 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
}

.code-label {
    font-weight: bold;
}

.copy-btn {
    background-color: #6c757d;
    color: white;
    border: none;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    transition: background-color 0.2s;
}

.copy-btn:hover {
    background-color: #5a6268;
}

.copy-btn:active {
    background-color: #495057;
}

.copy-btn.copied {
    background-color: #28a745;
}

.code-content {
    background-color: #f8f9fa;
    padding: 12px;
    margin: 0;
    white-space: pre-wrap;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.4;
    overflow-x: auto;
}

/* 选中文本样式 */
::selection {
    background-color: #007bff;
    color: white;
}

/* 确保聊天区域可以选择文本 */
.message-wrap {
    user-select: text !important;
    -webkit-user-select: text !important;
    -moz-user-select: text !important;
    -ms-user-select: text !important;
}

/* 聊天消息样式优化 */
.bot-message, .user-message {
    user-select: text !important;
    -webkit-user-select: text !important;
}
</style>

<script>
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const text = element.textContent || element.innerText;
    
    // 使用现代的 Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function() {
            showCopySuccess(elementId);
        }).catch(function(err) {
            console.log('复制失败:', err);
            fallbackCopy(text, elementId);
        });
    } else {
        // 回退方案
        fallbackCopy(text, elementId);
    }
}

function fallbackCopy(text, elementId) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopySuccess(elementId);
        } else {
            console.log('复制失败');
        }
    } catch (err) {
        console.log('复制失败:', err);
    }
    
    document.body.removeChild(textArea);
}

function showCopySuccess(elementId) {
    const button = document.querySelector(`#${elementId}`).parentElement.querySelector('.copy-btn');
    if (button) {
        const originalText = button.textContent;
        button.textContent = '✅ 已复制';
        button.classList.add('copied');
        
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('copied');
        }, 2000);
    }
}
</script>
"""

def run_enhanced_webui():
    with gr.Blocks(css=custom_css, title="G代码编程助手") as demo:
        # 添加自定义CSS和JavaScript
        gr.HTML(custom_css)
        
        with gr.Row():  # 横向布局
            audio_input = gr.Audio(source="microphone", type="filepath", label="语音输入", scale=1)
            reset_button = gr.Button("重新输入", scale=0)

        # 使用自定义的ChatInterface替代方案
        with gr.Column():
            gr.Markdown("# G代码编程助手📒")
            gr.Markdown("您可以咨询关于GJ306数控系统和G代码编程的问题。代码块支持一键复制功能。")
            
            chatbot = gr.Chatbot(
                value=[],
                label="聊天记录",
                height=500,
                show_copy_button=True,  # 启用Gradio内置的复制按钮
                avatar_images=__AVATAR,
                bubble_full_width=False,
                render_markdown=True
            )
            
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="输入您的问题...",
                    label="消息输入",
                    scale=4,
                    max_lines=3
                )
                submit_btn = gr.Button("发送", scale=1, variant="primary")
            
            # 示例问题
            gr.Examples(
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
                inputs=msg_input
            )

        def respond(message, chat_history):
            """处理用户消息并更新聊天记录"""
            if not message.strip():
                return chat_history, ""
            
            # 添加用户消息到历史记录
            chat_history = chat_history + [[message, None]]
            
            # 获取AI响应
            response_generator = chat_with_gcode(message, chat_history[:-1])
            
            # 处理流式响应
            for partial_response in response_generator:
                # 格式化响应以包含复制按钮
                formatted_response = format_message_with_copy_buttons(partial_response)
                chat_history[-1][1] = formatted_response
                yield chat_history, ""
            
            return chat_history, ""

        # 绑定事件
        submit_btn.click(
            fn=respond,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input],
            show_progress=True
        )
        
        msg_input.submit(
            fn=respond,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input],
            show_progress=True
        )

        # 绑定语音输入
        audio_input.change(
            fn=audio_to_text,
            inputs=audio_input,
            outputs=msg_input
        )

        # 绑定"重新输入"按钮
        reset_button.click(
            fn=reset_audio_input,
            inputs=[],
            outputs=audio_input
        )

    # 启动应用
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=int(Config.get_instance().get_with_nested_params("server", "ui_port")),
        share=Config.get_instance().get_with_nested_params("server", "ui_share"),
        max_threads=10
    )

if __name__ == "__main__":
    run_enhanced_webui()