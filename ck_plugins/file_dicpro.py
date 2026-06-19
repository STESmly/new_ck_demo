from nonebot import on_regex
from nonebot.params import RegexGroup
from nonebot.adapters.onebot.v11 import Bot as botv11, PrivateMessageEvent, GroupMessageEvent,MessageSegment as send_method_v11
from nonebot.adapters.qq import Bot as botqq, GroupMessageCreateEvent,C2CMessageCreateEvent,MessageSegment as send_method_qq
from nonebot.adapters.qq.models.common import MessageMarkdown, MessageMarkdownParams, MessageKeyboard, InlineKeyboard, InlineKeyboardRow, Button, RenderData, Action, Permission
from ..basic_method import *
from ..adapters_method import *
from ..html_render import *
import asyncio


指令_670d9743542cae3ea7ebe36af56bd53648b0a1126162e78d81a32934a711302e = on_regex(r'^你好$')
@指令_670d9743542cae3ea7ebe36af56bd53648b0a1126162e78d81a32934a711302e.handle()
async def 指令_670d9743542cae3ea7ebe36af56bd53648b0a1126162e78d81a32934a711302e(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
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


指令_c90a1cdb561d0269284d52e41013bb2bd68e3b61e186db87e03ebced48b00d60 = on_regex(r'^再见$')
@指令_c90a1cdb561d0269284d52e41013bb2bd68e3b61e186db87e03ebced48b00d60.handle()
async def 指令_c90a1cdb561d0269284d52e41013bb2bd68e3b61e186db87e03ebced48b00d60(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
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
                raise
            if _should_exit_loop:
                break
    except asyncio.CancelledError:
        raise


指令_d6d7b36504d7ed6cb86cfbac611a5764e6c1f89dae9d0318a8077034e220f23d = on_regex(r'^访问测试$')
@指令_d6d7b36504d7ed6cb86cfbac611a5764e6c1f89dae9d0318a8077034e220f23d.handle()
async def 指令_d6d7b36504d7ed6cb86cfbac611a5764e6c1f89dae9d0318a8077034e220f23d(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
    res = await get_url(f'http://110.41.8.213:8000/api/emojis/list', method='get')
    data = SafeGetter(locals().get("res", " ")).get(f'files'," ").value()
    kd_data = {
      "rows": [
        {
          "buttons": [
            {
              "id": "btn_1781433837842",
              "render_data": {
                "label": "按钮",
                "visited_label": "以按",
                "style": 1
              },
              "action": {
                "type": 1,
                "data": "777888",
                "permission": {
                  "type": 2
                },
                "reply": True,
                "enter": True
              }
            }
          ]
        }
      ]
    }
    await send(bot,event,f'{locals().get("data", " ")}[CQ:md,content=\n#你好][CQ:at,id={getattr(event, "user_id", None) or (event.get_user_id() if hasattr(event, "get_user_id") else None) or " "}][CQ:kd,content={locals().get("kd_data", " ")}]')
    await 无参_670d9743542cae3ea7ebe36af56bd53648b0a1126162e78d81a32934a711302e(bot,event,regex_group)


指令_6aa8f49cc992dfd75a114269ed26de0ad6d4e7d7a70d9c8afb3d7a57a88a73ed = on_regex(r'^测试$')
@指令_6aa8f49cc992dfd75a114269ed26de0ad6d4e7d7a70d9c8afb3d7a57a88a73ed.handle()
async def 指令_6aa8f49cc992dfd75a114269ed26de0ad6d4e7d7a70d9c8afb3d7a57a88a73ed(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
    a1 = 2
    a2 = 8
    a3 = 7788
    a=(a3*(a1+a2*a3))


指令_ca25a0959a916c2302dca7dabdaadc03e29e06b137c0f602807bcc2722d469ff = on_regex(r'^括号测试([\s\S]*)$')
@指令_ca25a0959a916c2302dca7dabdaadc03e29e06b137c0f602807bcc2722d469ff.handle()
async def 指令_ca25a0959a916c2302dca7dabdaadc03e29e06b137c0f602807bcc2722d469ff(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
    a = regex_group[0] if regex_group else None
    await send(bot,event,f'{locals().get("a", " ")}')


指令_dbaa4e780e2bdf13dc44193e669fdc5a2618c1fa67b4b54eec849a0b06e4f3ca = on_regex(r'^测试md([\s\S]*)#([\s\S]*)$')
@指令_dbaa4e780e2bdf13dc44193e669fdc5a2618c1fa67b4b54eec849a0b06e4f3ca.handle()
async def 指令_dbaa4e780e2bdf13dc44193e669fdc5a2618c1fa67b4b54eec849a0b06e4f3ca(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
    a = await inline_kb_md(f'{regex_group[0] if regex_group else None}',f'{regex_group[1] if regex_group else None}')
    await send(bot,event,f'[CQ:md,content={locals().get("a", " ")}]')


指令_bd1be381427c9a6212fe4e0ef7d998b455898bf1ea31b1ebcb9334e014950d1e = on_regex(r'^网页图测试(.*)$')
@指令_bd1be381427c9a6212fe4e0ef7d998b455898bf1ea31b1ebcb9334e014950d1e.handle()
async def 指令_bd1be381427c9a6212fe4e0ef7d998b455898bf1ea31b1ebcb9334e014950d1e(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
    a = await html_to_png(f'{regex_group[0] if regex_group else None}', 1080,1080)
    await send(bot,event,f'[CQ:img,url={locals().get("a", " ")}]')


指令_526b0fd4493eb5d4cd7e5ac5219b75313fcbabb8fb9f0e51a9f534bbe6aacb9c = on_regex(r'^调用测试$')
@指令_526b0fd4493eb5d4cd7e5ac5219b75313fcbabb8fb9f0e51a9f534bbe6aacb9c.handle()
async def 指令_526b0fd4493eb5d4cd7e5ac5219b75313fcbabb8fb9f0e51a9f534bbe6aacb9c(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...] = RegexGroup()):
    await 无参_670d9743542cae3ea7ebe36af56bd53648b0a1126162e78d81a32934a711302e(bot,event,regex_group)
    await 有参_670d9743542cae3ea7ebe36af56bd53648b0a1126162e78d81a32934a711302e(bot,event,regex_group,f'测试',参数2=f'长沙市')



async def 无参_670d9743542cae3ea7ebe36af56bd53648b0a1126162e78d81a32934a711302e(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...]):
    a="""**加粗**\n__下划线加粗__"""
    b="""
    **加粗**
    __下划线加粗__
    _斜体_
    *星号斜体*
    ***加粗斜体***
    ~~删除线~~
    """
    await send(bot,event,f'[CQ:md,content=#调用测试{locals().get("a", " ")}]')
    await send(bot,event,f'[CQ:md,content=#区别{locals().get("b", " ")}]')



async def 有参_670d9743542cae3ea7ebe36af56bd53648b0a1126162e78d81a32934a711302e(bot: botv11 | botqq, event: PrivateMessageEvent|GroupMessageEvent|GroupMessageCreateEvent|C2CMessageCreateEvent, regex_group: tuple[str, ...],参数1,参数2):
    a=2
    return  a, a
