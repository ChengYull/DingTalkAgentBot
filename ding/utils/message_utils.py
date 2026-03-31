import json

import requests

GROUP_MESSAGE_URL = "https://api.dingtalk.com/v1.0/robot/groupMessages/send"
PRIVATE_MESSAGE_URL = "https://api.dingtalk.com/v1.0/robot/oToMessages/batchSend"
GROUP_MESSAGE = 2
PRIVATE_MESSAGE = 1


def send_message_req(access_token, conversation_type: int, body: dict):
    headers = {
        "x-acs-dingtalk-access-token": access_token,
        "Content-Type": "application/json"
    }
    if conversation_type == PRIVATE_MESSAGE:
        url = PRIVATE_MESSAGE_URL
    elif conversation_type == GROUP_MESSAGE:
        url = GROUP_MESSAGE_URL
    else:
        raise ValueError("conversation_type must be 1 (private) or 2 (group)")
    response = requests.post(url, headers=headers, json=body)
    return {
        "code": response.status_code,
        "data": response.json()
    }

def send_group_message_util(access_token, client_id, conversation_id: str, msg_param: dict):
    body = {
            "robotCode": client_id,
            "openConversationId": conversation_id,
            "msgKey": msg_param.get("msgKey", ""),
            "msgParam": json.dumps(msg_param.get("msgParam", {}))
    }
    return send_message_req(access_token, GROUP_MESSAGE, body)

def send_private_message_util(access_token,client_id, user_is_list: list[str], msg_param: dict):
    body = {
        "robotCode": client_id,
        "userIds": user_is_list,
        "msgKey": msg_param.get("msgKey", ""),
        "msgParam": json.dumps(msg_param.get("msgParam", {}))
    }
    return send_message_req(access_token, PRIVATE_MESSAGE, body)