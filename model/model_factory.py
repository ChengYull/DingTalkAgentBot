import os
from abc import ABC, abstractmethod
from typing import Optional

from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

from utils.config_handler import model_conf

from langchain_community.chat_models import ChatOpenAI

class BaseModelFactory(ABC):
    @abstractmethod
    def geterator(self) -> Optional[Embeddings | BaseChatModel]:
        pass



class ChatModelFactory(BaseModelFactory):
    def geterator(self) -> Optional[Embeddings | BaseChatModel]:
        model_root = model_conf["key_root"]
        if model_root == "bailian":
            select_key = model_conf["select_key"]
            os.environ["OPEN_AI_KEY"] = model_conf["key"][select_key]
            # print(os.environ["OPEN_AI_KEY"])
            return ChatTongyi(model=model_conf["chat_model"])
        elif model_root == "openai":
            # print(model_conf[model_conf["key_root"]]["key"])
            os.environ["OPENAI_API_KEY"] = model_conf[model_root]["minimax"]["key"]
            return ChatOpenAI(
                model=model_conf["chat_model"],
                openai_api_base=model_conf[model_root]["minimax"]["url"]
            )

        else:
            return None


class EmbedingsFactory(BaseModelFactory):
    def geterator(self) -> Optional[Embeddings | BaseChatModel]:
        if model_conf["key_root"] == "bailian":
            select_key = model_conf["select_key"]
            os.environ["DASHSCOPE_API_KEY"] = model_conf["key"][select_key]
        else:
            return None
        return DashScopeEmbeddings(model=model_conf["embedding_model_name"])

# 初始化 避免报错
select_key = model_conf["select_key"]
os.environ["OPEN_AI_KEY"] = model_conf["key"][select_key]
os.environ["DASHSCOPE_API_KEY"] = model_conf["key"][select_key]

chat_model = ChatModelFactory().geterator()
embedings_model = EmbedingsFactory().geterator()

if __name__ == '__main__':
    response = chat_model.invoke("你好")
    print(response.content)