
import os
from langchain_core.tools import tool

from scheduler.jobs.job_def import add_timer_prompt
from utils.logger_handler import logger
from utils.scrape.cnmo_news_scraper import cnmo_news_scraper
from scheduler.scheduler_manager import scheduler

@tool(description="获取文本文件内容，输入参数为文件路径")
def read_str_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        logger.error(f"[read_str_file]{file_path}文件不存在")
        return f"{file_path}文件不存在"
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()



@tool(description="生成Markdown报告，传入参数为报告路径，和报告具体内容")
def generate_report(md_path: str, content: str):
    if os.path.exists(md_path):
        logger.error(f"[generate_report]{md_path}已存在")
        return f"{md_path}文件已存在，尝试重命名后再重试"
    try:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"[generate_report]写入报告发生错误{str(e)}")
        return f"[generate_report]写入报告发生错误{str(e)},停止生成"
    return f"成功生成报告：{md_path}"

@tool(description="发送钉钉群组消息,参数为会话id和封装的dict消息")
def send_group_message(conversation_id: str, msg_param: dict):
    from ding.robot_service import ding_bot_service
    return ding_bot_service.send_group_message(conversation_id, msg_param)

@tool(description="发送钉钉私聊消息,参数为用户id列表和封装的dict消息")
def send_private_message(user_id_list: list[str], msg_param: dict):
    from ding.robot_service import ding_bot_service
    return ding_bot_service.send_private_message(user_id_list, msg_param)

@tool(description="获取用户信息")
def get_user_info():
    from ding.robot_service import ding_bot_service
    return ding_bot_service.get_cur_user_info()

@tool(description="获取最新手机相关新闻, 参数为新闻条数，默认为5条")
def get_phone_news(max_news: int=5):
    res = cnmo_news_scraper.scrape_batch(max_news=max_news, delay=0.5)
    return res

@tool(description="获取定时任务列表")
def get_timer_task_list():
    job_list = scheduler.list_jobs()
    return job_list

@tool(description="添加定时任务")
def add_timer_task(cron_expr: str, job_id: str, name: str, timer_prompt: str):
    try:
        scheduler.add_cron_job(
            add_timer_prompt,
            cron_expr=cron_expr,
            job_id=job_id,
            name=name,
            kwargs={
                "timer_prompt": timer_prompt
            }
        )
        return f"成功添加定时任务：{name},执行时间：{cron_expr}, 指令：{timer_prompt}"
    except Exception as e:
        logger.error(f"[add_timer_task]添加定时任务发生错误{str(e)}")
        return f"添加定时任务：{name}发生错误:{str(e)}"


@tool(description="移除定时任务")
def remove_timer_task(job_id: str):
    try:
        scheduler.remove_job(job_id)
        return f"成功移除定时任务{job_id}"
    except Exception as e:
        logger.error(f"[remove_timer_task]移除定时任务{job_id}失败：{str(e)}")
        return f"移除定时任务{job_id}失败：{str(e)}"
