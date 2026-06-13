from nonebot import on_regex
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
