
from ding.robot_service import ding_bot_service
from scheduler import scheduler, init_scheduler_from_config

if __name__ == '__main__':
    # 启动定时任务调度器
    init_scheduler_from_config()
    scheduler.start()

    # 列出所有任务
    print("=== 当前定时任务 ===")
    for job in scheduler.list_jobs():
        print(f"  - {job['name']}: {job['next_run_time']}")


    # 启动钉钉服务
    ding_bot_service.run_bot_listen_server()