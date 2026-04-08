import time
from typing import Callable

from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langgraph.types import Command

from utils.logger_handler import logger
from utils.prompt_handler import load_system_prompt


@wrap_tool_call
def monitor_tool(
        # 请求的数据封装
        request: ToolCallRequest,
        # 执行的函数本身
        handler: Callable[[ToolCallRequest], ToolMessage | Command]
) -> ToolMessage | Command:
    """
    完成工具执行的监控
    :param request:
    :param handler: 工具执行器
    :return: 工具调用结果
    """
    logger.info(f"[tool_monitor]执行工具：{request.tool_call['name']}")
    logger.info(f"[tool_monitor]传入参数：{request.tool_call['args']}")

    try:

        start = time.time()
        # 执行工具
        result = handler(request)
        # 统计调用时间
        cost = time.time() - start

        logger.info(f"[tool_monitor]工具{request.tool_call['name']}调用成功,耗时：{cost}")
        logger.info(f"[tool_monitor]执行结果：{result}")

        return result

    except Exception as e:
        logger.error(f"[tool_monitor]工具调用{request.tool_call['name']}失败，原因：{str(e)}")
        raise e

@before_model
def log_befor_model(
        # 整个Agent智能体中的状态记录
        state: AgentState,
        # 记录了整个执行过程中的上下文信息
        runtime: Runtime
):
    """
    在模型执行前输出日志
    :param state:
    :param runtime:
    :return:
    """
    logger.info(f"[log_befor_model]带有{len(state['messages'])}条消息")
    # log输出最新一条消息的类型 与 内容
    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__} | {state['messages'][-1].content}")
    logger.debug(f"[log_befor_model] 完整消息：{state['messages']}")
    return None

@dynamic_prompt
def dynamic_prompt(
        request: ModelRequest
) -> str:
    """
    生成系统提示词之前调用此函数
    可以在这个函数中修改系统提示词
    :param request:
    :return: 提示词字符串
    """

    return load_system_prompt()
