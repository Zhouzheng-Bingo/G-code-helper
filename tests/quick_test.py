#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速性能测试 - 定位慢速原因
"""

import os
import time

# 设置环境变量
os.environ["PY_ENVIRONMENT"] = "local"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def test_llm_speed():
    """测试LLM响应速度"""
    print("="*60)
    print("测试1: LLM客户端响应速度")
    print("="*60)
    
    try:
        from lang_chain.client.client_factory import ClientFactory
        
        factory = ClientFactory()
        print(f"LLM_BASE_URL: {factory.client_url}")
        print(f"LLM_API_KEY: {factory.api_key[:10]}...")
        
        client = factory.get_client()
        
        # 测试简单查询
        start = time.time()
        response = client.chat_with_ai("回答我：1+1等于几？只需要回答数字")
        end = time.time()
        
        print(f"\n✅ LLM响应成功!")
        print(f"耗时: {end - start:.2f}秒")
        print(f"响应: {response}")
        
    except Exception as e:
        print(f"❌ LLM测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_intent_classification():
    """测试意图分类速度"""
    print("\n" + "="*60)
    print("测试2: 意图分类速度")
    print("="*60)
    
    try:
        # 直接测试LLM驱动的意图分类
        from lang_chain.client.client_factory import ClientFactory
        
        test_prompt = """请判断以下问题的类型，只回答数字：
1. 问候
2. G代码知识咨询  
3. 工艺任务执行
4. PDF文档查询
5. 未知

问题：G01是什么意思？

只需要回答对应的数字。"""
        
        client = ClientFactory().get_client()
        
        start = time.time()
        response = client.chat_with_ai(test_prompt)
        end = time.time()
        
        print(f"✅ 意图分类完成!")
        print(f"耗时: {end - start:.2f}秒")
        print(f"分类结果: {response}")
        
    except Exception as e:
        print(f"❌ 意图分类测试失败: {e}")
        import traceback
        traceback.print_exc()

def check_ollama_status():
    """检查Ollama服务状态"""
    print("\n" + "="*60)
    print("测试3: Ollama服务状态")
    print("="*60)
    
    try:
        import requests
        
        # 检查Ollama服务
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama服务正常运行")
            print(f"可用模型数量: {len(models)}")
            for model in models[:3]:  # 只显示前3个
                print(f"  - {model['name']}")
        else:
            print(f"⚠️ Ollama服务响应异常: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Ollama服务 (http://localhost:11434)")
        print("请确保Ollama正在运行: ollama serve")
    except Exception as e:
        print(f"❌ 检查Ollama失败: {e}")

def check_sleep_in_code():
    """检查代码中的sleep延迟"""
    print("\n" + "="*60)
    print("测试4: 检查人为延迟")
    print("="*60)
    
    files_to_check = [
        'qa/interaction.py',
        'qa/answer.py',
        'qa/question_parser.py'
    ]
    
    total_sleep_time = 0
    for file in files_to_check:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if 'time.sleep' in line:
                        # 尝试提取sleep时间
                        import re
                        match = re.search(r'time\.sleep\(([\d.]+)\)', line)
                        if match:
                            sleep_time = float(match.group(1))
                            total_sleep_time += sleep_time
                            print(f"  {file}:{i+1} - sleep({sleep_time}秒)")
        except Exception as e:
            print(f"  检查{file}失败: {e}")
    
    if total_sleep_time > 0:
        print(f"\n⚠️ 发现总计 {total_sleep_time:.2f}秒 的人为延迟!")
    else:
        print("\n✅ 未发现time.sleep延迟")

def main():
    print("🔬 快速性能诊断\n")
    
    # 1. 检查Ollama状态
    check_ollama_status()
    
    # 2. 测试LLM速度
    test_llm_speed()
    
    # 3. 测试意图分类
    test_intent_classification()
    
    # 4. 检查代码延迟
    check_sleep_in_code()
    
    print("\n" + "="*60)
    print("诊断完成!")

if __name__ == "__main__":
    main()