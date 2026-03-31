"""
定时任务管理器
"""
import os
from typing import Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from utils.logger_handler import logger
from utils.path_handler import get_abs_path
from utils.config_handler import load_config


class SchedulerManager:
    """定时任务管理器"""

    def __init__(self):
        self.scheduler = BackgroundScheduler(
            jobstores={'default': MemoryJobStore()},
            executors={
                'default': ThreadPoolExecutor(10),
                'processpool': ThreadPoolExecutor(5)
            },
            job_defaults={
                'coalesce': False,
                'max_instances': 3,
                'misfire_grace_time': 300  # 任务错过执行时间后，5分钟内仍会补执行
            }
        )
        self._running = False

    def start(self):
        """启动调度器"""
        if not self._running:
            self.scheduler.start()
            self._running = True
            logger.info("定时任务调度器已启动")

    def shutdown(self, wait: bool = True):
        """停止调度器"""
        if self._running:
            self.scheduler.shutdown(wait=wait)
            self._running = False
            logger.info("定时任务调度器已停止")

    def add_interval_job(
        self,
        func: Callable,
        seconds: Optional[int] = None,
        minutes: Optional[int] = None,
        hours: Optional[int] = None,
        job_id: str = None,
        name: str = None,
        **kwargs
    ):
        """
        添加间隔任务

        :param func: 任务函数
        :param seconds: 间隔秒数
        :param minutes: 间隔分钟数
        :param hours: 间隔小时数
        :param job_id: 任务ID
        :param name: 任务名称
        """
        trigger_kwargs = {}
        if seconds:
            trigger_kwargs['seconds'] = seconds
        if minutes:
            trigger_kwargs['minutes'] = minutes
        if hours:
            trigger_kwargs['hours'] = hours

        if not trigger_kwargs:
            raise ValueError("必须指定 seconds、minutes 或 hours 之一")

        job = self.scheduler.add_job(
            func,
            IntervalTrigger(**trigger_kwargs),
            id=job_id,
            name=name or job_id,
            replace_existing=True,
            **kwargs
        )
        logger.info(f"添加间隔任务成功: {job_id}, 间隔: {trigger_kwargs}")
        return job

    def add_cron_job(
        self,
        func: Callable,
        cron_expr: str = None,
        year: int = None,
        month: int = None,
        day: int = None,
        hour: int = None,
        minute: int = None,
        second: int = None,
        day_of_week: str = None,
        job_id: str = None,
        name: str = None,
        **kwargs
    ):
        """
        添加Cron任务

        :param func: 任务函数
        :param cron_expr: Cron表达式 (如 "0 9 * * *" 表示每天9点)
        :param year: 年
        :param month: 月
        :param day: 日
        :param hour: 时
        :param minute: 分
        :param second: 秒
        :param day_of_week: 星期 (0-6 或 mon,tue,wed,thu,fri,sat,sun)
        :param job_id: 任务ID
        :param name: 任务名称
        """
        if cron_expr:
            trigger = CronTrigger.from_crontab(cron_expr)
        else:
            trigger = CronTrigger(
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                second=second,
                day_of_week=day_of_week
            )

        job = self.scheduler.add_job(
            func,
            trigger,
            id=job_id,
            name=name or job_id,
            replace_existing=True,
            **kwargs
        )
        logger.info(f"添加Cron任务成功: {job_id}, 表达式: {cron_expr or f'{month}/{day} {hour}:{minute}:{second}'}")
        return job

    def add_date_job(
        self,
        func: Callable,
        run_date,
        job_id: str = None,
        name: str = None,
        **kwargs
    ):
        """
        添加一次性任务

        :param func: 任务函数
        :param run_date: 运行时间 (datetime 或 str)
        :param job_id: 任务ID
        :param name: 任务名称
        """
        job = self.scheduler.add_job(
            func,
            DateTrigger(run_date=run_date),
            id=job_id,
            name=name or job_id,
            replace_existing=True,
            **kwargs
        )
        logger.info(f"添加一次性任务成功: {job_id}, 运行时间: {run_date}")
        return job

    def remove_job(self, job_id: str):
        """删除任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"删除任务成功: {job_id}")
            return True
        except Exception as e:
            logger.error(f"删除任务失败: {job_id}, 错误: {e}")
            return False

    def pause_job(self, job_id: str):
        """暂停任务"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"暂停任务成功: {job_id}")
            return True
        except Exception as e:
            logger.error(f"暂停任务失败: {job_id}, 错误: {e}")
            return False

    def resume_job(self, job_id: str):
        """恢复任务"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"恢复任务成功: {job_id}")
            return True
        except Exception as e:
            logger.error(f"恢复任务失败: {job_id}, 错误: {e}")
            return False

    def get_job(self, job_id: str):
        """获取任务信息"""
        return self.scheduler.get_job(job_id)

    def list_jobs(self):
        """列出所有任务"""
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
            for job in jobs
        ]

    def is_running(self):
        """检查调度器是否运行"""
        return self._running


# 全局调度器实例
scheduler = SchedulerManager()


def load_scheduler_config():
    """加载定时任务配置"""
    config_path = get_abs_path("config/scheduler_config.yml")
    if os.path.exists(config_path):
        return load_config(config_path)
    return {}


def init_scheduler_from_config():
    """从配置文件初始化定时任务"""
    config = load_scheduler_config()
    jobs_config = config.get("jobs", [])

    for job_conf in jobs_config:
        if not job_conf.get("enabled", True):
            continue

        job_id = job_conf.get("id")
        job_type = job_conf.get("type")  # interval, cron, date
        job_func = job_conf.get("function")
        job_name = job_conf.get("name", job_id)

        # 获取任务函数
        func = _get_job_function(job_func)
        if not func:
            logger.warning(f"任务函数不存在: {job_func}, 跳过")
            continue

        # 根据类型添加任务
        if job_type == "interval":
            interval_conf = job_conf.get("interval", {})
            job_kwargs = job_conf.get("kwargs", {})
            scheduler.add_interval_job(
                func,
                seconds=interval_conf.get("seconds"),
                minutes=interval_conf.get("minutes"),
                hours=interval_conf.get("hours"),
                job_id=job_id,
                name=job_name,
                **job_kwargs
            )
        elif job_type == "cron":
            cron_conf = job_conf.get("cron", {})
            job_kwargs = job_conf.get("kwargs", {})
            scheduler.add_cron_job(
                func,
                cron_expr=cron_conf.get("expression"),
                job_id=job_id,
                name=job_name,
                kwargs=job_kwargs
            )

    logger.info(f"从配置加载了 {len(jobs_config)} 个定时任务")


def _get_job_function(func_path: str):
    """根据函数路径获取函数"""
    try:
        module_path, func_name = func_path.rsplit('.', 1)
        module = __import__(module_path, fromlist=[func_name])
        return getattr(module, func_name)
    except Exception as e:
        logger.error(f"获取任务函数失败: {func_path}, 错误: {e}")
        return None