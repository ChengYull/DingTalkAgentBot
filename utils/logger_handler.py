import logging

import datetime
import os

from utils.config_handler import log_conf
from utils.path_handler import get_abs_path

# log保存根目录
LOGS_ROOT = get_abs_path(log_conf.get("logs_path", "logs"))

# 日志格式配置
DEFAULT_LOG_FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)

def get_logger(
        name: str = log_conf.get("log_name", "AGENT"),
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file = None
) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 避免重复添加Handler
    if logger.handlers:
        return logger

    # 控制台Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(console_handler)

    if not log_file:
        now_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = os.path.join(LOGS_ROOT, f"{name}_{now_str}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)
    return logger

# 获取日志器
logger = get_logger()

if __name__ == "__main__":
    logger.info(f"hello world")