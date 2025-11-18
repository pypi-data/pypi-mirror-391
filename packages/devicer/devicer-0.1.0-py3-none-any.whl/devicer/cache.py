import torch


def clear_torch():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
