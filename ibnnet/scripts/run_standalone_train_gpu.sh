#!/bin/bash


echo "=============================================================================================================="
echo "Please run the script as: "
echo "bash run.sh DATA_PATH EVAL_PATH CKPT_PATH"
echo "For example: bash run.sh /path/dataset /path/evalset /path/ckpt"
echo "It is better to use the absolute path."
echo "=============================================================================================================="
EXE_PATH=$(pwd)
DATA_PATH=$1
EVAL_PATH=$2
CKPT_PATH=$3

python train.py  \
    --epochs 100 \
    --train_url "$EXE_PATH" \
    --data_url "$DATA_PATH" \
    --eval_url "$EVAL_PATH" \
    --ckpt_url "$CKPT_PATH" \
    --device_target "GPU" \
    --pretrained \
    > train.log 2>&1 &
echo "start training"
cd ../
