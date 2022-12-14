"""
python start.py
"""
import os
import glob
import argparse
import numpy as np
import mindspore.nn as nn
import mindspore.ops as ops
from mindspore import export
from mindspore import context, Tensor
from mindspore import dtype as mstype
from mindspore.parallel import set_algo_parameters
from mindspore.train.model import Model, ParallelMode
from mindspore.communication import management as MutiDev
from mindspore.communication.management import init, get_rank
from mindspore.parallel import _cost_model_context as cost_model_context
from mindspore.train.serialization import load_checkpoint, load_param_into_net
from mindspore.train.callback import ModelCheckpoint, CheckpointConfig, LossMonitor, TimeMonitor
from src.dataset import create_dataset
from src.iresnet import iresnet100
from src.loss import PartialFC

DATA_PATH = "/cache/data_path_"
CKPT_PATH = "/cache/ckpt/"

parser = argparse.ArgumentParser(description='Mindspore ImageNet Training')
# Datasets
parser.add_argument('--train_url', default='', type=str,
                    help='output path')
parser.add_argument('--data_url', default='', type=str)
# Optimization options
parser.add_argument('--epochs', default=25, type=int, metavar='N',
                    help='number of total epochs to run')
parser.add_argument('--num_classes', default=85742, type=int, metavar='N',
                    help='num of classes')
parser.add_argument('--batch_size', default=64, type=int, metavar='N',
                    help='train batchsize (default: 256)')
parser.add_argument('--lr', '--learning-rate', default=0.08, type=float,
                    metavar='LR', help='initial learning rate')
parser.add_argument('--schedule', type=int, nargs='+', default=[10, 16, 21],
                    help='Decrease learning rate at these epochs.')
parser.add_argument('--gamma', type=float, default=0.1,
                    help='LR is multiplied by gamma on schedule.')
parser.add_argument('--momentum', default=0.9, type=float, metavar='M',
                    help='momentum')
parser.add_argument('--weight-decay', '--wd', default=1e-4, type=float,
                    metavar='W', help='weight decay (default: 1e-4)')
# Device options
parser.add_argument('--device_target', type=str,
                    default='Ascend', choices=['GPU', 'Ascend', 'CPU'])
parser.add_argument('--device_num', type=int, default=1)
parser.add_argument('--device_id', type=int, default=0)
parser.add_argument('--modelarts', type=bool, default=True)

args = parser.parse_args()


def lr_generator(lr_init, total_epochs, steps_per_epoch):
    '''lr_generator
    '''
    lr_each_step = []
    for i in range(total_epochs):
        if i in args.schedule:
            lr_init *= args.gamma
        for _ in range(steps_per_epoch):
            lr_each_step.append(lr_init)
    lr_each_step = np.array(lr_each_step).astype(np.float32)
    return Tensor(lr_each_step)


class MyNetWithLoss(nn.Cell):
    '''
    WithLossCell
    '''

    def __init__(self, backbone, cfg):
        super(MyNetWithLoss, self).__init__(auto_prefix=False)
        self._backbone = backbone.to_float(mstype.float16)
        self._loss_fn = PartialFC(num_classes=cfg.num_classes,
                                  world_size=cfg.device_num).to_float(mstype.float32)
        self.L2Norm = ops.L2Normalize(axis=1)

    def construct(self, data, label):
        out = self._backbone(data)
        loss = self._loss_fn(out, label)
        return loss


def frozen_to_air(modelnet, modelargs):
    param_dict = load_checkpoint(modelargs.get("ckpt_file"))
    load_param_into_net(modelnet, param_dict)

    input_arr = Tensor(
        np.zeros([modelargs.get("batch_size"), 3, modelargs.get("height"), modelargs.get("width")], np.float32))
    export(modelnet, input_arr, file_name=modelargs.get("file_name"), file_format=modelargs.get("file_format"))


