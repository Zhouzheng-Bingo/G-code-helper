#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

user_input = "我要使用外圆工艺加工一个外圆，每次进刀量0.5毫米，总共进两刀，进刀量总共是一毫米，加工长度是100毫米，加工速度是300毫米每分"

print("调试正则表达式模式匹配")
print(f"用户输入: {user_input}")
print("-" * 80)

# 测试Cn的模式
cn_patterns = [
    r'总共进(\d+)刀',
    r'进(\d+)刀', 
    r'循环(\d+)次',
    r'Cn[是为=:]?\s*(\d+)',
]

print("🔍 调试Cn参数:")
for pattern in cn_patterns:
    match = re.search(pattern, user_input, re.IGNORECASE)
    if match:
        print(f"✅ 模式 '{pattern}' 匹配成功: {match.group(1)}")
    else:
        print(f"❌ 模式 '{pattern}' 匹配失败")

print()

# 测试Cr的模式  
cr_patterns = [
    r'进刀量总共[是为:]?\s*(\d+(?:\.\d+)?)毫米',
    r'总进刀量[是为:]?\s*(\d+(?:\.\d+)?)毫米',
    r'Cr[是为=:]?\s*(\d+(?:\.\d+)?)',
]

print("🔍 调试Cr参数:")
for pattern in cr_patterns:
    match = re.search(pattern, user_input, re.IGNORECASE)
    if match:
        print(f"✅ 模式 '{pattern}' 匹配成功: {match.group(1)}")
    else:
        print(f"❌ 模式 '{pattern}' 匹配失败")

print()

# 显示具体文本段落
print("🔍 分析具体文本:")
print("关键短语: '总共进两刀'")
print("关键短语: '进刀量总共是一毫米'")

# 尝试改进的模式
print()
print("🔧 尝试改进的模式:")

# 改进的Cn模式
improved_cn_patterns = [
    r'总共进([二两2２]\d*)刀',
    r'总共进(\d+)刀',
    r'进([二两2２]\d*)刀',
    r'进(\d+)刀',
]

for pattern in improved_cn_patterns:
    match = re.search(pattern, user_input, re.IGNORECASE)
    if match:
        # 处理中文数字
        value = match.group(1)
        if value in ['二', '两', '2', '２']:
            value = '2'
        print(f"✅ 改进模式 '{pattern}' 匹配成功: {value}")
        break
    else:
        print(f"❌ 改进模式 '{pattern}' 匹配失败")

# 改进的Cr模式  
improved_cr_patterns = [
    r'进刀量总共[是为:]?\s*([一1１])毫米',
    r'进刀量总共[是为:]?\s*(\d+(?:\.\d+)?)毫米',
    r'总共[是为:]?\s*([一1１])毫米',
]

for pattern in improved_cr_patterns:
    match = re.search(pattern, user_input, re.IGNORECASE)
    if match:
        # 处理中文数字
        value = match.group(1)
        if value in ['一', '1', '１']:
            value = '1'
        print(f"✅ 改进模式 '{pattern}' 匹配成功: {value}")
        break
    else:
        print(f"❌ 改进模式 '{pattern}' 匹配失败")