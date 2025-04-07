from qa.interaction import chat_with_gcode
from qa.session_state import current_session

def test_gcode_generation():
    print("=== G代码生成测试 ===\n")
    
    # 新的测试：
    # 我要使用外圆工艺加工一个外圆，Cn=2, L=100.0, Tr=0.5, Cr=1.0, F=300.0
    # 我要使用外圆工艺加工一个外圆，Cn是2，L是100.0，Tr是0.5，Cr是1.0，F是300.0
    # 我要使用外圆工艺加工一个外圆，Cn=2
    # 参数大小写也可以不区分，也可以没有逗号

    test_cases = [
        # 测试用例1：完整流程 - 正确的参数
        [
            "我要使用外圆工艺加工一个外圆",
            "2",      # Cn: 整数
            "100.0",  # L: 浮点数
            "0.5",    # Tr: 浮点数
            "1.0",    # Cr: 浮点数
            "300.0"   # F: 浮点数
        ],
        
        # 测试用例2：参数类型错误
        [
            "我要使用外圆工艺加工一个外圆",
            "abc",    # 错误的Cn值
            "100.0"   # 正确的L值
        ],
        
        # 测试用例3：只说主工艺
        ["我要用外圆工艺"],
        
        # 测试用例4：直接说子工艺
        ["我要加工外圆"]
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print("="*50)
        
        # 确保每个测试用例开始时状态是清空的
        current_session.clear()
        
        # 维护会话历史
        history = []
        
        # 模拟对话
        for user_input in test_case:
            print(f"\n用户输入: {user_input}")
            print("系统响应:")
            # chat_with_gcode 返回的是生成器，需要遍历获取完整响应
            response = ""
            for chunk in chat_with_gcode(user_input, history):
                response = chunk  # 获取最后的完整响应
            print(response)
            # 更新历史记录
            history.append([user_input, response])

if __name__ == "__main__":
    test_gcode_generation() 