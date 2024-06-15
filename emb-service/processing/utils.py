import torch


def autodevice():
    return 'cuda' if torch.cuda.is_available() else 'cpu'
