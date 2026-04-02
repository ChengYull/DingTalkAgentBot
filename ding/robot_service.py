import json

from agent.main_agent import MainAgent, main_agent
from ding.utils.message_utils import send_private_message_util, send_group_message_util
from ding.utils.user_utils import get_userid_by_name
from utils.config_handler import bot_conf
import time
import requests
from utils.logger_handler import logger
from dingtalk_stream import AckMessage
import dingtalk_stream

class MyEventHandler(dingtalk_stream.EventHandler):
    async def process(self, event: dingtalk_stream.EventMessage):
        logger.info(event.headers.event_type,
              event.headers.event_id,
              event.headers.event_born_time,
              event.data)

        return AckMessage.STATUS_OK, 'OK'

class MyCallbackHandler(dingtalk_stream.ChatbotHandler):
    def __init__(self, agent: MainAgent):
        super(MyCallbackHandler, self).__init__()
        self.agent = agent

    async def process(self, message: dingtalk_stream.CallbackMessage):
        ## conversationType 1 表示单聊，2 表示群聊
        ## conversationId 会话id
        logger.info(f"[钉钉接收消息]-message.data- {message.data}")
        user_id = message.data.get("senderStaffId", None)
        conversation_type = message.data.get("conversationType", None)
        conversation_id = message.data.get("conversationId", None)
        input_msg = {
            "conversation_type": conversation_type,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "sender_nick": message.data.get("senderNick"),
            "text": message.data.get("text", {}).get("content", ""),
        }
        input_str = json.dumps(input_msg, ensure_ascii=False)
        rep = await self.get_agent_reply(input_str, user_id=user_id)
        logger.debug(f"[钉钉消息处理结果]  {rep}")
        return AckMessage.STATUS_OK, 'OK'
    async def get_agent_reply(self, query, user_id=None):
        return self.agent.get_reply(query, user_id=user_id)

class RobotService:

    def __init__(self):
        self.agent = None

        self.access_token = bot_conf["access_token"]
        self.client_id = bot_conf["client_id"]
        self.client_secret = bot_conf["client_secret"]
        self.agent_id = bot_conf["agent_id"]
        self._access_token = None
        self._token_expires_at = 0 # token刷新时间

    def _get_access_token(self) -> str:
        """获取访问令牌"""
        # 如果token还有效，直接返回
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        # 获取新token
        url = "https://oapi.dingtalk.com/gettoken"
        params = {
            "appkey": self.client_id,
            "appsecret": self.client_secret
        }

        response = requests.get(url, params=params)
        result = response.json()

        if result.get("errcode") == 0 and result.get("access_token"):
            self._access_token = result["access_token"]
            # token有效期2小时，提前5分钟刷新
            self._token_expires_at = time.time() + 115 * 60
            return self._access_token
        else:
            raise Exception(f"获取 access_token 失败: {result}")

    def _send_work_notice(self, body: dict) -> dict:
        token = self._get_access_token()
        url = f"https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={token}"
        response = requests.post(url, json=body)
        return response.json()

    def send_markdown_work_notice(
        self,
        title: str,
        content: str,
        userid_list: list = None,
        dept_id_list: list = None,
        to_all_user: bool = False
    ) -> dict:
        """
        发送 Markdown 消息

        支持的Markdown语法:
            # 一级标题
            ## 二级标题
            **加粗文字**
            [链接文字](URL)
            - 列表项
        """
        body = {
            "agent_id": self.agent_id,
            "msg": {
                "msgtype": "markdown",
                "markdown": {"title": title, "text": content}
            },
            "to_all_user": to_all_user
        }

        if userid_list:
            body["userid_list"] = ",".join(userid_list)

        if dept_id_list:
            body["dept_id_list"] = ",".join(str(d) for d in dept_id_list)

        return self._send_work_notice(body)



    def send_private_message(self, user_id_list, msg_param):
        res = send_private_message_util(self._get_access_token(), self.client_id, user_id_list, msg_param)
        logger.info(f"[钉钉私聊消息发送] 消息：{msg_param} 结果：{res}")
        return res

    def send_group_message(self, conversation_id, msg_param):
        res = send_group_message_util(self._get_access_token(), self.client_id, conversation_id, msg_param)
        logger.info(f"[钉钉群聊消息发送] 消息：{msg_param} 结果：{res}")
        return res

    def get_user_id_by_nick(self, nick_name):
        res = get_userid_by_name(self._get_access_token(), nick_name)
        logger.info(f"[根据昵称获取用户ID] 昵称：{nick_name} 结果：{res}")
        if res["code"] == 200 and res["data"]["list"]:
            return res["data"]["list"][0]
        else:
            return f"未找到昵称为 {nick_name} 的用户, 结果：{res}"

    def run_bot_listen_server(self):
        client_id = self.client_id
        client_secret = self.client_secret
        credential = dingtalk_stream.Credential(client_id, client_secret)

        client = dingtalk_stream.DingTalkStreamClient(credential)
        client.register_all_event_handler(MyEventHandler())
        client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, MyCallbackHandler(main_agent))
        self.send_private_message(["4248573029996722"],
                                  {
                                      "msgKey": "sampleMarkdown",
                                      "msgParam": {
                                          "title": "服务已启动",
                                          "text": "# 服务已启动 \n\n机器人监听服务器已启动，等待接收消息..."
                                      }
                                  })
        client.start_forever()

ding_bot_service = RobotService()

if __name__ == '__main__':
    # ding_bot_service.send_group_message("11")
    print(ding_bot_service._get_access_token())
    print(ding_bot_service.get_user_id_by_nick("程渝"))
    # ding_bot_service.run_bot_listen_server()
    # msg_param = {
    #     "msgKey": "sampleMarkdown",
    #     "msgParam": {
    #         "title": "Markdown消息标题",
    #         "text": "# 一级标题\n## 二级标题\n**加粗文字**\n[链接文字](https://www.example.com)\n- 列表项1\n- 列表项2"
    #     }
    # }
    # print(
    #     ding_bot_service.send_private_message(["4248573029996722"], msg_param)
    #     # ding_bot_service.send_group_message2("cidISzpQt3AXRimkEM/vYGDiA==", msg_param)
    # )