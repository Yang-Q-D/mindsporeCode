#!/bin/bash


echo "=============================================================================================================="
echo "Please run the script as: "
echo "bash run.sh DATA_PATH"
echo "For example: bash run.sh /path/dataset"
echo "It is better to use the absolute path."
echo "=============================================================================================================="
EXE_PATH=$(pwd)
DATA_PATH=$1

python train.py  \
    --epochs 25 \
    --train_url "$EXE_PATH" \
    --data_url "$DATA_PATH" \
    --device_target "GPU" \
    > train.log 2>&1 &
echo "start training"
cd ../
