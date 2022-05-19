from __future__ import print_function
from sacred import Experiment
import wandb
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR


ex = Experiment('exp8', save_git_info=False)
from sacred.observers import MongoObserver
ex.observers.append(MongoObserver.create(
    url=f'mongodb://mongo_user:mongo_password@mongo/sacred', db_name='sacred'))
wandb.init(project="demo", entity="alcf-datascience", name='exp8')


@ex.config
def ml_config():
    batch_size = 6000
    epochs = 14
    lr = 1.0
    gamma = 0.7
    log_interval = 1
    model_path = None


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


def init(_seed, _config):
    torch.manual_seed(_seed)

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
        ])

    train_loader = torch.utils.data.DataLoader(
        datasets.MNIST(
            './data',
            train=True,
            download=True,
            transform=transform
        ),
        batch_size=_config['batch_size'],
        pin_memory=True,
        shuffle=True
    )

    test_loader = torch.utils.data.DataLoader(
        datasets.MNIST(
            './data',
            train=False,
            transform=transform
        ),
        batch_size=_config['batch_size'],
        pin_memory=True,
        shuffle=True
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = Net().to(device)
    optimizer = optim.Adadelta(model.parameters(), lr=_config['lr'])
    scheduler = StepLR(optimizer, step_size=1, gamma=_config['gamma'])
    return model, optimizer, scheduler, train_loader, test_loader


def test_epoch(model, test_loader, epoch, _run):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    loss = 0
    with torch.no_grad():
        for batchidx, (data, target) in enumerate(test_loader):
            data, target = data.to(device), target.to(device)
            output = model(data)
            loss += F.nll_loss(output, target).item()
    return loss / len(test_loader)


def train_epoch(model, train_loader, optimizer, epoch, log_interval, _run):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    Ndata = len(train_loader.dataset)
    Nbathes = len(train_loader)
    epoch_loss = 0
    for batchidx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
        if batchidx % log_interval == 0:
            print(f'---->[{batchidx*len(data)}/{Ndata}' \
                  f' ({batchidx/Nbathes*100:.0f}%)]\tLoss: {loss:.6f}')
    return epoch_loss / Nbathes


@ex.command
def profile(_seed, _config):
    model, optimizer, scheduler, train_loader, test_loader = init(_seed, _config)
    model.train()

    with torch.profiler.profile(
            activities=[torch.profiler.ProfilerActivity.CPU,
                        torch.profiler.ProfilerActivity.CUDA],
            schedule=torch.profiler.schedule(
                wait=0,
                warmup=1,
                active=_config['epochs']
            ),
            on_trace_ready=torch.profiler.tensorboard_trace_handler('.')
            ) as prof:
        for epoch in range(_config['epochs']):
            print(f'Train Epoch: {epoch}')        
            train_epoch(model, train_loader, optimizer, _config['log_interval'])
            prof.step()


@ex.automain
def train(_run, _seed, _config):
    wandb.config.update(_config)
    model, optimizer, scheduler, train_loader, test_loader = init(_seed, _config)
    model.train()

    # demonstation
    _run.open_resource('./data//MNIST/raw/t10k-images-idx3-ubyte.gz')

    for epoch in range(_config['epochs']):
        print(f'Train Epoch: {epoch}')        
        loss = train_epoch(model, train_loader, optimizer, epoch, _config['log_interval'], _run)
        _run.log_scalar('train.loss', loss, epoch)
        wandb.log({'train.loss': loss})

        scheduler.step()
        loss = test_epoch(model, test_loader, epoch, _run)
        _run.log_scalar('test.loss', loss, epoch)
        wandb.log({'test.loss': loss})

        wandb.watch(model)
        if _config['model_path'] is not None:
            fname = _config['model_path'] + f'/model_epoch{epoch}.pt'
            torch.save(model.state_dict(), fname)
            _run.add_artifact(fname, name=f'model_epoch{epoch}.pt', content_type="application/octet-stream")
            wandb.log_artifact(fname, name=f'model_epoch{epoch}.pt', type="application-octet-stream")
