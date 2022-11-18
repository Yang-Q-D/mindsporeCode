#!/bin/bash


echo "=============================================================================================================="
echo "Please run the script as: "
echo "bash run.sh DATA_PATH EVAL_PATH CKPT_PATH RANK_SIZE"
echo "For example: bash run.sh /path/dataset /path/evalset /path/ckpt 8"
echo "It is better to use the absolute path."
echo "=============================================================================================================="
set -e

export DEVICE_NUM=$4
export RANK_SIZE=$4
export DATASET_NAME=$1
export EVAL_PATH=$2
export CKPT_PATH=$3
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

rm -rf ./train_parallel
mkdir ./train_parallel
cp -r ./src/ ./train_parallel
# shellcheck disable=SC2035
cp *.py ./train_parallel
cd ./train_parallel
env > env.log
echo "start training"
    mpirun -n $4 --allow-run-as-root --output-filename log_output --merge-stderr-to-stdout \
    python train.py --device_num $4 --device_target GPU --data_url $1 \
    --ckpt_url $3 --eval_url $2 \
    --pretrained \
    > train.log 2>&1 &
