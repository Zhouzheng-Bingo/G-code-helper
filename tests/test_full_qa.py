#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试完整问答流程的耗时
"""

import os
import time

# 设置环境变量
os.environ["PY_ENVIRONMENT"] = "local"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def test_full_qa():
    """测试完整问答流程"""
    print("测试完整问答流程")
    print("="*60)
    
    from qa.interaction import chat_with_gcode
    
    test_questions = [
        "G01是什么意思？",
        "你好",
        "帮我做一个外圆加工"
    ]
    
    for question in test_questions:
        print(f"\n问题: {question}")
        print("-"*40)
        
        start_time = time.time()
        response = ""
        chunk_count = 0
        first_chunk_time = None
        
        # 收集所有响应块
        for chunk in chat_with_gcode(question, []):
            if first_chunk_time is None:
                first_chunk_time = time.time() - start_time
                print(f"首个响应块时间: {first_chunk_time:.2f}秒")
            response = chunk
            chunk_count += 1
        
        total_time = time.time() - start_time
        
        print(f"总耗时: {total_time:.2f}秒")
        print(f"响应块数: {chunk_count}")
        print(f"响应内容: {response[:100]}...")
        
        # 计算延迟影响
        sleep_delay = chunk_count * 0.05  # 每个块0.05秒延迟
        actual_time = total_time - sleep_delay
        print(f"去除sleep延迟后: {actual_time:.2f}秒")

if __name__ == "__main__":
    test_full_qa()