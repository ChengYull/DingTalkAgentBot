#!/usr/bin/env python

import argparse
from dingtalk_stream import AckMessage
import dingtalk_stream

from agent.main_agent import MainAgent, main_agent
from utils.config_handler import bot_conf


class MyEventHandler(dingtalk_stream.EventHandler):
    async def process(self, event: dingtalk_stream.EventMessage):
        print(event.headers.event_type,
              event.headers.event_id,
              event.headers.event_born_time,
              event.data)

        return AckMessage.STATUS_OK, 'OK'


class MyCallbackHandler(dingtalk_stream.CallbackHandler):
    def __init__(self, agent: MainAgent):
        super(MyCallbackHandler, self).__init__()
        self.agent = agent

    async def process(self, message: dingtalk_stream.CallbackMessage):
        ## conversationType 1 表示单聊，2 表示群聊
        ## conversationId 会话id
        print("-message.data-", message.data)

        return AckMessage.STATUS_OK, 'OK'


def main():
    client_id = bot_conf["client_id"]
    client_secret = bot_conf["client_secret"]

    credential = dingtalk_stream.Credential(client_id, client_secret)
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_all_event_handler(MyEventHandler())
    client.register_callback_handler(dingtalk_stream.ChatbotMessage.TOPIC, MyCallbackHandler(main_agent))
    client.start_forever()


if __name__ == '__main__':
    main()