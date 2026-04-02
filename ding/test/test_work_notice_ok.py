# -*- coding: utf-8 -*-
"""
钉钉企业内部应用 - 纯HTTP请求发送工作通知
只需要 requests 库，无需复杂的 SDK

官方API文档：
https://open.dingtalk.com/document/orgapp/asynchronous-sending-of-enterprise-session-messages
"""

import json
import time
import requests

from utils.config_handler import bot_conf


class DingTalkWorkNotice:
    """
    钉钉工作通知消息发送器
    纯HTTP实现，简单可靠
    """

    def __init__(self, app_key: str, app_secret: str, agent_id: int):
        """
        初始化

        Args:
            app_key: 应用的 AppKey
            app_secret: 应用的 AppSecret
            agent_id: 应用的 AgentId
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.agent_id = agent_id
        self._access_token = None
        self._token_expires_at = 0

    def _get_access_token(self) -> str:
        """获取访问令牌"""
        # 如果token还有效，直接返回
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        # 获取新token
        url = "https://oapi.dingtalk.com/gettoken"
        params = {
            "appkey": self.app_key,
            "appsecret": self.app_secret
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

    def _send(self, body: dict) -> dict:
        """发送消息"""
        token = self._get_access_token()

        url = f"https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={token}"

        response = requests.post(url, json=body)
        return response.json()

    def send_text(
        self,
        content: str,
        userid_list: list = None,
        dept_id_list: list = None,
        to_all_user: bool = False
    ) -> dict:
        """
        发送文本消息

        Args:
            content: 文本内容（最长2048字节）
            userid_list: 接收者userid列表，如 ["user001", "user002"]
            dept_id_list: 接收者部门id列表，如 [123, 456]
            to_all_user: 是否发送给全员

        Returns:
            {"errcode": 0, "errmsg": "ok", "task_id": 123456}
        """
        body = {
            "agent_id": self.agent_id,
            "msg": {
                "msgtype": "text",
                "text": {"content": content}
            },
            "to_all_user": to_all_user
        }

        if userid_list:
            body["userid_list"] = ",".join(userid_list)

        if dept_id_list:
            body["dept_id_list"] = ",".join(str(d) for d in dept_id_list)

        return self._send(body)

    def send_markdown(
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

        return self._send(body)

    def send_link(
        self,
        title: str,
        text: str,
        message_url: str,
        pic_url: str = None,
        userid_list: list = None,
        dept_id_list: list = None,
        to_all_user: bool = False
    ) -> dict:
        """
        发送链接消息
        """
        link_body = {
            "title": title,
            "text": text,
            "messageUrl": message_url
        }
        if pic_url:
            link_body["picUrl"] = pic_url

        body = {
            "agent_id": self.agent_id,
            "msg": {
                "msgtype": "link",
                "link": link_body
            },
            "to_all_user": to_all_user
        }

        if userid_list:
            body["userid_list"] = ",".join(userid_list)

        if dept_id_list:
            body["dept_id_list"] = ",".join(str(d) for d in dept_id_list)

        return self._send(body)

    def send_action_card(
        self,
        title: str,
        content: str,
        single_title: str,
        single_url: str,
        userid_list: list = None,
        dept_id_list: list = None,
        to_all_user: bool = False
    ) -> dict:
        """
        发送卡片消息（单按钮）
        """
        body = {
            "agent_id": self.agent_id,
            "msg": {
                "msgtype": "action_card",
                "action_card": {
                    "title": title,
                    "markdown": content,
                    "single_title": single_title,
                    "single_url": single_url
                }
            },
            "to_all_user": to_all_user
        }

        if userid_list:
            body["userid_list"] = ",".join(userid_list)

        if dept_id_list:
            body["dept_id_list"] = ",".join(str(d) for d in dept_id_list)

        return self._send(body)


# ==================== 使用示例 ====================

def main():
    """
    使用示例
    """

    print("=" * 60)
    print("钉钉工作通知消息发送示例")
    print("=" * 60)

    # ========== 配置参数（请替换为你的实际值）==========

    # 在钉钉开放平台获取
    APP_KEY = bot_conf["client_id"]  # 在钉钉开放平台 - 应用详情 获取
    APP_SECRET = bot_conf["client_secret"]  # 在钉钉开放平台 - 应用详情 获取

    # 用户的 staffId（在钉钉管理后台 - 通讯录 - 搜索用户 获取）
    USER_ID = '42485730299967212'
    AGENT_ID = bot_conf["agent_id"]  # 替换为你的 AgentId
    USER_ID_LIST = [USER_ID]  # 替换为接收者的 userId

    # 创建客户端
    dingtalk = DingTalkWorkNotice(APP_KEY, APP_SECRET, AGENT_ID)

    # ========== 示例1: 发送文本消息 ==========
    print("\n📤 发送文本消息...")
    result = dingtalk.send_text(
        content="👋 你好！这是一条测试消息",
        userid_list=USER_ID_LIST
    )
    print_result(result)

    # ========== 示例2: 发送 Markdown 消息 ==========
    print("\n📤 发送 Markdown 消息...")
    markdown = """## 📊 今日工作日报

