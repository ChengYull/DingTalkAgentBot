
from utils.config_handler import prompt_conf
from utils.logger_handler import logger
from utils.path_handler import get_abs_path


def load_system_prompt():
    try:
        sys_prompt_path = get_abs_path(prompt_conf["system_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompt]在Yml配置中，没有找到system_prompt_path项")
        raise e
    try:
        return open(sys_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_prompt]读取system_prompt出现错误：{e}")
        raise e

