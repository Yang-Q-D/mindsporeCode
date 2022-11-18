"""
python lr_generator.py
"""
import numpy as np
from mindspore import Tensor
from src.config import cfg


def lr_generator(lr_init, total_epochs, steps_per_epoch):
    lr_each_step = []
    for i in range(total_epochs):
        if i in cfg.schedule:
            lr_init *= cfg.gamma
        for _ in range(steps_per_epoch):
            lr_each_step.append(lr_init)
    lr_each_step = np.array(lr_each_step).astype(np.float32)
    return Tensor(lr_each_step)
