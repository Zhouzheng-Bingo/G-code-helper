#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试增强功能
"""

import os
import sys

os.environ['PY_ENVIRONMENT'] = 'local'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试导入
try:
    from qa.llm_centric_classifier import llm_centric_parse_process_type
    print("✅ 模块导入成功")
    
    # 测试一个简单例子
    test_input = "车一个外圆"
    print(f"\n测试输入: {test_input}")
    
    result = llm_centric_parse_process_type(test_input)
    print(f"结果: {result}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()