#!/bin/bash

echo "=============================================================================================================="
echo "Please run the script as: "
echo "bash run.sh DATA_PATH RANK_SIZE"
echo "For example: bash run.sh /path/dataset 8"
echo "It is better to use the absolute path."
echo "=============================================================================================================="
set -e

export DEVICE_NUM=$2
export RANK_SIZE=$2
export DATASET_NAME=$1
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

rm -rf ./train_parallel
mkdir ./train_parallel
cp -r ./src/ ./train_parallel
# shellcheck disable=SC2035
cp *.py ./train_parallel
cd ./train_parallel
env > env.log
echo "start training"
    mpirun -n $2 --allow-run-as-root --output-filename log_output --merge-stderr-to-stdout \
    python train.py --device_num $2 --device_target GPU --data_url $1 \
    > train.log 2>&1 &
