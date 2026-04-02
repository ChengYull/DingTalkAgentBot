import requests


def main_req(access_token, url, body: dict):
    headers = {
        "x-acs-dingtalk-access-token": access_token,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=body)
    return {
        "code": response.status_code,
        "data": response.json()
    }