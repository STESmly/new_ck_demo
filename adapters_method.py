import ast
import json
import re

from nonebot.adapters.onebot.v11 import Bot as botv11, PrivateMessageEvent, GroupMessageEvent,MessageSegment as send_method_v11
from nonebot.adapters.qq import Bot as botqq, GroupMessageCreateEvent,C2CMessageCreateEvent,MessageSegment as send_method_qq
from nonebot.adapters.qq.models.common import MessageMarkdown, MessageMarkdownParams, MessageKeyboard, InlineKeyboard, InlineKeyboardRow, Button, RenderData, Action, Permission

from nonebot.adapters import Bot
from .basic_method import file_path
from pathlib import Path

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

def cqcode_to_json(platfrom, message_str: str) -> list:
    """解析 CQ 码字符串为消息段列表，支持参数值内嵌套 []{}"""
    segments = []
    n = len(message_str)
    i = 0
    text_start = 0

    while i < n:
        # 查找 [CQ: 标记
        cq_start = message_str.find('[CQ:', i)
        if cq_start == -1:
            break

        # CQ 码之前的纯文本
        if cq_start > text_start:
            text = message_str[text_start:cq_start]
            if text:
                segments.append({
                    "type": "text",
                    "data": {
                        "text" if platfrom == "OneBot V11" else "content":
                        text.replace('&#91;', '[').replace('&#93;', ']')
                    }
                })

        # 开始解析 CQ 码
        pos = cq_start + 4  # 跳过 '[CQ:'

        # 读取 type（字母数字下划线）
        type_start = pos
        while pos < n and (message_str[pos].isalnum() or message_str[pos] == '_'):
            pos += 1
        cq_type = message_str[type_start:pos]

        # 解析参数 key=value，跟踪括号深度
        params = {}
        if pos < n and message_str[pos] == ',':
            pos += 1  # 跳过 type 后的逗号

        while pos < n:
            ch = message_str[pos]

            # CQ 码结束
            if ch == ']':
                pos += 1
                break

            # 跳过空白和逗号
            if ch in (' ', ','):
                pos += 1
                continue

            # 读取 key
            key_start = pos
            while pos < n and message_str[pos] not in '=,]\n':
                pos += 1
            key = message_str[key_start:pos].strip()

            if not key:
                continue

            if pos < n and message_str[pos] == '=':
                pos += 1  # 跳过 =

                # 读取 value（跟踪括号和引号深度）
                value_start = pos
                bracket_depth = 0
                brace_depth = 0
                in_single = False
                in_double = False

                while pos < n:
                    ch = message_str[pos]

                    # 字符串内：跳过转义，寻找引号结束
                    if in_double:
                        if ch == '\\' and pos + 1 < n:
                            pos += 2
                            continue
                        if ch == '"':
                            in_double = False
                        pos += 1
                        continue
                    if in_single:
                        if ch == '\\' and pos + 1 < n:
                            pos += 2
                            continue
                        if ch == "'":
                            in_single = False
                        pos += 1
                        continue

                    # 进入字符串
                    if ch == '"':
                        in_double = True
                        pos += 1
                        continue
                    if ch == "'":
                        in_single = True
                        pos += 1
                        continue

                    # 跟踪括号深度
                    if ch == '[':
                        bracket_depth += 1
                    elif ch == ']':
                        if bracket_depth == 0:
                            break  # CQ 码结束
                        bracket_depth -= 1
                    elif ch == '{':
                        brace_depth += 1
                    elif ch == '}':
                        brace_depth -= 1
                    elif ch == ',' and bracket_depth == 0 and brace_depth == 0:
                        break  # 参数分隔

                    pos += 1

                value = message_str[value_start:pos]
                params[key] = value.replace("&amp;","&")
            else:
                # 无 = 的独立标志参数
                params[key] = ''
                if pos < n and message_str[pos] == ',':
                    pos += 1

        segments.append({
            "type": cq_type,
            "data": params
        })

        text_start = pos
        i = pos

    # 末尾剩余纯文本
    if text_start < n:
        text = message_str[text_start:]
        if text:
            segments.append({
                "type": "text",
                "data": {
                    "text" if platfrom == "OneBot V11" else "content":
                    text.replace('&#91;', '[').replace('&#93;', ']')
                }
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

def img_msg_qq(url=None,**kargs):
    try:
        img_data = ast.literal_eval(url)
        return send_method_qq.file_image(img_data)
    except:
        if re.match(r'^https?://',url):
            return send_method_qq.image(url)
        else:
            return send_method_qq.file_image(Path(file_path.joinpath(url)))

def img_msg_v11(url=None,**kargs):
    try:
        img_data = ast.literal_eval(url)
        return send_method_v11.image(img_data)
    except:
        if re.match(r'^https?://',url):
            return send_method_v11.image(url)
        else:
            return send_method_v11.image(Path(file_path.joinpath(url)))

def kd_msg_qq(**kargs):
    content = kargs.get("content")
    # 解析为 dict：优先 Python 风格（单引号+True/False/None），兜底 JSON
    if isinstance(content, str):
        try:
            content = ast.literal_eval(content)
        except (ValueError, SyntaxError):
            content = json.loads(content)
    return send_method_qq.keyboard(MessageKeyboard(content=InlineKeyboard(**content)))

PLATFORM_ADAPTERS = {
    'OneBot V11': {
        'at': at_id_v11,
        'img': img_msg_v11,
        'text':send_method_v11.text
    },
    'QQ': {
        'at': qq_at_user,
        'img': img_msg_qq,
        'md':md_msg_qq,
        'kd':kd_msg_qq,
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
                    if "friend" in event.get_session_id():
                        continue
                    else:
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
