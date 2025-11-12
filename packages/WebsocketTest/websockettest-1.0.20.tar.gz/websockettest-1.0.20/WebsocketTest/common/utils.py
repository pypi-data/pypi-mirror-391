import  base64, json,os
import pandas as pd
import inspect,urllib
import random
import string
from datetime import datetime
import email.utils
from functools import wraps,reduce
from WebsocketTest.common.logger import logger
from typing import Optional, Union, Literal
import uuid
import hashlib
import asyncio
def get_rfc1123_time():
        # 获取当前UTC时间
        now = datetime.utcnow()
        # 将时间格式化为RFC1123格式
        rfc1123_time = email.utils.format_datetime(now)
        return rfc1123_time

def generate_random_string(length=32):
    """
    生成指定长度的随机字符串，该字符串可以从包含小写字母、数字以及'@'符号的字符集中随机选择。
    
    Args:
        length (int): 生成字符串的长度，默认为32。
    
    Returns:
        str: 生成的随机字符串。
    """
    if length < 1:
        raise ValueError("Length must be at least 1.")
    
    # 定义字符池：包含小写字母、数字和 '@' 符号
    chars = string.ascii_lowercase + string.digits + "@"
    
    # 从字符池中随机选择指定数量的字符
    random_chars = random.choices(chars, k=length)
    
    return ''.join(random_chars)

