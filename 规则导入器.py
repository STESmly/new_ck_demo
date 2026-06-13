import re
from functools import wraps
from typing import Callable, Any, Dict, List, Tuple
from .basic_method import safe_value,extract_and_split,list_to_number,convert_message_string

class Matcher:
    """
    判断器：保存条件表达式，并通过 handle 装饰器绑定处理函数
    """
    _registry: List[Tuple[int, str, Callable, Callable]] = []

    def __init__(self, condition: str, method, priority: int = 0):
        self.condition = condition
        self.method = method
        self.priority = priority

    def handle(self):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            Matcher._registry.append((self.priority, self.condition, self.method, func))
            return wrapper
        return decorator

    @staticmethod
    async def dispatch(input_str: str):
        Matcher._registry.sort(key=lambda x: x[0])
        for priority, condition, method, handler in Matcher._registry:
            data = method(rf"{condition}", input_str)
            if data:
                try:
                    data.groups()
                    input_str = await handler(data.groups(), input_str)
                except:
                    input_str = await handler(data, input_str)
            else:
                pass
        return input_str
    


发送 = Matcher("\$发送 ([^\$]*)\$", re.findall, priority=1)
读文件 = Matcher("\$读文件 ([^\$]*) ([^\$]*) ([^\$]*)\$", re.findall, priority=1)
写文件1 = Matcher("\$写文件 ([^\$]*) ([^\$]*) ([^\$]*)\$", re.findall, priority=1)
写文件2 = Matcher("\$写文件 ([^\$]*) ([^\$]*)\$", re.findall, priority=1)
访问 = Matcher("\$访问 ([^\$]+?)(?: ([^\$]+?))?(?: ([^\$]+?))?(?: ([^\$]+?))?\$", re.findall, priority=1)
循环 = Matcher("\n\s*循环(.*)", re.findall, priority=1)
调用 = Matcher("\$调用 ([^\$]+?)(?: #([^\$]+?))?\$", re.findall, priority=1)

变量调用 = Matcher("(?<!\\\\)%((?:[^\\\\%]|\\\\.)*)(?<!\\\\)%", re.findall, priority=3)
json转译 = Matcher("@%([^%]*)%#(.*)",re.findall,priority=2)
计算 = Matcher("\$计算 \[([^\$]*)\]\$",re.findall,priority=1)

如果1 = Matcher("\n\s*如果(.*)(==|>=|<=|>|<|!=)(.*)", re.findall, priority=1)
如果2 = Matcher("\n\s*另如果(.*)(==|>=|<=|>|<|!=)(.*)", re.findall, priority=1)

否则 = Matcher("\n\s*否则", re.findall, priority=1)
返回 = Matcher("\n\s*返回(.*)",re.findall,priority=1)

# 2. 用 @xxx.handle() 装饰异步处理函数
@发送.handle()
async def _(text,line):
    for test_data in text:
        msg = await convert_message_string(test_data)
        msg = await safe_value(msg)
        line =line.replace(f'$发送 {test_data}$', f"await send(bot,event,{msg})")
    return line

@读文件.handle()
async def _(text,line):
    for test_data in text:
        line = line.replace(f'$读文件 {test_data[0]} {test_data[1]} {test_data[2]}$', f"await read_txt({await safe_value(test_data[0])},{await safe_value(test_data[2])},{await safe_value(test_data[1])})")
    return line

@写文件1.handle()
async def _(text,line):
    for test_data in text:
        line = line.replace(f'$写文件 {test_data[0]} {test_data[1]} {test_data[2]}$', f"await write_txt({await safe_value(test_data[0])},{await safe_value(test_data[2])},{await safe_value(test_data[1])})")
    return line

@写文件2.handle()
async def _(text,line):
    for test_data in text:
        line = line.replace(f'$写文件 {test_data[0]} {test_data[1]}$', f"await write_txt({await safe_value(test_data[0])},{await safe_value(test_data[1])})")
    return line

