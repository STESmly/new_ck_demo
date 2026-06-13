import re
from pathlib import Path
import os, asyncio

data_dir = Path(__file__).parent.parent / "词库插件"

ck_path = data_dir / "词库文件"

async def get_text(file_path):
    result = []
    if not os.path.exists(file_path):
        open(file_path, 'w', encoding='utf-8').close()
    with open(file_path, 'r', encoding='utf-8') as f:
        txt_res = f.read()
        parts = re.split('\n\n\n|\n\n', txt_res)
        for part in parts:
            if len(part) > 0:
                data = re.split('\n', part)
                zhiling = data[0]
                code = data[1:] if len(data) > 1 else []
                result.append({
                    "指令": zhiling,
                    "代码": code,
                })
    return result

async def get_all_text():
    all_text = []
    try:
        for file_name in os.listdir(ck_path):
            if file_name.endswith('.ck'):
                file_path = os.path.join(ck_path, file_name)
                txt_finall_res = await get_text(file_path)
                result = {
                    "文件名": file_name[:-3],
                    "内容": txt_finall_res
                }
                all_text.append(result)

        return all_text

    except FileNotFoundError:
        ck_path.mkdir(parents=True, exist_ok=True)
        open(ck_path / "dicpro.ck", 'w', encoding='utf-8').close()
    return None

async def fix_tab(code: list):
    tab_time = 0
    while_try_time = 0
    result = []
    break_type = False
    for line in code:
        if re.match(r'^如果(.*)(==|>=|<=|>|<|!=)(.*)$', line):
            line = '    ' * tab_time + line
            tab_time += 1
        elif re.match(r'^另如果.*$', line):
            line = '    ' * tab_time + line
            tab_time += 1
        elif re.match(r'^否则.*$', line):
            line = '    ' * tab_time + line
            tab_time += 1
        elif res :=re.match(r'^循环(.*)$', line):
            data = res.groups()
            if data[0] != "尾":
                result.append('    '*tab_time + 'try:')
                result.append('    ' * (tab_time+1) + f'循环{data[0].replace("%","")}')
                line = '    '*(tab_time+2)+'await asyncio.sleep(0)'
                break_type = True
                tab_time += 2
                while_try_time += 1
            elif break_type:
                line = '    ' * tab_time + 'break'
                break_type = False
                tab_time -= 1
            else:
                continue
        elif re.match(r'^如果尾$', line):
            if tab_time > 0:
                tab_time -= 1
                continue
            else:
                continue
        else:
            line = '    ' * tab_time + line
        result.append(line)
    if break_type:
        for i in range(0,while_try_time):
            result.append('    '*tab_time + 'if _should_exit_loop:')
            result.append('    ' * (tab_time+1) + 'break')
            break_type = False
            tab_time -= 2
            result.append('    '*tab_time + 'except asyncio.CancelledError:')
            result.append('    '* (tab_time+1)+'print("[Plugin] Loop cancelled")')
            result.append('    '*(tab_time+1)+'raise')
    else:
        for i in range(0,while_try_time):
            result.append('    '*(tab_time+1) + 'if _should_exit_loop:')
            result.append('    ' * (tab_time+2) + 'break')
            tab_time -= 2
            result.append('    '*(tab_time+1) + 'except asyncio.CancelledError:')
            result.append('    '* (tab_time+2)+'print("[Plugin] Loop cancelled")')
            result.append('    '*(tab_time+2)+'raise')
    return result
    

async def build_ciku():
    all_text : list = await get_all_text()
    res = """from nonebot import on_regex
from nonebot.params import RegexGroup
from nonebot.adapters.onebot.v11 import Bot as botv11, PrivateMessageEvent, GroupMessageEvent,MessageSegment as send_method_v11
from nonebot.adapters.qq import Bot as botqq, GroupMessageCreateEvent,C2CMessageCreateEvent,MessageSegment as send_method_qq
from nonebot.adapters.qq.models.common import MessageMarkdown, MessageMarkdownParams, MessageKeyboard, InlineKeyboard, InlineKeyboardRow, Button, RenderData, Action, Permission
from ..basic_method import *
from ..adapters_method import *
import asyncio
from nonebot import get_driver

_should_exit_loop = False

def set_exit_flag():
    global _should_exit_loop
    _should_exit_loop = True
    print("[Plugin] Exit flag set")

driver = get_driver()

@driver.on_shutdown
async def shutdown_handler():
    print("[Plugin] Shutdown triggered, exiting loop...")
    set_exit_flag()
"""
    back = []
    for item in all_text:
        codes = item["内容"]
        for code in codes:
            code_res = await fix_tab(code["代码"])
            res += "\n\n"
            if ma:=re.match('^\[内部\](.*)\[(.*)\]$',code['指令']):
                can = ma.groups()
                canshu = can[1].split(" ")
                can_list = ""
                can_list = ",".join(canshu)
                res += f"\nasync def 有参{can[0]}(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...],{can_list}):\n"
                for line in code_res:
                    res += f"    {line}\n"
            elif ma:=re.match('^\[内部\](.*)$',code['指令']):
                res += f"\nasync def 无参{ma.groups()[0]}(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...]):\n"
                for line in code_res:
                    res += f"    {line}\n"
            else:

                res += f"{code['指令']} = on_regex(r'^{code['指令']}$')\n"
                res += f"@{code['指令']}.handle()"
                res += f"\nasync def {code['指令']}(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):\n"
                for line in code_res:
                    res += f"    {line}\n"
        back.append(
            {
                "文件名": item["文件名"],
                "内容": res
            }
        )
    return back