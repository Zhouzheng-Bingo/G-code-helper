#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对比原版和优化版的性能
"""

import os
import time

# 设置环境变量
os.environ["PY_ENVIRONMENT"] = "local"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def test_original():
    """测试原版性能"""
    from qa.interaction import chat_with_gcode
    
    questions = [
        "你好",
        "G01是什么意思？",
    ]
    
    print("="*60)
    print("测试原版 chat_with_gcode")
    print("="*60)
    
    for q in questions:
        print(f"\n问题: {q}")
        start = time.time()
        response = ""
        for chunk in chat_with_gcode(q, []):
            response = chunk
        end = time.time()
        print(f"耗时: {end - start:.2f}秒")
        print(f"回答: {response[:100]}...")

def test_optimized():
    """测试优化版性能"""
    from qa.optimized_interaction import chat_with_gcode_optimized
    
    questions = [
        "你好",
        "G01是什么意思？",
    ]
    
    print("\n" + "="*60)
    print("测试优化版 chat_with_gcode_optimized")
    print("="*60)
    
    for q in questions:
        print(f"\n问题: {q}")
        start = time.time()
        response = ""
        for chunk in chat_with_gcode_optimized(q, []):
            response = chunk
        end = time.time()
        print(f"耗时: {end - start:.2f}秒")
        print(f"回答: {response[:100]}...")

def main():
    print("🔬 性能对比测试\n")
    
    # 先测试优化版（避免缓存影响）
    test_optimized()
    
    # 再测试原版
    test_original()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()