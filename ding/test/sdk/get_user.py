import dingtalk.api
request = dingtalk.api.OapiGettokenRequest("https://oapi.dingtalk.com/user/get")
request.userid="userid1"
response = request.getResponse()
print(response)