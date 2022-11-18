#!/bin/bash


echo "=============================================================================================================="
echo "Please run the script as: "
echo "bash run.sh DATA_PATH EVAL_PATH CKPT_PATH RANK_SIZE"
echo "For example: bash run.sh /path/dataset /path/evalset /path/ckpt 8"
echo "It is better to use the absolute path."
echo "=============================================================================================================="
DATA_PATH=$1
export DATA_PATH=${DATA_PATH}
EVAL_PATH=$2
export EVAL_PATH=${EVAL_PATH}
# shellcheck disable=SC2034
CKPT_PATH=$3
export CKPT_PATH=${CKPT_PATH}
RANK_SIZE=$4

EXEC_PATH=$(pwd)
echo "$EXEC_PATH"

test_dist_8pcs()
{
    export RANK_TABLE_FILE=${EXEC_PATH}/rank_table_8pcs.json
    export RANK_SIZE=8
}

test_dist_2pcs()
{
    export RANK_TABLE_FILE=${EXEC_PATH}/rank_table_2pcs.json
    export RANK_SIZE=2
}

test_dist_${RANK_SIZE}pcs

for((i=0;i<RANK_SIZE;i++))
do
    rm -rf device$i
    mkdir device$i
    cp -r ./src/ ./device$i
    cp train.py ./device$i
    cd ./device$i
    export DEVICE_ID=$i
    export RANK_ID=$i
    echo "start training for device $i"
    env > env$i.log
    python train.py --data_url "$DATA_PATH" --eval_url "$EVAL_PATH" --ckpt_url "$CKPT_PATH" \
    --device_num "$RANK_SIZE" --pretrained > train.log$i 2>&1 &
    cd ../
done
echo "start training"
cd ../
