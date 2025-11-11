from contextvars import ContextVar

class Config:
    filler_url = "https://api.tristero.com/v2/orders"
    quoter_url = "https://api.tristero.com/v2/quotes"
    ws_url = "wss://api.tristero.com/v2/orders"

    headers = {
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    }

config_var = ContextVar("config", default=Config())

def get_config():
    return config_var.get()

def set_config(new_config: Config):
    return config_var.set(new_config)

