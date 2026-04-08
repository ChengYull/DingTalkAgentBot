import yaml

from utils.path_handler import get_abs_path

def load_config(config_path: str, encoding: str = "utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_prompt_config(config_path: str = get_abs_path("config/prompt_config.yml")):
    return load_config(config_path, encoding="utf-8")

def load_model_config(config_path: str = get_abs_path("config/model_config.yml")):
    return load_config(config_path, encoding="utf-8")

def load_log_config(config_path: str = get_abs_path("config/log_config.yml")):
    return load_config(config_path, encoding="utf-8")

def load_bot_config(config_path: str = get_abs_path("config/ding_bot_config.yml")):
    return load_config(config_path, encoding="utf-8")

def load_memory_config(config_path: str = get_abs_path("config/memory_config.yml")):
    return load_config(config_path, encoding="utf-8")

model_conf = load_model_config()
log_conf = load_log_config()
prompt_conf = load_prompt_config()
bot_conf = load_bot_config()
memory_conf = load_memory_config()

if __name__ == '__main__':
    print(load_prompt_config()["system_prompt_path"])
    print(get_abs_path(load_log_config()["log_path"]))
