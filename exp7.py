import torch
from sacred import Experiment


ex = Experiment('exp7', save_git_info=False)


def init_model():
    model = torch.nn.Linear(1, 1)
    inputs = torch.randn(1024)
    return model, inputs


@ex.command
def validate(_config):
    model, inputs = init_model()
    model.eval()
    print("I do validation")


@ex.command
def profile(_config):
    model, inputs = init_model()
    print("I do profile")


@ex.automain
def train(_config):
    model, inputs = init_model()
    model.train()
    print("I do train")
