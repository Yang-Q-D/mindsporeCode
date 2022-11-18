#!/bin/bash


echo "=============================================================================================================="
echo "Please run the script as: "
echo "bash run.sh DATA_PATH EVAL_PATH CKPT_PATH"
echo "For example: bash run.sh /path/dataset /path/evalset /path/ckpt device_id"
echo "It is better to use the absolute path."
echo "=============================================================================================================="
EXE_PATH=$(pwd)
DATA_PATH=$1
EVAL_PATH=$2
CKPT_PATH=$3
DEVICEID=$4

rm -rf "train$4"
mkdir "train$4"
cp -r ./src/ ./"train$4"
cp train.py ./"train$4"
cd ./"train$4"
export DEVICE_ID=$4
export RANK_ID=$4
echo "start training for device $4"
env > env$4.log
python train.py  \
    --epochs 100 \
    --train_url "$EXE_PATH" \
    --data_url "$DATA_PATH" \
    --eval_url "$EVAL_PATH" \
    --ckpt_url "$CKPT_PATH" \
    --pretrained \
    --device_id $DEVICEID \
    > train.log 2>&1 &
echo "start training"
cd ../
