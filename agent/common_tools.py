import os
import json
from langchain_core.tools import tool

@tool(description="获取文件夹中的文件列表，参数为文件夹路径")
def get_file_list(dir: str) -> str:
    if os.path.isdir(dir):
        file_list = os.listdir(dir)
    else:
        return f"目标文件夹{dir}不存在"
    return json.dumps({
        "dir": dir,
        "files": file_list
    })


@tool(description="获取当前系统时间，返回格式化时间字符串, 返回格式：YYYY-MM-DD HH:MM:SS")
def get_current_time() -> str:
    """
    获取当前系统时间
    返回格式：YYYY-MM-DD HH:MM:SS
    """
    from datetime import datetime

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time