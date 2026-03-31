"""
任务定义
"""

from utils.logger_handler import logger

def add_timer_prompt(timer_prompt: str):
    from ding.robot_service import ding_bot_service
    from agent.main_agent import main_agent
    try:
        res = main_agent.get_reply(timer_prompt)
        ding_bot_service.send_group_message(res)
    except Exception as e:
        logger.error(f"[添加定时指令]错误：{str(e)}")