@访问.handle()
async def _(text,line):
    for test_data in text:
        url = test_data[0]
        method = test_data[1] if len(test_data) > 1 else 'get'
        headers = test_data[2] if len(test_data) > 2 else None
        upjson = test_data[3] if len(test_data) > 3 else None
        line = line.replace(f'$访问 {url} {method} {headers} {upjson}$', f"await get_url({await safe_value(url)}, method='{method}', headers={headers}, upjson={upjson})")
        line = line.replace(f'$访问 {url} {method} {headers}$', f"await get_url({await safe_value(url)}, method='{method}', headers={headers})")
        line = line.replace(f'$访问 {url} {method}$', f"await get_url({await safe_value(url)}, method='{method}')")
        line = line.replace(f'$访问 {url}$', f"await get_url({await safe_value(url)})")
    return line

@循环.handle()
async def _(text,line):
    for test_data in text:
        line = line.replace(f'循环{test_data}', f'while {test_data}:')
    return line

@调用.handle()
async def _(text,line):
    for test_data in text:
        fun_name = f"有参{test_data[0]}" if len(test_data[1]) > 0 else f"无参{test_data[0]}"
        can_list = str(test_data[1]).split("#")
        res_can = ''
        for can in can_list if len(test_data[1]) > 0 else []:
            if deng := re.match(r"(.*)=(.*)",can):
                res_can += f",{deng.groups()[0]}={await safe_value(deng.groups()[1] if len(deng.groups()[1])>0 else ' ')}" 
            else:
                res_can += f",f'{can}'" 
        line = line.replace(f'$调用 {test_data[0]}$',f"await {fun_name}(bot,event,regex_group)")
        line = line.replace(f'$调用 {test_data[0]} #{test_data[1]}$',f"await {fun_name}(bot,event,regex_group{res_can})")
    return line

@变量调用.handle() 
async def _(text,line):
    for test_data in text:
        if test_data == "QQ":
            line = line.replace(f"%QQ%", '{getattr(event, "user_id", None) or (event.get_user_id() if hasattr(event, "get_user_id") else None) or " "}')
        elif test_data == "群号":
            line = line.replace(f"%群号%", '{getattr(event, "group_id", None) or getattr(event, "group_openid", None) or " "}')
        elif test_data == "昵称":
            line = line.replace(f"%昵称%", '{await get_sender_name(event)}')
        else:
            line = line.replace(f"%{test_data}%", f'{{locals().get("{test_data}", " ")}}')
    return line

@json转译.handle()
async def _(text,line):
    for test_data in text:
        key = test_data[0]
        value = f'SafeGetter(locals().get("{key}", " "))'
        value_data = test_data[1].split('#')
        for res in value_data:
            value += f'.get({await safe_value(res)}," ")'
        value+='.value()'
        line = line.replace(f"@%{key}%#{test_data[1]}",value)
    return line

@计算.handle()
async def _(text,line):
    for test_data in text:
        res = await extract_and_split(f'[{test_data}]')
        for i in res:
            i = await list_to_number(i)
            line = line.replace(f'$计算 [{test_data}]$', i)
    return line

@如果1.handle()
async def _(text,line):
    for test_data in text:
        line = line.replace(f'如果{test_data[0]}{test_data[1]}{test_data[2]}', f'if {test_data[0]}{test_data[1]}{test_data[2]}:')
    return line

@如果2.handle()
async def _(text,line):
    for test_data in text:
        line = line.replace(f'另如果{test_data[0]}{test_data[1]}{test_data[2]}', f'elif {test_data[0]}{test_data[1]}{test_data[2]}:')
    return line

@否则.handle()
async def _(text,line):
    for test_data in text:
        line = line.replace(f'否则', f'else:')
    return line

@返回.handle()
async def _(text,line):
    for test_data in text:
        line = line.replace(f'返回{test_data}',f'return {test_data}')
    return line