#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试预加载效果的脚本
"""

import os
import time
import sys

# 设置环境变量
os.environ["PY_ENVIRONMENT"] = "local"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def test_without_preload():
    """测试不使用预加载的情况"""
    print("\n" + "="*60)
    print("测试1: 不使用预加载")
    print("="*60)
    
    start_time = time.time()
    
    # 模拟一次问答
    from qa.interaction import chat_with_gcode
    
    test_message = "G01是什么意思？"
    print(f"测试问题: {test_message}")
    
    response_start = time.time()
    response = ""
    for chunk in chat_with_gcode(test_message, []):
        response = chunk
    
    response_time = time.time() - response_start
    total_time = time.time() - start_time
    
    print(f"响应: {response[:100]}...")
    print(f"响应时间: {response_time:.2f}秒")
    print(f"总耗时（含导入）: {total_time:.2f}秒")
    
    return response_time, total_time

def test_with_preload():
    """测试使用预加载的情况"""
    print("\n" + "="*60)
    print("测试2: 使用预加载")
    print("="*60)
    
    # 预加载
    preload_start = time.time()
    from model.preload_manager import get_preload_manager
    preload_manager = get_preload_manager()
    preload_manager.preload_all_models()
    preload_time = time.time() - preload_start
    print(f"预加载耗时: {preload_time:.2f}秒")
    
    # 再次测试问答
    from qa.interaction import chat_with_gcode
    
    test_message = "G01是什么意思？"
    print(f"测试问题: {test_message}")
    
    response_start = time.time()
    response = ""
    for chunk in chat_with_gcode(test_message, []):
        response = chunk
    
    response_time = time.time() - response_start
    
    print(f"响应: {response[:100]}...")
    print(f"响应时间: {response_time:.2f}秒")
    
    return preload_time, response_time

def main():
    """主测试函数"""
    print("🚀 开始测试预加载效果")
    
    # 测试1: 不预加载
    try:
        no_preload_response_time, no_preload_total_time = test_without_preload()
    except Exception as e:
        print(f"❌ 测试1失败: {e}")
        no_preload_response_time = no_preload_total_time = 0
    
    # 清理导入缓存，模拟重新启动
    modules_to_remove = [m for m in sys.modules if m.startswith('qa') or m.startswith('model')]
    for module in modules_to_remove:
        del sys.modules[module]
    
    # 测试2: 预加载
    try:
        preload_time, preload_response_time = test_with_preload()
    except Exception as e:
        print(f"❌ 测试2失败: {e}")
        preload_time = preload_response_time = 0
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"不使用预加载:")
    print(f"  - 首次响应时间: {no_preload_response_time:.2f}秒")
    print(f"  - 总耗时（含导入）: {no_preload_total_time:.2f}秒")
    print(f"\n使用预加载:")
    print(f"  - 预加载时间: {preload_time:.2f}秒")
    print(f"  - 响应时间: {preload_response_time:.2f}秒")
    print(f"  - 总耗时: {preload_time + preload_response_time:.2f}秒")
    
    if no_preload_response_time > 0 and preload_response_time > 0:
        improvement = ((no_preload_response_time - preload_response_time) / no_preload_response_time) * 100
        print(f"\n✨ 性能提升: {improvement:.1f}%")

if __name__ == "__main__":
    main()