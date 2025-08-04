#!/usr/bin/env python3
"""
Zen AI - 简化的多模型AI接口
提供对O3和Gemini模型的直接访问
"""

import json
import requests
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

class ZenAI:
    def __init__(self):
        self.config_path = Path(__file__).parent / "zen_tools" / "custom_models.json"
        self.providers = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载模型配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {p['name']: p for p in config['providers']}
        except Exception as e:
            print(f"❌ 配置加载失败: {e}")
            return {}
    
    def models(self) -> List[str]:
        """列出所有可用模型"""
        available_models = []
        for provider_name, provider in self.providers.items():
            for model in provider['models']:
                available_models.append(model['id'])
                print(f"🤖 {model['id']} - {model['name']}")
                print(f"   📝 {model['description']}")
                print(f"   🔢 上下文: {model['context_window']:,} tokens")
                print()
        return available_models
    
    def _find_model_provider(self, model_id: str) -> Optional[Dict[str, Any]]:
        """查找模型对应的提供商"""
        for provider in self.providers.values():
            for model in provider['models']:
                if model['id'] == model_id:
                    return provider
        return None
    
    def chat(self, prompt: str, model: str = 'gemini-2.5-flash') -> str:
        """与指定模型对话"""
        provider = self._find_model_provider(model)
        if not provider:
            return f"❌ 模型 {model} 不可用"
        
        try:
            headers = {
                'Authorization': f"Bearer {provider['api_key']}",
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': model,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 4000,
                'temperature': 0.7
            }
            
            response = requests.post(
                f"{provider['api_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"❌ API调用失败: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ 请求失败: {str(e)}"

# 便捷函数
def ask_gemini(prompt: str, model: str = 'gemini-2.5-flash') -> str:
    """使用Gemini模型快速问答"""
    ai = ZenAI()
    return ai.chat(prompt, model)

def ask_o3(prompt: str, model: str = 'o3-mini') -> str:
    """使用O3模型进行推理"""
    ai = ZenAI()
    return ai.chat(prompt, model)

def list_models() -> List[str]:
    """列出可用模型"""
    ai = ZenAI()
    return ai.models()

# 主程序 - 显示可用模型
if __name__ == "__main__":
    print("🚀 Zen AI 模型系统")
    print("=" * 50)
    
    ai = ZenAI()
    if not ai.providers:
        print("❌ 没有找到可用的模型配置")
        print("   请确保 zen_tools/custom_models.json 文件存在")
        exit(1)
    
    print("📋 可用模型:")
    models = ai.models()
    
    print(f"✅ 共找到 {len(models)} 个模型")
    print("\n💡 使用示例:")
    print("from zen_ai import ask_gemini, ask_o3")
    print("answer = ask_gemini('什么是机器学习?')")
    print("solution = ask_o3('设计一个排序算法')")
