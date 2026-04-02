import requests
import json

from utils.config_handler import bot_conf

# 钉钉机器人API地址
url = "https://api.dingtalk.com/v1.0/robot/groupMessages/send"

# 请求头
headers = {
    "Content-Type": "application/json",
    "x-acs-dingtalk-access-token": "ff2898d4cf503dfd9c7844a48b397db23"  # 替换为实际的access_token
}

# 请求体
data = {
    "msgParam": json.dumps({
        "content": "11"
    }),  # 消息参数，根据msgKey的不同格式会变化
    "msgKey": "sampleText",  # 消息模板Key，如：sampleText、sampleImageMsg等
    "openConversationId": "cidISzpQt3AXRimkEM/vYGDiA1==",  # 群会话ID
    "robotCode": bot_conf["robotCode"]  # 机器人编码
}

# 发送请求
response = requests.post(url, headers=headers, json=data)

# 输出响应
print(f"状态码: {response.status_code}")
print(f"响应内容: {response.text}")

# 解析响应
if response.status_code == 200:
    result = response.json()
    print("消息发送成功")
    print(f"消息ID: {result.get('processQueryKey')}")
else:
    print(f"消息发送失败: {response.text}")