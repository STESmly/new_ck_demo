import re

from nonebot.adapters.onebot.v11 import Bot as botv11, PrivateMessageEvent, GroupMessageEvent,MessageSegment as send_method_v11
from nonebot.adapters.qq import Bot as botqq, GroupMessageCreateEvent,C2CMessageCreateEvent,MessageSegment as send_method_qq
from nonebot.adapters.qq.models.common import MessageMarkdown, MessageMarkdownParams, MessageKeyboard, InlineKeyboard, InlineKeyboardRow, Button, RenderData, Action, Permission

from nonebot.adapters import Bot

class SafeGetter:
    def __init__(self, data):
        self._data = data

    def get(self, key, default=None):

        data = self._data

        if isinstance(key, str) and isinstance(data, dict):
            val = data.get(key, default)
        elif isinstance(key, int) and isinstance(data, list):
            try:
                val = data[key]
            except IndexError:
                val = default
        else:
            val = default

        return SafeGetter(val)

    def value(self):
        return self._data

def cqcode_to_json(platfrom,message_str: str) -> str:

    pattern = re.compile(r"(.*?)\[CQ:([a-zA-Z0-9]+)(.*?)(?<!\\)\]", re.DOTALL)

    segments = []
    last_end = 0

    for match in pattern.finditer(message_str):
        text_before = match.group(1)
        if text_before:
            segments.append({
                "type": "text",
                "data": {"text"if platfrom == "OneBot V11" else "content": text_before.replace('&#91;', '[').replace('&#93;',']')}
            })
        
        cq_type = match.group(2)
        params_str = match.group(3)
        
        params = {}
        if params_str:

            for param in params_str.lstrip(',').split(','):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value

        segments.append({
            "type": cq_type,
            "data": params
        })
        last_end = match.end()


    remaining_text = message_str[last_end:]
    if remaining_text:
        segments.append({
            "type": "text",
            "data": {"text"if platfrom == "OneBot V11" else "content": remaining_text.replace('&#91;', '[').replace('&#93;',']')}
        })

    return segments

def qq_at_user(id):
    return f'<qqbot-at-user id="{id}"/>'

def md_msg_v11(text:str=None,**kargs):
    if msg:=kargs.get("content"):
        return send_method_v11.text(msg)
    return send_method_v11.text(text)

def md_msg_qq(markdown:str=None,**kargs):
    if msg:=kargs.get("content"):
        return send_method_qq.markdown(msg)
    return send_method_qq.markdown(markdown)

def at_id_v11(user_id = None,**kargs):
    if id:=kargs.get("id"):
        return send_method_v11.at(id)
    return send_method_v11.at(user_id)

PLATFORM_ADAPTERS = {
    'OneBot V11': {
        'at': at_id_v11,
        'image': send_method_v11.image,
        'reply': send_method_v11.reply,
        'text':send_method_v11.text
    },
    'QQ': {
        'at': qq_at_user,
        'image': 'image',
        'reply': 'reply',
        'md':md_msg_qq
    },
}

async def get_sender_name(event) -> str:
    sender = getattr(event, "sender", None)
    if sender is not None:
        card = getattr(sender, "card", None)
        if card and card.strip():
            return card
        nickname = getattr(sender, "nickname", None)
        if nickname and nickname.strip():
            return nickname

    author = getattr(event, "author", None)
    if author is not None:
        username = getattr(author, "username", None)
        if username and username.strip():
            return username

    return " "

def buildmsg(platform,cq_json:dict):
    print(cq_json)
    cq_type = cq_json.get("type",False)
    cq_data = cq_json.get("data",False)
    mapping:dict = PLATFORM_ADAPTERS.get(platform, False)
    if cq_type and mapping:
        method = mapping.get(cq_type,md_msg_v11 if platform == "OneBot V11"else send_method_qq.text)
        return method(**cq_data)


async def send(bot: Bot, event, cqcode: str, *args, **kwargs) -> None:
    platform = bot.adapter.get_name()
    cq_json: list = cqcode_to_json(platform, cqcode)

    # ------------------ QQ 平台特殊处理（含 md 类型时合并） ------------------
    if platform == "QQ":
        has_md = any(seg.get("type") == "md" for seg in cq_json)
        if has_md:
            merged_parts = []          # 寄存器：存储 text/md/at 的合并内容
            other_segments = []        # 存储其他类型的消息段

            for seg in cq_json:
                typ = seg.get("type")
                data = seg.get("data", {})

                if typ == "text":
                    merged_parts.append(data.get("content", ""))
                elif typ == "md":
                    merged_parts.append(data.get("content", ""))
                elif typ == "at":
                    # 适配不同字段名（CQ 码中通常为 "qq"）
                    user_id = data.get("qq") or data.get("id") or ""
                    merged_parts.append(qq_at_user(user_id))
                else:
                    # 其他类型（image, file 等）直接构建
                    other_segments.append(buildmsg(platform, seg))

            # 合并所有寄存器内容为一个 Markdown 段
            md_content = "".join(merged_parts)
            md_segment = md_msg_qq(md_content)

            # 最终消息 = Markdown 段 + 其他段
            final_msg = md_segment
            for seg in other_segments:
                final_msg += seg

            await bot.send(event, final_msg)
            return

    # ------------------ 通用逻辑（非 QQ 平台 或 QQ 平台无 md 段） ------------------
    msg = None
    for seg_data in cq_json:
        seg = buildmsg(platform, seg_data)
        if msg is None:
            msg = seg
        else:
            msg += seg
    await bot.send(event, msg)
