from ding.utils.main_request import main_req

GET_GROUP_MENBER_URL = "https://api.dingtalk.com/v1.0/contact/users/search"

body = {
    "queryWord": "程",
    "offset": 0,
    "size": 1,
    "fullMatchField": 1
}
access_token = "90bc4a9ed7e136dab743ee74d70a042b"
print(main_req(access_token, GET_GROUP_MENBER_URL, body))