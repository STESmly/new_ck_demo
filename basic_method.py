import os
from nonebot.log import logger
import httpx
import re
import json
from .读取词库 import data_dir

file_path = data_dir / "data"
if not file_path.exists():
    file_path.mkdir(parents=True, exist_ok=True)


async def safe_value(value:str,str_type=True):
    value = value.replace("{","{{").replace("}","}}").replace("'","\\'")
    try:
        res = int(value)
        return res
    except:
        if str_type:
            return f"f'{value}'"
        else:
            return value

async def read_txt(user_path, user_value, user_key=None,file_path=file_path):
    user_path = str(user_path)
    user_value = str(user_value)
    
    config = {}
    file_path = os.path.join(file_path, user_path)
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    if not os.path.exists(file_path):
        open(file_path, 'w', encoding='utf-8').close()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        if user_key != None:
            user_key = str(user_key)
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if '=' in line:
                    key, value = line.split('=')
                    config[key.strip()] = value.strip()
                else:
                    logger.warning(f"文件：{file_path} 不符合当前读取逻辑，请检查文件格式")
                    return await safe_value(user_value,False)
            return await safe_value(config.get(user_key, user_value),False)
            
        else:
            content = f.read()
            if len(content) != 0:
                return await safe_value(content,False)
            else:
                return await safe_value(user_value,False)


async def write_txt(user_path, value, key=None,file_path=file_path):
    user_path = str(user_path)
    user_value = str(user_value)
    file_path = os.path.join(file_path, user_path)
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    if not os.path.exists(file_path):
        open(file_path, 'w', encoding='utf-8').close()

    config = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        key = str(key)
        for line in f:
            line = line.strip()
            if not line:
                continue
            if '=' in line:
                k, v = line.split('=')
                config[k.strip()] = v.strip()

                config[key] = value

                with open(file_path, 'w', encoding='utf-8') as f:
                    for k, v in config.items():
                        f.write(f"{k} = {v}\n")
            else:
                logger.warning(f"写入失败！ 文件：{file_path} 不符合当前写入逻辑，请检查文件格式")
    if key is not None:
        config[key] = value
        with open(file_path, 'w', encoding='utf-8') as f:
            for k, v in config.items():
                f.write(f"{k} = {v}\n")
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"{value}")
    return ""
    
async def get_url(url,method='get', headers=None,upjson=None):
    client = httpx.Client()
    if method == 'get':
        if headers == None:
            res = client.get(url)
        else:
            res = client.get(url, headers=headers)
    elif method == 'post':
        if headers == None:
            if upjson == None:
                res = client.post(url)
            else:
                res = client.post(url, json=upjson)
        else:
            if upjson == None:
                res = client.post(url, headers=headers)
            else:
                res = client.post(url, headers=headers, json=upjson)
    try:
        data = json.loads(res.text)
        return data
    except:
        return res.text


async def convert_message_string(raw: str) -> str:
    """
    将字符串中的自定义 ±语法± 转为标准 CQ 码，
    同时将原本存在的 [CQ:...] 转义为普通文本。
    """
    # 第一步：转义所有方括号（包括 [ 和 ]）
    escaped = raw.replace('[', '&#91;').replace(']', '&#93;')
    
    def _to_cq(match):
        inner = match.group(1).strip()  # 例如 "image file=1.jpg,url=http://..."
        # 按第一个空格分割
        if ' ' not in inner:
            # 没有空格，可能只有类型无参数
            return ""
        parts = inner.split(' ', 1)
        cq_type = parts[0].strip()
        params_str = parts[1].strip()
        # params_str 格式: "param1=value1,param2=value2,..."
        # 注意：如果参数值中有逗号，应该转义，这里假设没有
        return f'[CQ:{cq_type},{params_str}]'
    converted = re.sub(r'±([^±]+)±', _to_cq, escaped)
    return converted

async def match_math_expression(expr):
    try:
        json.loads(expr)
        return
    except:
        token_pattern = re.compile(r'\%[^%%]*\%|\[[^\[\]]*\]|\d+|[+\-*/]')

        # 将表达式分割成令牌列表
        tokens = token_pattern.findall(expr)
        
        def parse_expression(tokens):
            def parse_term(tokens):
                term = parse_factor(tokens)
                while tokens and tokens[0] in ('*', '/'):
                    tokens.pop(0)  # 移除运算符
                    parse_factor(tokens)
                return term

            def parse_factor(tokens):
                if tokens[0] == '(':
                    tokens.pop(0)  # 移除左括号
                    parse_expression(tokens)
                    if not tokens or tokens.pop(0) != ')':
                        return
                elif tokens[0] == '[':
                    tokens.pop(0)  # 移除左方括号
                    parse_bracket_expression(tokens)
                    if not tokens or tokens.pop(0) != ']':
                        return
                else:
                    tokens.pop(0)  # 移除数字

            def parse_bracket_expression(tokens):
                parse_term(tokens)
                while tokens and tokens[0] in ('+', '-'):
                    tokens.pop(0)  # 移除运算符
                    parse_term(tokens)

            parse_term(tokens)
            while tokens and tokens[0] in ('+', '-'):
                tokens.pop(0)  # 移除运算符
                parse_term(tokens)

        try:
            parse_expression(tokens)
            if tokens:
                return
        except IndexError:
            return 

        # 将[]替换成()
        return expr.replace('[', '(').replace(']', ')').replace('%', '').replace('{', '(').replace('}', ')')

async def list_to_number(list):
    try:
        result = await match_math_expression(list)
    except ValueError as e:
        result = None
    if result is None:
        return False
    return result

async def extract_formulas(s):
    """提取所有括号正确闭合的算式块"""
    blocks = []
    current_start = -1
    depth = 0
    for i, c in enumerate(s):
        if c == '[':
            if depth == 0:
                current_start = i  # 开始新块
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0 and current_start != -1:
                blocks.append(s[current_start:i+1])  # 记录闭合块
                current_start = -1
    return blocks

async def split_formulas(s):
    """将连续表达式分割为独立算式"""
    result = []
    start = 0
    depth = 0
    for i, c in enumerate(s):
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                result.append(s[start:i+1])
                start = i + 1
    if depth != 0:
        raise ValueError(f"括号未闭合: {s}")
    return result

async def extract_and_split(s):
    """组合提取和分割过程"""
    blocks = await extract_formulas(s)
    final_result = []
    for block in blocks:
        final_result.extend(await split_formulas(block))
    return final_result