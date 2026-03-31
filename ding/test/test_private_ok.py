import requests
import json

# API 地址
url = "https://api.dingtalk.com/v1.0/robot/oToMessages/batchSend"

# 请求头
headers = {
    "x-acs-dingtalk-access-token": "ff2898d4cf503dfd9c7844a48b397db3",  # 替换为你的实际token
    "Content-Type": "application/json"
}

msg_key = "sampleActionCard"
msg_param = {
        "title": "测试标题",
        "text": "内容测试",
        "singleTitle": "查看详情",
        "singleURL": "https://open.dingtalk.com"
    }

# 请求体
payload = {
    "robotCode": "ding78qvob0ffowxxwtm",  # 替换为你的机器人Code
    "userIds": ["4248573029996722", "user456"],  # 接收消息的用户ID列表
    "msgKey": msg_key,  # 消息类型Key，例如：sampleTextMsg（文本消息）
    "msgParam": json.dumps(msg_param)  # 消息参数，需转为JSON字符串
}

# 发送POST请求
response = requests.post(url, headers=headers, json=payload)

# 打印响应
print("状态码:", response.status_code)
print("响应内容:", response.text)