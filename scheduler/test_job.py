"""
定时任务测试
每3秒打印一次，验证调度器是否正常工作
"""

import time
from scheduler import scheduler, load_scheduler_config
from scheduler.scheduler_manager import init_scheduler_from_config

# 测试任务：每3秒打印
def test_interval_task(info: str=""):
    """测试间隔任务"""
    print(f"[测试任务] {time.strftime('%Y-%m-%d %H:%M:%S')} - 定时任务执行中...  info: {info}")
    return "测试任务完成"


# 动态添加任务的函数
def add_job_interactive():
    """交互式添加任务"""
    job_type = input("任务类型 (1=cron, 2=interval): ")
    job_id = input("任务ID: ")
    job_name = input("任务名称: ")

    if job_type == "1":
        # Cron任务
        cron_expr = input("Cron表达式 (如 0 * * * *): ")
        scheduler.add_cron_job(
            test_interval_task,
            cron_expr=cron_expr,
            job_id=job_id,
            name=job_name,
            args=("test666666666666",)
        )
        print(f"添加Cron任务成功: {job_id}")
    else:
        # Interval任务
        seconds = int(input("间隔秒数: "))
        scheduler.add_interval_job(
            test_interval_task,
            seconds=seconds,
            job_id=job_id,
            name=job_name,
            args=("test666666666666",)
        )
        print(f"添加Interval任务成功: {job_id} (每{seconds}秒)")


# 重新加载配置文件的函数
def reload_config():
    """重新加载配置文件"""
    print("\n=== 重新加载配置文件 ===")
    init_scheduler_from_config()
    print("=== 重新加载后的任务列表 ===")
    for job in scheduler.list_jobs():
        print(f"  - {job['name']}: {job['next_run_time']}")


# 添加一个每3秒执行的任务
print("=== 添加测试任务：每3秒打印一次 ===")
scheduler.add_interval_job(
    test_interval_task,
    seconds=10,
    job_id="test_3s",
    name="测试-3秒间隔",
    kwargs={
        "info": "这是每3秒执行的任务信息"
    }
)

scheduler.add_cron_job(
    test_interval_task,
    cron_expr="41 10 * * *",
    job_id="test_cron",
    name="测试定时",
    kwargs={
        "info": "这是定时执行的任务信息"
    }
)

# 启动调度器
print("=== 启动定时任务调度器 ===")
scheduler.start()

# 列出所有任务
print("\n=== 当前定时任务列表 ===")
for job in scheduler.list_jobs():
    print(f"  任务: {job['name']}")
    print(f"  ID: {job['id']}")
    print(f"  下次执行: {job['next_run_time']}")
    print(f"  触发器: {job['trigger']}")

# 保持运行，提供交互菜单
print("=== 运行中 ===")
print("  输入 'a' - 动态添加任务")
print("  输入 'r' - 重新加载配置文件")
print("  输入 'l' - 列出所有任务")
print("  输入 'q' - 退出")
print()

try:
    while True:
        cmd = input("请输入命令: ").strip().lower()

        if cmd == 'a':
            add_job_interactive()
        elif cmd == 'r':
            reload_config()
        elif cmd == 'l':
            print("\n=== 当前任务列表 ===")
            for job in scheduler.list_jobs():
                print(f"  - {job['name']}: {job['next_run_time']}")
            print()
        elif cmd == 'q':
            break
        else:
            print("未知命令")

except KeyboardInterrupt:
    print("\n=== 停止调度器 ===")
    scheduler.shutdown()
    print("调度器已停止")