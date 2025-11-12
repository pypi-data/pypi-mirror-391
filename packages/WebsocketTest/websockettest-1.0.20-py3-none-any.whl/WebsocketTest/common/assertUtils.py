import re
from WebsocketTest.common.utils import *
from typing import Literal
from typing import Any, Dict, Generator, Optional,Literal
from datetime import timedelta,date

# 使用预定义的表达式映射
EXPR_MAP = {
    'today': lambda: str(date.today()),  # 今天，格式如 "2023-11-16"
    'tomorrow': lambda: str(date.today() + timedelta(days=1)),  # 明天,格式如 "2023-11-17"
    'yesterday': lambda: str(date.today() - timedelta(days=1))  # 昨天
}
def safe_eval(expr):
    if expr in EXPR_MAP:
        return EXPR_MAP[expr]() # 调用对应的 lambda 函数
    raise ValueError(f"Invalid expression: {expr}")

def get_value(data, path, decode_funcs=None):
    """
    获取嵌套字典中的值。
    
    :param data: 嵌套字典
    :param path: 字典路径，用点号分隔
    :param decode_funcs: 一个字典，键是路径，值是解码函数
    :return: 路径对应的值, 如果路径不存在则返回None
    """
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    # 特殊处理某些路径的值
    if decode_funcs and path in decode_funcs:
        return decode_funcs[path](current)
    else:
        return current

def get_key_value(input_str, delimiter=',，', pair_delimiter='=',opt: Literal["in", "not in"]="in"):
    """
    解析键值对字符串，返回指定数据格式。
    
    :param input_str: 键值对字符串
    :param delimiter: 键值对之间的分隔符，默认为逗号
    :param pair_delimiter: 键和值之间的分隔符，默认为等号
    :return: 键和值
    """
    def should_include(part):
        """根据 opt 判断是否包含该部分"""
        if opt == "in":
            return pair_delimiter in part
        elif opt == "not in":
            return ":" not in part
        else:
            raise ValueError(f"Invalid operation: {opt}")

    # 解析字符串并根据 opt 进行过滤
    key_value_map = {part.split(pair_delimiter)[0].strip():part.strip().split(pair_delimiter)[1].strip() for part in re.split(rf'[{delimiter}]', input_str) if should_include(part)}
    return key_value_map


def get_Urlparam_dic(urlstr, json_fields=None):
    """
    将URL查询字符串解析为字典，并处理特定字段的JSON解码。
    
    :param urlstr: 完整的URL字符串
    :param json_fields: 需要进行JSON解码的字段列表
    :return: 解析后的字典
    """
    if json_fields is None:
        json_fields = []
    # 如果URL中没有查询字符串，直接返回空字典
    if '?' not in urlstr:
        return {}
    
    # 分离URL和查询字符串
    _, _params = urlstr.split('?', 1)
    
    # 解析查询字符串为键值对
    params = urllib.parse.parse_qs(_params)
    # 解码值并构建字典,values[0]取第一个值（假设每个键只有一个值）
    obj = {key: url_decode(values[0]) if values else None for key, values in params.items()}
    def decode_json_field(field, value):
        """
        尝试将字段值解析为JSON对象。
        
        :param field: 字段名
        :param value: 字段值
        :return: 解析后的JSON对象或原始值
        """
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            print(f"JSON解码错误: {e}")
            print(f"字段 '{field}' 的值为: {value}")
            return None
    # 解析特定字段为JSON对象
    for field in json_fields:
        if field in obj:
            obj[field] = decode_json_field(field, obj[field])
    
    return obj
    

def has_key(obj, key_path):
    """
    检查一个对象中是否存在指定的键路径。

    :param obj: 要检查的对象。
    :param key_path: 键路径，用点号分隔。
    :return: 如果路径存在则返回True, 否则返回False。
    """
    current_obj = obj
    keys = key_path.split('.')
    for key in keys:
            if key in current_obj:
                current_obj = current_obj[key] 
            else:
                return False
    return True


def find_matching_index(
    data: Any,
    conditions: Dict[str, str],
    current_path: str = ""
) -> Generator[str, None, None]:
    """
    递归查找匹配条件的第一个列表索引（生成器版本）
    """
    if isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, (dict, list)):
                new_path = f"{current_path}[{index}]"
                yield from find_matching_index(item, conditions, new_path)
    elif isinstance(data, dict):
        if all(str(data.get(key)) == value for key, value in conditions.items()):
            if match := re.search(r'\[(\d+)\]', current_path):
                yield match.group(1)
        for key, value in data.items():
            new_path = f"{current_path}.{key}" if current_path else key
            if isinstance(value, (dict, list)):
                yield from find_matching_index(value, conditions, new_path)

def find_first_match(
    data: Any,
    conditions: Dict[str, str]
) -> Optional[str]:
    """
    优化版：直接返回第一个匹配的索引（或None）
    """
    return next(find_matching_index(data, conditions), None)