if __name__ == "__main__":
    ckpt_save_path = CKPT_PATH
    train_epoch = args.epochs
    target = args.device_target
    context.set_context(mode=context.GRAPH_MODE,
                        device_target=target, save_graphs=False)
    if args.device_num > 1:
        device_id = int(os.getenv('DEVICE_ID'))
        context.set_context(device_id=device_id)
    else:
        context.set_context(device_id=args.device_id)
    if args.device_num > 1:
        context.set_auto_parallel_context(parallel_mode=ParallelMode.DATA_PARALLEL,
                                          gradients_mean=True,
                                          )
        cost_model_context.set_cost_model_context(device_memory_capacity=32.0 * 1024.0 * 1024.0 * 1024.0,
                                                  costmodel_gamma=0.001,
                                                  costmodel_beta=280.0)
        set_algo_parameters(elementwise_op_strategy_follow=True)
        init()
        ckpt_save_path = CKPT_PATH + "ckpt_" + str(get_rank()) + "/"
        print("ckpt_save_path finish copy to %s" % ckpt_save_path)
    if args.modelarts:
        import moxing as mox

        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH, 0o755)
        mox.file.copy_parallel(src_url=args.data_url, dst_url=DATA_PATH)
        print("training data finish copy to %s" % DATA_PATH)

        mox.file.copy_parallel(
            src_url=args.data_url, dst_url=DATA_PATH + os.getenv('DEVICE_ID'))
        zip_command = "unzip -o -q " + DATA_PATH + os.getenv('DEVICE_ID') + "/MS1M.zip -d " + DATA_PATH + os.getenv(
            'DEVICE_ID')
        os.system(zip_command)
        train_dataset = create_dataset(dataset_path=DATA_PATH + os.getenv('DEVICE_ID') + '/MS1M/',
                                       do_train=True,
                                       repeat_num=1, batch_size=args.batch_size, target=target)
    else:
        train_dataset = create_dataset(dataset_path=args.data_url, do_train=True,
                                       repeat_num=1, batch_size=args.batch_size, target=target)
    step = train_dataset.get_dataset_size()
    lr = lr_generator(args.lr, train_epoch, steps_per_epoch=step)
    net = iresnet100()
    train_net = MyNetWithLoss(net, args)
    optimizer = nn.SGD(params=train_net.trainable_params(), learning_rate=lr / 512 * args.batch_size * args.device_num,
                       momentum=args.momentum, weight_decay=args.weight_decay)
    model = Model(train_net, optimizer=optimizer)

    time_cb = TimeMonitor(data_size=train_dataset.get_dataset_size())
    loss_cb = LossMonitor()
    cb = [time_cb, loss_cb]
    config_ck = CheckpointConfig(
        save_checkpoint_steps=60, keep_checkpoint_max=5)
    prefix = "ArcFace"
    if args.modelarts:
        ckpt_cb = ModelCheckpoint(prefix="ArcFace", config=config_ck,
                                  directory=ckpt_save_path)
        cb.append(ckpt_cb)
    else:
        if args.device_num == 8 and MutiDev.get_rank() % 8 == 0:
            ckpt_cb = ModelCheckpoint(prefix="ArcFace", config=config_ck,
                                      directory=args.train_url)
            cb.append(ckpt_cb)
        if args.device_num == 1:
            ckpt_cb = ModelCheckpoint(prefix="ArcFace", config=config_ck,
                                      directory=args.train_url)
            cb.append(ckpt_cb)
    model.train(train_epoch, train_dataset, callbacks=cb, dataset_sink_mode=True)

    if not os.path.isdir(CKPT_PATH):
        os.makedirs(CKPT_PATH)
    ckpt_list = glob.glob(CKPT_PATH + prefix + "*.ckpt")
    if not ckpt_list:
        print("ckpt file not generated.")

    ckpt_list.sort(key=os.path.getmtime)
    ckpt_model = ckpt_list[-1]
    net = iresnet100()
    frozen_to_air_args = {'ckpt_file': ckpt_model,
                          'batch_size': args.batch_size,
                          'height': 112,
                          'width': 112,
                          'file_name': (CKPT_PATH + prefix),
                          'file_format': 'AIR'}
    frozen_to_air(net, frozen_to_air_args)

    if args.modelarts:
        mox.file.copy_parallel(src_url=CKPT_PATH, dst_url=args.train_url)