def decode_unicode_escape(data):
    """
    递归地遍历字典或列表，将所有字符串值中的Unicode转义序列解码为原始字符。
    
    Args:
        data (dict or list): 包含Unicode转义序列的JSON对象（字典或列表）。
    
    Returns:
        dict or list: 解码后的JSON对象，其中所有字符串值已被正确解码。
    """
    if isinstance(data, dict):
        return {key: decode_unicode_escape(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [decode_unicode_escape(element) for element in data]
    elif isinstance(data, str):
        try:
            # 使用 json.loads 来解析包含转义字符的字符串
            return json.loads(f'"{data}"')
        except json.JSONDecodeError:
            # 如果字符串不是有效的JSON字符串，则直接返回原字符串
            return data
    else:
        # 对于其他类型的数据，直接返回它们
        return data

def convert_to_json(data):
    """
    将包含Unicode转义序列的JSON数据解码，并返回JSON格式的字符串。
    
    Args:
        data (dict or list): 包含Unicode转义序列的JSON对象（字典或列表）。
    
    Returns:
        str: 解码并格式化后的JSON字符串。
    """
    decoded_data = decode_unicode_escape(data)
    return json.dumps(decoded_data, ensure_ascii=False, indent=4)
    
def encode_base64(
    s: Optional[Union[str, bytes]],
    *,
    input_encoding: Literal['auto', 'str', 'bytes'] = 'auto',
    output_encoding: str = 'utf-8'
) -> Optional[str]:
    """将字符串或字节数据编码为 Base64 格式
    
    Args:
        s: 要编码的输入数据，可以是字符串或字节，None 直接返回 None
        input_encoding: 输入处理模式：
            'auto' - 自动检测类型（默认）
            'str' - 强制作为字符串处理
            'bytes' - 强制作为字节处理
        output_encoding: 输出结果的编码格式（默认utf-8）
    
    Returns:
        Base64 编码后的字符串，如果输入为 None 则返回 None
    
    Raises:
        TypeError: 输入类型不符合要求
        ValueError: 编码失败或模式参数无效
    """
    if s is None:
        return None

    # 输入类型处理
    try:
        if input_encoding == 'str':
            data = s.encode('utf-8') if isinstance(s, str) else s
        elif input_encoding == 'bytes':
            data = s if isinstance(s, bytes) else str(s).encode('utf-8')
        elif input_encoding == 'auto':
            data = s.encode('utf-8') if isinstance(s, str) else s
        else:
            raise ValueError(f"Invalid input_encoding: {input_encoding}")
    except (AttributeError, UnicodeError) as e:
        raise ValueError(f"Input encoding failed: {str(e)}") from e

    if not isinstance(data, bytes):
        raise TypeError(f"Expected bytes or string, got {type(s).__name__}")

    # Base64 编码
    try:
        return base64.b64encode(data).decode(output_encoding)
    except UnicodeError as e:
        raise ValueError(f"Output decoding failed: {str(e)}") from e
def decode_base64(s):
    """将 Base64 编码的字符串解码回原始字符串"""
    return base64.b64decode(s.encode('utf-8')).decode('utf-8') if s is not None else None

def url_decode(str_):
    """
    解码URL编码的字符串。
    
    :param str_: URL编码的字符串
    :return: 解码后的字符串
    """
    return urllib.parse.unquote_plus(str_)  if str_ else None

def check_text_language(text):
    """
    检查文本是纯中文、纯英文还是中文加英文。
    
    :param text: 需要检查的文本
    :return: 文本的语言类型 ('纯中文', '纯英文', '中文+英文', '其他')
    """
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
    has_english = any('a' <= char <= 'z' or 'A' <= char <= 'Z' for char in text)

    if has_chinese and has_english:
        return "中文+英文"
    elif has_chinese:
        return "纯中文"
    elif has_english:
        return "纯英文"
    else:
        return "其他"
    
def safe_get(data, keys, default=""):
    """用 reduce 安全访问嵌套字典"""
    try:
        return reduce(lambda d, k: d[k], keys, data)
    except (KeyError, TypeError):
        return default
    # """ 安全地从嵌套字典中获取值 """
    # for key in keys:
    #     try:
    #         data = data[key]
    #     except (KeyError, TypeError):
    #         return default
    # return data

def append_msg_to_excel(file_path, **kwargs):
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 如果文件不存在，创建一个新的 DataFrame 并保存为 Excel 文件
            existing_df = pd.DataFrame()
        else:
            # 读取现有数据
            existing_df = pd.read_excel(file_path)

        # 动态构建 new_data 字典
        new_data = {**kwargs}

        # 将新数据转换为 DataFrame
        new_df = pd.DataFrame([new_data])

        # 追加新数据到现有数据
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)

        # 写回 Excel 文件
        updated_df.to_excel(file_path, index=False)
    except Exception as e:
        # 获取当前文件名和方法名
        current_file = inspect.getfile(inspect.currentframe())
        current_function = inspect.currentframe().f_code.co_name
        print(f"An error occurred in file '{current_file}' and function '{current_function}': {e}")

def read_excel(file_path,sheet_name):
    df = pd.read_excel(file_path,sheet_name, header=0, dtype={'debug': str,'debugX': str})
    # 如果确实需要空字符串，先转换类型
    pd.set_option('future.no_silent_downcasting', True)
    df = df.astype(object).fillna("")  # 转换为object类型
    data_dict = df.to_dict(orient='records')
    return data_dict

def exception_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 直接使用被装饰函数的名字
            function_name = func.__name__
            file_name = os.path.basename(func.__code__.co_filename)  # 提取文件名
            # 打印异常和函数名
            logger.error( f"异常发生在文件 [{file_name}] 的函数 [{function_name}] 中: {str(e)}",
                exc_info=True  # 自动追加堆栈信息
                )
            # 可选择再次抛出异常或进行其他处理
            raise
    return wrapper
def merge_dicts(a: dict, b: dict) -> dict:
    """合并两个字典，重复key时优先取a中非空的值
    
    Args:
        a: 优先字典（保留其非空值）
        b: 后备字典（当a中的值为空时使用）
    
    Returns:
        合并后的新字典
    """
    return {
        # 遍历所有key（a和b的key取并集）
        k: 
            # 如果key在a中 且 a的value不是空值 → 取a的值
            a.get(k) if k in a and a.get(k) not in (None, "") 
            # 否则 → 取b的值（可能为None）
            else b.get(k)
        # 获取a和b的所有key的并集（避免用a|b需要Python 3.9+）
        for k in set(a) | set(b)
    }

def gen_case_suite(file_path,sheet_name):
    # 生成测试用例套件
    data_dict = read_excel(file_path,sheet_name)
    case_suite = []
    for case in data_dict:
        case_suite.append(case)
    return case_suite

def get_auth_id():
    """
    生成基于系统MAC地址的唯一身份验证ID。
    
    返回:
        str: 唯一的身份验证ID。
    """
    # 获取系统MAC地址的整数表示，并转换为12位的十六进制字符串
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    
    # 将MAC地址按照标准格式（使用冒号分隔）重新组合
    formatted_mac = ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
    
    # 对格式化后的MAC地址进行MD5哈希处理，并返回其十六进制表示
    auth_id = hashlib.md5(formatted_mac.encode("utf-8")).hexdigest()
    return auth_id
def get_audio(text_path):
    with open(text_path, "rb") as file:
        content = file.read()
        return encode_base64(content,input_encoding='bytes')

async def send_file_chunks(text_path, ws, CHUNK_SIZE = 1280):
            """异步发送文件分块"""
            try:
                with open(text_path, 'rb') as file:
                    while chunk := file.read(CHUNK_SIZE):
                        await ws.send(chunk)
                        await asyncio.sleep(0.04)
            except IOError as e:
                logger.error(f"文件读取失败: {e}")