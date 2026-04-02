from ding.utils.main_request import main_req

GET_USERID_BY_NAME_URL = 'https://api.dingtalk.com/v1.0/contact/users/search'

def get_userid_by_name(access_token: str, name: str) -> str:
    body = {
        "queryWord": name,
        "offset": 0,
        "size": 1,
        "fullMatchField": 1
    }
    return main_req(access_token, GET_USERID_BY_NAME_URL, body)

if __name__ == '__main__':

    print(get_userid_by_name("程渝", "90bc4a9ed7e136dab743ee74d70a042b"))