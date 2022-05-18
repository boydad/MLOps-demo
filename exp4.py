import logging
from sacred import Experiment

logging.basicConfig(level=logging.CRITICAL)
ex = Experiment('hello_config', save_git_info=False)
ex.add_config('config.json')


@ex.automain
def my_main(_config):
    print(_config)
