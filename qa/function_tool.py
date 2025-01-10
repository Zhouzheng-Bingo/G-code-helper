import json
from typing import List, Tuple, Callable, Optional

from openai import Stream
from openai.types.chat import ChatCompletionChunk

from dao.graph.graph_dao import GraphDao
from lang_chain import rag_chain
from lang_chain.client.client_factory import ClientFactory
from qa.question_type import QuestionType
from model.graph_entity.search_model import _Value
from qa.prompt_templates import HELLO_ANSWER_TEMPLATE, LLM_HINT

_dao = GraphDao()

# 添加基类定义
class P:
    """工艺基类"""
    def __init__(self, sub_process_type: str, **kwargs):
        self.sub_process_type = sub_process_type

    def generate_gcode(self) -> str:
        raise NotImplementedError

# def relation_tool(entities: List[_Value] | None) -> Tuple[str, QuestionType] | None:
def relation_tool(*entities: _Value) -> Tuple[str, QuestionType] | None:
    # 0.用question问大模型得到工艺
    # 1.使用自己写的cypter语句获取模版
    # 2.F:进给速度 有配置
    # 3. 问题 ：entities[0]

    """G指令关系"""
    if not entities or len(entities) < 2:
        return None
    relationship_match = _dao.query_relationship_by_2points(entities[0].name, entities[1].name)
    if relationship_match:

        rel = relationship_match[0]['type(r)']
        if entities[0].name not in rel:
            start_name = entities[0].name
        else:
            start_name = entities[1].name
        return f"关系如下：{start_name}{rel}，详见:{relationship_match[0]['r']['Notes']}", QuestionType.GCODE_KNOWLEDGE_GRAPH


def document_search_tool(
        question: str,
        history: List[List[str] | None] = None
) -> Tuple[Tuple[str, Stream[ChatCompletionChunk]], QuestionType]:
    reference, response = rag_chain.invoke(question, history)
    return (reference, response), QuestionType.PDF_DOCUMENT

def hello_tool() -> Tuple[str, QuestionType]:
    """问候语"""
    response = ClientFactory().get_client().chat_with_ai(HELLO_ANSWER_TEMPLATE)
    return response, QuestionType.HELLO

def process_unknown_question_tool(
        question: str,
        history: List[List[str] | None] = None,
) -> Tuple[Tuple[str, Stream[ChatCompletionChunk]], QuestionType]:
    """处理未知类型的问题，包括纯知识性问题"""
    prompt = f"""
    你是一个数控加工专家。请回答用户关于数控加工的问题。
    如果是G代码相关的问题，请详细解释其功能和用法。
    如果是工艺相关的问题，请从专业角度给出建议。
    请用中文回答。

    用户问题: {question}
    """
    
    response = ClientFactory().get_client().chat_with_ai_stream(prompt, history[-5:] if history else None)
    return ("", response), QuestionType.UNKNOWN

TOOLS_MAPPING = {
    QuestionType.GCODE_KNOWLEDGE_GRAPH: relation_tool,
    QuestionType.PDF_DOCUMENT: document_search_tool,
    QuestionType.HELLO: hello_tool,
    QuestionType.UNKNOWN: process_unknown_question_tool,
}

def map_question_to_function(
    question_type: QuestionType,
) -> Callable:
    if question_type in TOOLS_MAPPING:
        return TOOLS_MAPPING[question_type]
    else:
        raise ValueError(f"No tool found for question type: {question_type}")

FUNCTION_ARGS_MAPPING = {
    QuestionType.GCODE_KNOWLEDGE_GRAPH: lambda args: args[1:3],
    QuestionType.PDF_DOCUMENT: lambda args: args[1:3],
    QuestionType.HELLO: lambda args: [],
    QuestionType.UNKNOWN: lambda args: args[1:3],
}

def map_question_to_function_args(
    question_type: QuestionType,
) -> Callable[[List], List]:
    if question_type in FUNCTION_ARGS_MAPPING:
        return FUNCTION_ARGS_MAPPING[question_type]
    else:
        raise ValueError(f"No argument mapping found for question type: {question_type}")

