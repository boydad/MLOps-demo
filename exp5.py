import logging
from sacred import Experiment

logging.basicConfig(level=logging.CRITICAL)
ex = Experiment('hello_config', save_git_info=False)

@ex.automain
def my_main(_config):
    print(_config)
