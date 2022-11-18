"""
python start.py
"""
import os
import glob
import argparse
import numpy as np
from mindspore import export
from mindspore import Tensor
from mindspore.train.serialization import load_checkpoint, load_param_into_net
from src.iresnet import iresnet100

DATA_PATH = "/cache/data_path_"
CKPT_PATH = "/cache/ckpt/"

parser = argparse.ArgumentParser(description='Mindspore ImageNet Training')
parser.add_argument('--train_url', default='', type=str,
                    help='output path')
parser.add_argument('--data_url', default='', type=str)
# Datasets
parser.add_argument('--batch_size', default=1, type=int, metavar='N',
                    help='train batchsize (default: 256)')

parser.add_argument('--modelarts', type=bool, default=True)
args = parser.parse_args()


def frozen_to_air(modelnet, modelargs):
    param_dict = load_checkpoint(modelargs.get("ckpt_file"))
    load_param_into_net(modelnet, param_dict)

    input_arr = Tensor(
        np.zeros([modelargs.get("batch_size"), 3, modelargs.get("height"), modelargs.get("width")], np.float32))
    export(modelnet, input_arr, file_name=modelargs.get("file_name"), file_format=modelargs.get("file_format"))


if __name__ == "__main__":
    import moxing as mox

    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH, 0o755)
    mox.file.copy_parallel(src_url=args.data_url, dst_url=CKPT_PATH)
    prefix = "ArcFace"
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
