import requests
import json
from typing import Dict, Any, Optional


def send_group_message(
        access_token: str,
        msg_key: str,
        msg_param: Dict[str, Any],
        open_conversation_id: str,
        cool_app_code: str,
        robot_code: str
) -> Dict[str, Any]:
    """
    发送钉钉群消息

    Args:
        access_token: 钉钉access token
        msg_key: 消息类型标识
        msg_param: 消息参数（JSON对象）
        open_conversation_id: 群聊ID
        robot_code: 机器人标识

    Returns:
        接口返回结果
    """
    url = "https://api.dingtalk.com/v1.0/robot/groupMessages/send"

    headers = {
        "x-acs-dingtalk-access-token": access_token,
        "Content-Type": "application/json"
    }

    data = {
        "msgKey": msg_key,
        "msgParam": json.dumps(msg_param, ensure_ascii=False),
        "openConversationId": open_conversation_id,
        "robotCode": robot_code,
        "coolAppCode": cool_app_code
    }

    try:
        response = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(data, ensure_ascii=False)
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"响应内容: {e.response.text}")
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return {"error": f"JSON解析失败: {e}"}


# 使用示例
if __name__ == "__main__":
    # 示例参数
    ACCESS_TOKEN = "18d6c9d399d63c06913e82c147de841aq"
    # MSG_KEY = "sampleText"  # 文本消息类型
    # MSG_PARAM = {
    #     "content": "这是一条测试消息"
    # }
    ### markdown类型
    #     MSG_KEY = "sampleMarkdown"  # 文本消息类型
    #     MSG_PARAM = {
    #         "title": "xxxx",
    #         "text": """### 1. 华为Pura 90系列外观细节曝光 侧边指纹保留 位置上移
    # - **时间**: 2026-03-27 09:20
    # - **摘要**: 华为Pura 90系列细节信息流出，将继续采用直角边框设计，后置摄像头模组形态变化不大。值得关注的是，侧边指纹识别方案得以延续，但识别按键位置进行了调整，被设计得“相对靠上”，疑似为潜望式长焦镜头腾出空间。该系列预计包含三款机型，可能全系回归直屏设计。
    # - **详情**: https://phone.cnmo.com/news/806257.html
    # ![图片描述](https://img.cnmo.com/2341_400x250/2340386.png)
    # """
    #     }
    ### 图片类型
    # MSG_KEY = "sampleImageMsg"  # 图片类型
    # MSG_PARAM = {
    #     "photoURL": "https://img.cnmo.com/2341_400x250/2340386.png"
    # }

    ### 链接类型
    # MSG_KEY = "sampleLink"  # 文本消息类型
    # MSG_PARAM = {
    #     "text": "消息内容测试",
    #     "title": "sampleLink消息测试",
    #     "picUrl": "@lADOADmaWMzazQKA",
    #     "messageUrl": "http://dingtalk.com"
    # }

    ### 卡片类型
    MSG_KEY = "sampleActionCard"  # 文本消息类型
    MSG_PARAM = {
        "title": "测试标题",
        "text": "内容测试",
        "singleTitle": "查看详情",
        "singleURL": "https://open.dingtalk.com"
    }
    OPEN_CONVERSATION_ID = "cidModuDcbZfghdH592n2/lnBw=="
    ROBOT_CODE = "ding78qvob0ffowxxw1tm"
    COOL_APP_CODE = "COOLAPP-1-1037FC5BDBC721335DB1D000W"
    # 调用发送消息
    result = send_group_message(
        access_token=ACCESS_TOKEN,
        msg_key=MSG_KEY,
        msg_param=MSG_PARAM,
        open_conversation_id=OPEN_CONVERSATION_ID,
        robot_code=ROBOT_CODE,
        cool_app_code=COOL_APP_CODE
    )

    print("调用结果:", json.dumps(result, ensure_ascii=False, indent=2))
