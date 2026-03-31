import json

from agent.main_agent import MainAgent, main_agent
from ding.utils.message_utils import send_private_message_util
from utils.config_handler import bot_conf
from typing import Dict, Any
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests

from utils.logger_handler import logger

import logging
from dingtalk_stream import AckMessage
import dingtalk_stream


def send_dingtalk_robot_message(access_token, secret, msg, at_user_ids=None, at_mobiles=None, is_at_all=False):
    """
    发送钉钉自定义机器人群消息

    :param access_token: 机器人webhook的access_token
    :param secret: 机器人安全设置的加签secret
    :param msg: 消息内容
    :param at_user_ids: @的用户ID列表，如 ["userid1", "userid2"] 或 "userid1,userid2"
    :param at_mobiles: @的手机号列表，如 ["13800000000", "13900000000"] 或 "13800000000,13900000000"
    :param is_at_all: 是否@所有人，默认False
    :return: 钉钉API响应
    """
    # 处理参数格式
    if at_user_ids and isinstance(at_user_ids, str):
        at_user_ids = [u.strip() for u in at_user_ids.split(',') if u.strip()]
    if at_mobiles and isinstance(at_mobiles, str):
        at_mobiles = [m.strip() for m in at_mobiles.split(',') if m.strip()]

    # 生成签名
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f'{timestamp}\n{secret}'
    hmac_code = hmac.new(secret.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    # 构建请求URL
    url = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}&timestamp={timestamp}&sign={sign}'
    # 构建请求体
    body = {
        "at": {
            "isAtAll": str(is_at_all).lower(),
            "atUserIds": at_user_ids or [],
            "atMobiles": at_mobiles or []
        },

        "markdown": {
            "title": "title",
            "text": msg
        },
        "msgtype": "markdown"
    }

    # 发送请求
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, json=body, headers=headers)

    return resp.json()

current_user_info = {}

class EchoTextHandler(dingtalk_stream.ChatbotHandler):
    def __init__(self, mainAgent: MainAgent):
        super(dingtalk_stream.ChatbotHandler, self).__init__()
        self.agent = mainAgent

    async def process(self, callback: dingtalk_stream.CallbackMessage):
        incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        text = incoming_message.text.content.strip()
        # 获取用户ID用于会话隔离
        user_id = incoming_message.sender_id
        current_user_info["user_id"] = user_id
        current_user_info["user_nick"] = incoming_message.sender_nick
        logger.info(f'[钉钉消息] 用户ID: {user_id}，会话id：{incoming_message.conversation_id}, 内容: {text}')
        reply = await self.get_agent_reply(text, user_id=user_id)
        self.reply_text(reply, incoming_message)
        return AckMessage.STATUS_OK, 'OK'

    async def get_agent_reply(self, query, user_id=None):
        return self.agent.get_reply(query, user_id=user_id)

class MyEventHandler(dingtalk_stream.EventHandler):
    async def process(self, event: dingtalk_stream.EventMessage):
        logger.info(event.headers.event_type,
              event.headers.event_id,
              event.headers.event_born_time,
              event.data)

        return AckMessage.STATUS_OK, 'OK'

class MyCallbackHandler(dingtalk_stream.CallbackHandler):
    def __init__(self, agent: MainAgent):
        super(MyCallbackHandler, self).__init__()
        self.agent = agent

    async def process(self, message: dingtalk_stream.CallbackMessage):
        ## conversationType 1 表示单聊，2 表示群聊
        ## conversationId 会话id
        logger.info(f"[钉钉接收消息]-message.data- {message.data}")
        user_id = message.data.get("senderStaffId", None)
        input_msg = {
            "conversation_type": message.data.get("conversationType"),
            "conversation_id": message.data.get("conversationId"),
            "user_id": message.data.get("senderStaffId"),
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

    # def send_group_message(self, text, user_ids="", at_all=False):
    #     # user_ids 可选的@参数
    #     mobiles = ""  # 或 ["13800000000", "13900000000"]
    #     try:
    #         # 发送消息
    #         result = send_dingtalk_robot_message(
    #             access_token=self.access_token,
    #             secret="",
    #             msg=text,
    #             at_user_ids=user_ids,  # 可省略
    #             at_mobiles=mobiles,  # 可省略
    #             is_at_all=at_all
    #         )
    #         logger.debug(f"[钉钉群组消息发送]：{text}")
    #         logger.info(f"[钉钉群组消息发送] 结果：{result}")
    #         return result
    #     except Exception as e:
    #         logger.error(f"[钉钉群组消息发送]发生错误：{str(e)}")
    #         return {"msg": f"[钉钉群组消息发送]发生错误：{str(e)}"}

    def get_cur_user_info(self):
        return current_user_info



    def send_private_message(self, user_id_list, msg_param):
        res = send_private_message_util(self._get_access_token(), self.client_id, user_id_list, msg_param)
        logger.info(f"[钉钉私聊消息发送] 消息：{msg_param} 结果：{res}")
        return res

    def send_group_message(self, conversation_id, msg_param):
        res = send_private_message_util(self._get_access_token(), self.client_id, conversation_id, msg_param)
        logger.info(f"[钉钉群聊消息发送] 消息：{msg_param} 结果：{res}")
        return

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
    ding_bot_service.run_bot_listen_server()
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