import json
import os

from sympy.core.evalf import get_abs

from utils.config_handler import memory_conf
from utils.logger_handler import logger
from utils.path_handler import get_abs_path


def load_memory_store(user_id: str, message_len: int = -1):
    """
    加载用户的对话历史
    :param user_id: 用户ID
    :param message_len: 加载的消息条数，默认为-1表示加载全部
    :return: 消息列表
    """
    # 这里可以从文件中加载用户的对话历史
    # 目前示例中直接返回一个空列表
    memory_dir = get_abs_path(memory_conf["memories_dir"])
    memory_path = os.path.join(memory_dir, f"{user_id}.json")
    if not os.path.exists(memory_path):
        # 不存在则创建一个空文件
        with open(memory_path, "w", encoding="utf-8") as f:
            f.write("[]")
        return []
    msg = []
    try:
        with open(memory_path, "r", encoding="utf-8") as f:
            msg = json.load(f)
    except Exception as e:
        logger.error(f"[load_memory]加载用户{user_id}的对话历史出现错误：{str(e)}")
        raise e

    return msg if (message_len == -1 or message_len >= len(msg)) else msg[-message_len:] # 只返回最后message_len条消息

def add_message_in_memory_store(user_id: str, new_message: dict):
    """
    添加新的消息到用户的对话历史中
    :param user_id: 用户ID
    :param new_message: 新消息的字典格式
    :return:
    """
    memory_dir = get_abs_path(memory_conf["memories_dir"])
    memory_path = os.path.join(memory_dir, f"{user_id}.json")
    if not os.path.exists(memory_path):
        # 不存在则创建一个空文件
        with open(memory_path, "w", encoding="utf-8") as f:
            f.write("[]")
    try:
        with open(memory_path, "r", encoding="utf-8") as f:
            msg = json.load(f)
        msg.append(new_message)
        with open(memory_path, "w", encoding="utf-8") as f:
            json.dump(msg, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"[add_new_message]添加新消息到用户{user_id}的对话历史出现错误：{str(e)}")
        raise e