**已完成：**
- ✅ 功能A开发
- ✅ 代码评审

**明日计划：**
- 🔄 功能B开发
- 📝 编写文档
"""
    result = dingtalk.send_markdown(
        title="今日日报",
        content=markdown,
        userid_list=USER_ID_LIST
    )
    print_result(result)

    # ========== 示例3: 发送链接消息 ==========
    print("\n📤 发送链接消息...")
    result = dingtalk.send_link(
        title="钉钉开放平台",
        text="点击访问钉钉开发者文档",
        message_url="https://open.dingtalk.com/",
        userid_list=USER_ID_LIST
    )
    print_result(result)

    # ========== 示例4: 发送卡片消息 ==========
    print("\n📤 发送卡片消息...")
    result = dingtalk.send_action_card(
        title="🔔 系统通知",
        content="### 系统将于今晚 **22:00** 维护\n\n请提前保存工作",
        single_title="查看详情",
        single_url="https://oa.example.com/notice",
        userid_list=USER_ID_LIST
    )
    print_result(result)

    # ========== 示例5: 发送给部门 ==========
    print("\n📤 发送给部门...")
    result = dingtalk.send_text(
        content="部门通知消息",
        dept_id_list=[1, 2, 3]  # 部门ID列表
    )
    print_result(result)

    # ========== 示例6: 发送给全员 ==========
    print("\n📤 发送给全员...")
    result = dingtalk.send_text(
        content="全员通知消息",
        to_all_user=True
    )
    print_result(result)

    print("\n" + "=" * 60)


def print_result(result: dict):
    """打印结果"""
    if result.get("errcode") == 0:
        print(f"✅ 发送成功! task_id: {result.get('task_id')}")
    else:
        print(f"❌ 发送失败!")
        print(f"   errcode: {result.get('errcode')}")
        print(f"   errmsg: {result.get('errmsg')}")


if __name__ == '__main__':
    # main()

    APP_KEY = bot_conf["client_id"]  # 在钉钉开放平台 - 应用详情 获取
    APP_SECRET = bot_conf["client_secret"]  # 在钉钉开放平台 - 应用详情 获取

    # 用户的 staffId（在钉钉管理后台 - 通讯录 - 搜索用户 获取）
    USER_ID = '$:LWCP_v1:$K1UHjYKAuT2TDx3Cg276psGM9IBnsHvq'
    AGENT_ID = bot_conf["agent_id"]  # 替换为你的 AgentId
    USER_ID_LIST = [USER_ID]  # 替换为接收者的 userId

    # 创建客户端
    dingtalk = DingTalkWorkNotice(APP_KEY, APP_SECRET, AGENT_ID)

    # ========== 示例1: 发送文本消息 ==========
    print("\n📤 发送文本消息...")
    result = dingtalk.send_text(
        content="👋 你好！这是一条测试消息",
        userid_list=USER_ID_LIST
    )
    print_result(result)
