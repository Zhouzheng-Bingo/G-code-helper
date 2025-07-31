#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
移除代码中的sleep延迟以提升性能
"""

import re

def remove_sleep_from_file(filepath):
    """移除文件中的sleep延迟代码"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换带有sleep的循环为直接yield
        # 模式1: for i in range(len(response)):
        #         time.sleep(0.05)
        #         yield response[:i + 1]
        pattern1 = r'for i in range\(len\(response\)\):\s*\n\s*time\.sleep\([0-9.]+\)\s*\n\s*yield response\[:i \+ 1\]'
        replacement1 = 'yield response'
        
        content = re.sub(pattern1, replacement1, content)
        
        # 替换带有sleep的循环为直接yield（变量名可能不同）
        pattern2 = r'for i in range\(len\((.*?)\)\):\s*\n\s*time\.sleep\([0-9.]+\)\s*\n\s*yield \1\[:i \+ 1\]'
        replacement2 = r'yield \1'
        
        content = re.sub(pattern2, replacement2, content)
        
        if content != original_content:
            # 备份原文件
            with open(filepath + '.backup', 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # 写入修改后的内容
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 已修改 {filepath}")
            print(f"   备份保存为 {filepath}.backup")
            
            # 统计修改了多少处
            changes = original_content.count('time.sleep') - content.count('time.sleep')
            print(f"   移除了 {changes} 处 sleep 延迟")
            
            return True
        else:
            print(f"ℹ️  {filepath} 无需修改")
            return False
            
    except Exception as e:
        print(f"❌ 处理 {filepath} 时出错: {e}")
        return False

def main():
    print("🚀 开始移除sleep延迟...")
    print("="*60)
    
    files_to_process = [
        'qa/interaction.py',
    ]
    
    total_changes = 0
    for file in files_to_process:
        if remove_sleep_from_file(file):
            total_changes += 1
    
    print("="*60)
    print(f"✅ 完成！共修改了 {total_changes} 个文件")
    print("\n⚠️  注意：")
    print("1. 原文件已备份为 .backup 文件")
    print("2. 如需恢复，可以使用备份文件")
    print("3. 移除sleep后，响应会立即显示完整内容，而非逐字显示")

if __name__ == "__main__":
    main()