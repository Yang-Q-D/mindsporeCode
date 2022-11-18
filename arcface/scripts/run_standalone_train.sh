#!/bin/bash


echo "=============================================================================================================="
echo "Please run the script as: "
echo "bash run.sh DATA_PATH"
echo "For example: bash run.sh path/MS1M DEVICE_ID"
echo "It is better to use the absolute path."
echo "=============================================================================================================="

# shellcheck disable=SC2034
DATA_PATH=$1
export DEVICE_ID=$2
python train.py  \
--data_url $DATA_PATH \
--device_num 1 \
> train.log 2>&1 &