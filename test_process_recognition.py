from qa.question_parser import parse_process_type

def test_process_recognition():
    # 预定义一些测试用例
    test_cases = [
        "我要使用外圆工艺加工一个外圆",
        "我想用外圆工艺",  # 只说主工艺
        "帮我加工一个外锥面",  # 只说子工艺
        "你好，请问今天天气怎么样？",  # 非工艺问题
        "我要加工一个内孔，使用里孔工艺",
        "使用螺纹工艺加工外直螺纹",
        "G代码是什么意思？",  # 非工艺问题
        "我要加工端面，使用端面工艺"
    ]
    
    print("\n=== 自动测试用例 ===")
    for question in test_cases:
        print("\n" + "="*50)
        print(f"测试问题: {question}")
        process_info = parse_process_type(question)
        print(f"主工艺: {process_info['main_process']}")
        print(f"子工艺: {process_info['sub_process']}")
        
    print("\n=== 交互式测试 ===")
    print("现在你可以输入任何问题进行测试(输入'q'退出)")
    while True:
        question = input("\n请输入测试问题: ")
        if question.lower() == 'q':
            break
            
        process_info = parse_process_type(question)
        print("\n识别结果:")
        print(f"主工艺: {process_info['main_process']}")
        print(f"子工艺: {process_info['sub_process']}")
        
        # 如果识别出主工艺但没有子工艺，显示可选的子工艺
        if process_info['main_process'] != "NO_PROCESS" and not process_info['sub_process']:
            sub_process_mapping = {
                "外圆工艺": ["外圆", "外锥面", "外圆弧"],
                "端面工艺": ["端面", "切槽", "内端面"],
                "里孔工艺": ["内圆", "内锥面", "内槽", "内弧", "中心孔"],
                "锥面工艺": ["外正锥面", "外反锥面", "内正锥面", "内反锥面"],
                "螺纹工艺": ["外直螺纹", "外锥（管）螺纹", "内直螺纹", "内锥（管）螺纹"],
                "倒角工艺": ["外圆角倒角", "外倒角", "内圆角倒角", "内倒角"]
            }
            if process_info["main_process"] in sub_process_mapping:
                print("\n可选的子工艺类型:")
                for sub_type in sub_process_mapping[process_info["main_process"]]:
                    print(f"- {sub_type}")

if __name__ == "__main__":
    test_process_recognition() 