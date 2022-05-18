import logging
from sacred import Experiment


ex = Experiment('hello_config', save_git_info=False)
logging.basicConfig(level=logging.CRITICAL)


@ex.config
def my_config():
    number = 0.1
    text = 'some test'
    mylist = [1, None]
    mydict = {'0': 1, '1': "test"}


@ex.automain
def my_main(_config):
    print(_config)
