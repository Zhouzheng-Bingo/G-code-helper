import os
from openai import OpenAI

# 设置环境变量
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"
os.environ["OPENAI_API_KEY"] = "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"

# 创建 OpenAI 客户端
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Say this is a test for me"}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")