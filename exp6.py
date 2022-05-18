import torch
from sacred import Experiment


ex = Experiment('exp6', save_git_info=False)


@ex.config
def my_config():
    opt_type = 'Adam'
    opt_cfg = {'lr': 0.1}


@ex.automain
def my_main(_config):
    model = torch.nn.Linear(1, 1)
    optClass = getattr(torch.optim, _config['opt_type'])
    optimizer = optClass(model.parameters(), **_config['opt_cfg'])
    print(optimizer)
