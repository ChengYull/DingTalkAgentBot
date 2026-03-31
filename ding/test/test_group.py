import requests
import json

# 钉钉机器人API地址
url = "https://api.dingtalk.com/v1.0/robot/groupMessages/send"

# 请求头
headers = {
    "Content-Type": "application/json",
    "x-acs-dingtalk-access-token": "43219a0960db38e99ec46d5e0b1f904c"  # 替换为实际的access_token
}

# 请求体
data = {
    "msgParam": json.dumps({
        "content": "这是一条测试消息22"
    }),  # 消息参数，根据msgKey的不同格式会变化
    "msgKey": "sampleText",  # 消息模板Key，如：sampleText、sampleImageMsg等
    "openConversationId": "cidISzpQt3AXRimkEM/vYGDiA==",  # 群会话ID
    "robotCode": "ding78qvob0ffowxxwtm"  # 机器人编码
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