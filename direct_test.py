# -*- coding: utf-8 -*-
"""
直接测试意图识别模块
"""

import os
import sys

# 设置环境
os.environ['PY_ENVIRONMENT'] = 'local'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_direct():
    """直接测试函数"""
    print("🚀 直接测试意图识别模块")
    
    try:
        from qa.question_parser import parse_process_type
        
        test_inputs = [
            "我要加工外圆，长度是50mm，进给速度300",
            "请帮我车一个内孔，直径20mm", 
            "外螺纹加工，M10螺纹",
            "车端面，表面要平整"
        ]
        
        for i, test_input in enumerate(test_inputs, 1):
            print(f"\n{'='*60}")
            print(f"测试 {i}: {test_input}")
            print('='*60)
            
            try:
                result = parse_process_type(test_input)
                print(f"结果: {result}")
            except Exception as e:
                print(f"错误: {e}")
                import traceback
                traceback.print_exc()
                
    except ImportError as e:
        print(f"导入失败: {e}")
        print("请确认环境配置正确")

if __name__ == "__main__":
    test_direct()