def identify_process_type(question: str) -> dict:
    """
    使用大模型识别用户问题中的工艺类型
    Args:
        question: 用户的问题文本
    Returns:
        dict: 包含主工艺和子工艺的字典
    """
    prompt = f"""
    你是一个数控加工工艺识别专家。请从用户的问题中识别出用户想要使用的加工工艺类型。
    只返回一个JSON对象，不要包含任何其他文字。
    
    规则：
    1. 如果问题中提到了主工艺和子工艺，需要同时返回两者
    2. 如果只提到了主工艺，子工艺返回null
    3. 如果只提到了子工艺，需要推断出对应的主工艺
    4. 如果问题与加工工艺完全无关，返回 NO_PROCESS
    5. 必须严格匹配以下工艺名称，不能用其他变体
    
    主工艺和对应的子工艺对照表:
    - 外圆工艺: [外圆, 外锥面, 外圆弧]
    - 端面工艺: [端面, 切槽, 内端面]
    - 里孔工艺: [内圆, 内锥面, 内槽, 内弧, 中心孔]
    - 锥面工艺: [外正锥面, 外反锥面, 内正锥面, 内反锥面]
    - 螺纹工艺: [外直螺纹, 外锥（管）螺纹, 内直螺纹, 内锥（管）螺纹]
    - 倒角工艺: [外圆角倒角, 外倒角, 内圆角倒角, 内倒角]
    
    示例输出格式：
    {{"main_process": "外圆工艺", "sub_process": "外圆"}}
    
    用户问题: {question}
    """
    
    response = ClientFactory().get_client().chat_with_ai(prompt)
    try:
        # 清理响应文本，只保留JSON部分
        response = response.strip()
        # 如果响应包含多行，尝试找到JSON部分
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                response = line
                break
        
        result = json.loads(response)
        
        # 验证返回值的格式
        if not isinstance(result, dict):
            raise ValueError("返回值不是字典类型")
        if "main_process" not in result or "sub_process" not in result:
            raise ValueError("返回值缺少必要的字段")
            
        return result
        
    except Exception as e:
        print(f"解析错误: {e}")
        print(f"原始响应: {response}")
        # 如果出现错误，返回默认值
        return {
            "main_process": "NO_PROCESS",
            "sub_process": None
        }

def get_process_template(sub_process: str) -> str:
    """
    从知识图谱中获取指定子工艺的代码模板
    Args:
        sub_process: 子工艺名称
    Returns:
        str: 代码模板字符串
    """
    try:
        query = f"""
        MATCH (s:SubProcess {{name: '{sub_process}'}})
        RETURN s.code as code
        """
        result = _dao.run_cypher(query).data()
        print(f"查询结果: {result}")
        
        if result and len(result) > 0 and 'code' in result[0]:
            code = result[0]['code']
            # 直接返回代码，不做额外处理
            return code
            
        print(f"未找到{sub_process}的代码模板")
        return None
    except Exception as e:
        print(f"获取模板时出错: {e}")
        return None

def parse_template_params(template: str) -> list:
    """
    从代码模板中解析需要的参数
    Args:
        template: 代码模板字符串
    Returns:
        list: 参数列表
    """
    prompt = f"""
    请从以下Python类的代码中提取参数信息。
    只返回参数名称，每行一个，不要包含任何其他文字、标点或格式标记。
    不要包含 sub_process_type 和 kwargs。
    
    示例输出格式：
    Cn
    L
    Tr
    Cr
    F
    
    代码：
    {template}
    """
    
    response = ClientFactory().get_client().chat_with_ai(prompt)
    # 清理响应文本
    response = response.strip()
    if '```' in response:
        # 提取代码块内容
        response = response.split('```')[1].strip()
    # 过滤掉空行和非参数行
    params = [line.strip() for line in response.split('\n') 
             if line.strip() and not line.startswith('-') and not line.startswith('`')]
    return params

def generate_gcode(sub_process: str, params: dict) -> str:
    """
    使用模板和参数生成G代码
    Args:
        sub_process: 子工艺名称
        params: 用户提供的参数字典
    Returns:
        str: 生成的G代码
    """
    try:
        # 1. 获取代码模板
        template = get_process_template(sub_process)
        if not template:
            raise ValueError(f"未找到{sub_process}的代码模板")
        
        # 2. 动态执行代码模板
        namespace = {
            'P': P,
            'str': str,
            'int': int,
            'float': float,
            'range': range,
            'len': len,
            'ValueError': ValueError
        }
        
        try:
            exec(template, namespace)
        except SyntaxError as e:
            print(f"代码模板语法错误: {e}")
            print(f"代码模板:\n{template}")
            raise ValueError("代码模板存在语法错误")
            
        # 3. 获取类名（假设是模板中唯一的类）
        process_class = None
        for name, item in namespace.items():
            if isinstance(item, type) and issubclass(item, P) and name != 'P':
                process_class = item
                break
                
        if not process_class:
            raise ValueError("代码模板中未找到有效的工艺类")
        
        # 4. 实例化类并生成G代码
        try:
            instance = process_class(sub_process_type=sub_process, **params)
            gcode = instance.generate_gcode()
            if not isinstance(gcode, str):
                raise ValueError("生成的G代码必须是字符串类型")
            if not gcode.strip():
                raise ValueError("生成的G代码不能为空")
            print(f"生成的G代码:\n{gcode}")  # 添加这行来查看生成的G代码
            return gcode
        except Exception as e:
            print(f"生成G代码时出错: {e}")
            print(f"参数: {params}")
            raise ValueError(f"生成G代码失败: {str(e)}")
            
    except Exception as e:
        print(f"生成G代码时的详细错误: {str(e)}")
        print(f"参数: {params}")
        raise ValueError(f"生成G代码时出错: {str(e)}")
