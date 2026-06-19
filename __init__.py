import asyncio
import sys
from .读取词库 import build_ciku, data_dir,ck_path,logger
from .规则导入器 import Matcher as mod1
from pathlib import Path
import hashlib
from nonebot import load_plugin,get_driver
from watchfiles import awatch
from .keyboard_creator import *
py_path = data_dir / "ck_plugins"
hash_path = data_dir / "hashes"

if not py_path.exists():
    py_path.mkdir(parents=True, exist_ok=True)
    with open(py_path / "__init__.py", "w", encoding="utf-8") as f:
        f.write("from . import *")
if not hash_path.exists():
    hash_path.mkdir(parents=True, exist_ok=True)

data_dir_str = str(data_dir)
if data_dir_str not in sys.path:
    sys.path.insert(0, data_dir_str)

load_plugin(py_path)



def get_hash_value(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            content = f.read()
            
            return content
    except FileNotFoundError:
        return None
    
def save_hash_value(file_name, hash_value):
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(hash_value)

def compute_string_hash(content: str, algorithm: str = 'sha256', encoding: str = 'utf-8') -> str:
    """
    计算字符串内容的哈希值。

    :param content: 要计算哈希的原始字符串
    :param algorithm: 哈希算法，如 'md5', 'sha1', 'sha256'，默认 'sha256'
    :param encoding: 字符串编码方式，默认 'utf-8'
    :return: 十六进制的哈希字符串
    :raises ValueError: 不支持的哈希算法时抛出
    """
    try:
        hash_func = hashlib.new(algorithm)
    except ValueError as e:
        raise ValueError(f"不支持的哈希算法: {algorithm}") from e

    # 将字符串编码为字节数据后更新哈希对象
    hash_func.update(content.encode(encoding))
    return hash_func.hexdigest()

def compute_file_hash(file_path, algorithm='sha256', chunk_size=8192):
    """
    计算指定文件的哈希值。
    
    :param file_path: 文件路径
    :param algorithm: 哈希算法，支持 hashlib 中所有算法，如 'md5', 'sha1', 'sha256'
    :param chunk_size: 每次读取的字节数
    :return: 十六进制的哈希字符串
    :raises FileNotFoundError: 文件不存在时抛出
    :raises ValueError: 不支持的哈希算法时抛出
    """
    try:
        # 创建哈希对象
        hash_func = hashlib.new(algorithm)
    except ValueError as e:
        raise ValueError(f"不支持的哈希算法: {algorithm}") from e

    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_func.update(chunk)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在: {file_path}")
    except PermissionError:
        raise PermissionError(f"没有权限读取文件: {file_path}")
    
    return hash_func.hexdigest()

async def 编译词库(ciku_data:dict = None):
    
    res_data = await build_ciku()
    int_name = ""
    for item in res_data:
        data = await mod1.dispatch(item["内容"])
        hash_res = compute_string_hash(data)
        try:
            int(item['文件名'])
            hash_value = get_hash_value(f"{hash_path}/num_{item['文件名']}_hash.txt")
            if hash_res != hash_value:
                with open(f"{py_path}/num_{item['文件名']}.py", "w", encoding="utf-8") as f:
                    f.write(str(data))
                save_hash_value(f"{hash_path}/num_{item['文件名']}_hash.txt", hash_res)
            else:
                pass
            int_name += f"from . import num_{item['文件名']}\n"
        except Exception as e:
            hash_value = get_hash_value(f"{hash_path}/file_{item['文件名']}_hash.txt")
            if hash_res != hash_value:
                with open(f"{py_path}/file_{item['文件名']}.py", "w", encoding="utf-8") as f:
                    f.write(str(data))
                save_hash_value(f"{hash_path}/file_{item['文件名']}_hash.txt", hash_res)
            else:
                pass
            int_name += f"from . import file_{item['文件名']}\n"
    int_hash = compute_string_hash(int_name)
    int_hash_value = get_hash_value(f"{hash_path}/hash-int.txt")
    if int_hash != int_hash_value:
        with open(f"{py_path}/__init__.py", "w", encoding="utf-8") as f:
            f.write(int_name)
        save_hash_value(f"{hash_path}/hash-int.txt", int_hash)
    else:
        pass



WATCH_DIRECTORY = ck_path

async def on_ck_file_modified(file_path: str):
    """
    当 .ck 文件被修改时，在此异步函数中编写你需要执行的操作。
    该函数会在监测到修改事件后被异步调用。
    """
    logger.info(f"检测到文件已被修改: {file_path}")
    # TODO: 在这里添加你的异步业务逻辑（例如异步重新加载模型、触发训练等）
    asyncio.create_task(编译词库())


async def monitor_ck_files():
    """异步监测目录中所有 .ck 文件的修改事件"""
    logger.info(f"开始异步监测目录: {WATCH_DIRECTORY}")
    logger.info("监测所有 .ck 文件的修改事件，按 Ctrl+C 停止...")
    asyncio.create_task(编译词库())

    async for changes in awatch(WATCH_DIRECTORY):
        for change_type, file_path in changes:
            if change_type <=3 :
                if file_path.lower().endswith('.ck'):
                    await on_ck_file_modified(file_path)


driver = get_driver()

@driver.on_startup
async def file_monitor():
    asyncio.create_task(monitor_ck_files())