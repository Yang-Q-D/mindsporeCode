"""
python config.py
"""
from easydict import EasyDict

cfg = EasyDict({
    "class_num": 1000,
    "train_batch": 64,
    "test_batch": 100,
    "momentum": 0.9,
    "weight_decay": 1e-4,
    "epoch_size": 1,
    "pretrain_epoch_size": 0,
    "save_checkpoint": True,
    "save_checkpoint_epochs": 10,
    "keep_checkpoint_max": 10,
    "save_checkpoint_path": "./",
    "warmup_epochs": 5,
    "lr": 0.1,
    "gamma": 0.1,
    "schedule": [30, 60, 90]
})
