
from langchain.agents import create_agent
from threading import Lock

from model.model_factory import chat_model
from utils.config_handler import model_conf
from utils.memory_handler import add_message_in_memory_store, load_memory_store
from utils.prompt_handler import load_system_prompt
from agent.agent_tools import (read_str_file, generate_report,
                               send_group_message, send_private_message,
                               get_phone_news, get_timer_task_list,
                               add_timer_task, remove_timer_task,
                               add_date_timer_task, get_user_id_by_nick,
                               get_whole_chat_history)
from agent.common_tools import get_file_list, get_current_time
from agent.agent_middleware import dynamic_prompt, log_befor_model, monitor_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from datetime import datetime
# 用户会话最大历史记录数
MAX_HISTORY = model_conf["max_history"]
tavily_tool = TavilySearchResults(
    tavily_api_key="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",  # ← 直接在这里写
    max_results=5
)

class MainAgent:
    def __init__(self):
        self.tools = [
            get_file_list,
            read_str_file,
            generate_report,
            get_current_time,
            send_private_message,
            send_group_message,
            tavily_tool,
            get_phone_news,
            get_timer_task_list,
            add_timer_task,
            remove_timer_task,
            add_date_timer_task,
            get_user_id_by_nick,
            get_whole_chat_history
        ]
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompt(),
            tools=self.tools,
            middleware=[dynamic_prompt, log_befor_model, monitor_tool]
        )
        # 用户会话历史字典 {user_id: [messages]}
        self.user_sessions = {}
        self._lock = Lock()

    def _get_user_messages(self, user_id: str):
        # """获取用户的对话历史，不存在则创建"""
        # if user_id not in self.user_sessions:
        #     # self.user_sessions[user_id] = []
        # return self.user_sessions[user_id]
        """限制历史长度"""
        return load_memory_store(user_id, MAX_HISTORY)


    def _add_user_message(self, user_id: str, role: str, content: str):
        """添加用户消息"""
        with self._lock:

            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            messages = self._get_user_messages(user_id)
            msg = {"time": formatted_time, "role": role, "content": content}
            messages.append(msg)
            add_message_in_memory_store(user_id, msg)


    def clear_history(self, user_id: str = None):
        """清除指定用户或所有用户的对话历史"""
        with self._lock:
            if user_id:
                self.user_sessions.pop(user_id, None)
            else:
                self.user_sessions.clear()

    def excute_stream(self, query: str, user_id: str = None):
        """流式执行，带用户隔离"""
        user_id = user_id or "default"
        self._add_user_message(user_id, "user", query)

        messages = self._get_user_messages(user_id)
        input_dict = {"messages": messages}

        assistant_text = ""
        for chunk in self.agent.stream(input_dict, stream_mode="values"):
            latest_message = chunk["messages"][-1]
            role = getattr(latest_message, "role", None) or getattr(latest_message, "type", None)
            content = getattr(latest_message, "content", None)
            if role in ("assistant", "ai") and content:
                assistant_text = content
                yield content.strip() + "\n"

        if assistant_text:
            self._add_user_message(user_id, "assistant", assistant_text.strip())

    def get_reply(self, query: str, user_id: str = None):
        """获取回复，带用户隔离"""
        if user_id is None:
            input_dict = {
                "messages": [
                    {"role": "user", "content": query},
                ]
            }
        else:
            self._add_user_message(user_id, "user", query)
            messages = self._get_user_messages(user_id)
            input_dict = {"messages": messages}

        res = self.agent.invoke(input_dict)
        latest_message = res["messages"][-1]
        content = getattr(latest_message, "content", None)

        if content and user_id:
            self._add_user_message(user_id, "assistant", content.strip())

        return content

main_agent = MainAgent()


def get_agent():
    """获取Agent实例"""
    return main_agent


if __name__ == '__main__':
    agent = MainAgent()
    # 测试用户隔离
    print(agent.get_reply("你好", user_id="user_001"))

