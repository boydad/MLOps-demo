import logging
from sacred import Experiment


ex = Experiment('hello_config', save_git_info=False)
logging.basicConfig(level=logging.CRITICAL)


@ex.config
def my_config():
    recipient = "world"
    message = "Hello %s!" % recipient


@ex.automain
def my_main(message):
    print(message)
