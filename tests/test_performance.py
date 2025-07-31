#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
性能测试脚本 - 找出真正的性能瓶颈
"""

import os
import time
import traceback
from functools import wraps

# 设置环境变量
os.environ["PY_ENVIRONMENT"] = "local"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 性能计时装饰器
def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"⏱️  {func.__name__} 耗时: {end - start:.2f}秒")
        return result
    return wrapper

@time_it
def test_import_time():
    """测试各模块导入时间"""
    print("\n📦 测试模块导入时间...")
    
    start = time.time()
    from qa.interaction import chat_with_gcode
    print(f"  - qa.interaction 导入耗时: {time.time() - start:.2f}秒")
    
    start = time.time()
    from model.preload_manager import get_preload_manager
    print(f"  - model.preload_manager 导入耗时: {time.time() - start:.2f}秒")
    
    start = time.time()
    from lang_chain.client.client_factory import ClientFactory
    print(f"  - lang_chain.client 导入耗时: {time.time() - start:.2f}秒")

@time_it
def test_preload():
    """测试预加载性能"""
    print("\n🚀 测试预加载...")
    from model.preload_manager import get_preload_manager
    manager = get_preload_manager()
    manager.preload_all_models()

@time_it
def test_llm_client():
    """测试LLM客户端连接"""
    print("\n🤖 测试LLM客户端...")
    try:
        from lang_chain.client.client_factory import ClientFactory
        factory = ClientFactory()
        client = factory.get_client()
        
        # 测试简单查询
        start = time.time()
        response = client.chat_with_ai("你好")
        print(f"  - LLM响应耗时: {time.time() - start:.2f}秒")
        print(f"  - 响应内容: {response[:50]}...")
    except Exception as e:
        print(f"  ❌ LLM客户端测试失败: {e}")

@time_it
def test_intent_classification():
    """测试意图分类性能"""
    print("\n🎯 测试意图分类...")
    try:
        from qa.question_parser import parse_question
        
        test_questions = [
            "G01是什么意思？",
            "外圆加工怎么做？",
            "帮我生成一个车削程序"
        ]
        
        for q in test_questions:
            start = time.time()
            result = parse_question(q)
            print(f"  - '{q}' 分类耗时: {time.time() - start:.2f}秒, 结果: {result}")
    except Exception as e:
        print(f"  ❌ 意图分类测试失败: {e}")
        traceback.print_exc()

@time_it
def test_entity_search():
    """测试实体搜索性能"""
    print("\n🔍 测试实体搜索...")
    try:
        from model.graph_entity.search_service import search
        
        start = time.time()
        code, msg, results = search("G01")
        print(f"  - 实体搜索耗时: {time.time() - start:.2f}秒")
        print(f"  - 搜索结果: code={code}, msg={msg}, results数量={len(results) if results else 0}")
    except Exception as e:
        print(f"  ❌ 实体搜索测试失败: {e}")

@time_it
def test_rag_retrieval():
    """测试RAG检索性能"""
    print("\n📚 测试RAG检索...")
    try:
        from model.rag.retriever_service import retriever_search
        
        start = time.time()
        docs = retriever_search("G代码")
        print(f"  - RAG检索耗时: {time.time() - start:.2f}秒")
        print(f"  - 检索到文档数: {len(docs) if docs else 0}")
    except Exception as e:
        print(f"  ❌ RAG检索测试失败: {e}")

@time_it
def test_full_qa_flow():
    """测试完整问答流程"""
    print("\n💬 测试完整问答流程...")
    try:
        from qa.interaction import chat_with_gcode
        
        test_message = "G01是什么意思？"
        print(f"  测试问题: {test_message}")
        
        # 测试流式响应
        start = time.time()
        response = ""
        chunk_count = 0
        first_chunk_time = None
        
        for chunk in chat_with_gcode(test_message, []):
            if first_chunk_time is None:
                first_chunk_time = time.time() - start
            response = chunk
            chunk_count += 1
        
        total_time = time.time() - start
        
        print(f"  - 首个响应块耗时: {first_chunk_time:.2f}秒")
        print(f"  - 总耗时: {total_time:.2f}秒")
        print(f"  - 响应块数量: {chunk_count}")
        print(f"  - 响应内容: {response[:100]}...")
    except Exception as e:
        print(f"  ❌ 完整问答测试失败: {e}")
        traceback.print_exc()

@time_it
def test_sleep_delays():
    """检查代码中的sleep延迟"""
    print("\n😴 检查sleep延迟...")
    
    # 检查interaction.py中的sleep
    try:
        with open('qa/interaction.py', 'r', encoding='utf-8') as f:
            content = f.read()
            sleep_count = content.count('time.sleep')
            print(f"  - qa/interaction.py 中发现 {sleep_count} 处 time.sleep")
            
            # 找出具体的sleep语句
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'time.sleep' in line:
                    print(f"    第{i+1}行: {line.strip()}")
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")

def main():
    """主测试函数"""
    print("="*60)
    print("🔬 G-Code Helper 性能诊断")
    print("="*60)
    
    # 1. 测试导入时间
    test_import_time()
    
    # 2. 测试预加载
    test_preload()
    
    # 3. 测试各个组件
    test_llm_client()
    test_intent_classification()
    test_entity_search()
    test_rag_retrieval()
    
    # 4. 测试完整流程
    test_full_qa_flow()
    
    # 5. 检查sleep延迟
    test_sleep_delays()
    
    print("\n" + "="*60)
    print("📊 性能诊断完成")
    print("="*60)

if __name__ == "__main__":
    main()