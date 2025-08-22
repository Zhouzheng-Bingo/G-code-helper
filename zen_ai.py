#!/usr/bin/env python3
"""
在项目中直接使用Zen AI模型
"""

import json
import requests
import os

class ZenAI:
    def __init__(self):
        # 加载配置
        config_path = os.path.join(os.path.dirname(__file__), 'zen_tools/custom_models.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.providers = {p['name']: p for p in config['providers']}
    
    def chat(self, prompt, model='gemini-2.5-flash'):
        """快速调用AI模型"""
        # 查找模型
        for provider in self.providers.values():
            for m in provider['models']:
                if m['id'] == model:
                    # 调用API
                    headers = {
                        'Authorization': f'Bearer {provider["api_key"]}',
                        'Content-Type': 'application/json'
                    }
                    data = {
                        'model': model,
                        'messages': [{'role': 'user', 'content': prompt}],
                        'temperature': 0.7
                    }
                    
                    response = requests.post(
                        f'{provider["api_url"]}/chat/completions',
                        headers=headers,
                        json=data,
                        timeout=60
                    )
                    
                    result = response.json()
                    if 'choices' in result:
                        return result['choices'][0]['message']['content']
                    else:
                        return f"错误: {result}"
        
        return f"未找到模型: {model}"
    
    def models(self):
        """列出所有可用模型"""
        print("可用的AI模型:")
        for provider in self.providers.values():
            print(f"\n{provider['name']}:")
            for model in provider['models']:
                print(f"  - {model['id']}: {model['description']}")

# 快捷函数
def ask_gemini(prompt):
    """快速问Gemini"""
    ai = ZenAI()
    return ai.chat(prompt, 'gemini-2.5-flash')

def ask_o3(prompt):
    """快速问O3"""
    ai = ZenAI()
    return ai.chat(prompt, 'o3-mini')

if __name__ == "__main__":
    # 测试
    ai = ZenAI()
    ai.models()
    print("\n测试Gemini:")
    print(ask_gemini("说一句鼓励的话"))