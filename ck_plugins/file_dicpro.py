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


你好 = on_regex(r'^你好$')
@你好.handle()
async def 你好(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
    res = await get_url(f'http://110.41.8.213:8000/api/emojis/list?n={{\'data\':7789}}', method='get')
    cs = '你好'
    if  cs == '你好':
        await send(bot,event,f'{getattr(event, "user_id", None) or (event.get_user_id() if hasattr(event, "get_user_id") else None) or " "}')
        await send(bot,event,f'{getattr(event, "group_id", None) or getattr(event, "group_openid", None) or " "}')
        await send(bot,event,f'{await get_sender_name(event)}')
    elif  cs == 7788:
        await send(bot,event,f'{locals().get("res", " ")}')
        await write_txt(f'测试',f'{locals().get("res", " ")}',f'a')
    else:
        await send(bot,event,f'{locals().get("晚上", " ")}')


再见 = on_regex(r'^再见$')
@再见.handle()
async def 再见(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
    i = 0
    data = await read_txt(777,111,455)
    try:
        while (i := i + data) < 5:
            await asyncio.sleep(0)
            await send(bot,event,666)
            try:
                while True:
                    await asyncio.sleep(0)
                    if _should_exit_loop:
                        break
            except asyncio.CancelledError:
                print("[Plugin] Loop cancelled")
                raise
            if _should_exit_loop:
                break
    except asyncio.CancelledError:
        print("[Plugin] Loop cancelled")
        raise


访问测试 = on_regex(r'^访问测试$')
@访问测试.handle()
async def 访问测试(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
    res = await get_url(f'http://110.41.8.213:8000/api/emojis/list', method='get')
    data = SafeGetter(locals().get("res", " ")).get(f'files'," ").value()
    await send(bot,event,f'{locals().get("data", " ")}[CQ:md,content=\n#你好][CQ:at,id={getattr(event, "user_id", None) or (event.get_user_id() if hasattr(event, "get_user_id") else None) or " "}]')


测试 = on_regex(r'^测试$')
@测试.handle()
async def 测试(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
    a1 = 2
    a2 = 8
    a3 = 7788
    a=(a3*(a1+a2*a3))


调用测试 = on_regex(r'^调用测试$')
@调用测试.handle()
async def 调用测试(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
    await 无参你好(bot,event,regex_group)
    await 有参你好(bot,event,regex_group,f'测试',参数2=f'长沙市')



async def 无参你好(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...]):
    a=1



async def 有参你好(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...],参数1,参数2):
    a=2
    return  a, {locals().get("a", " ")}
