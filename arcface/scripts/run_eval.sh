#!/bin/bash

echo "=============================================================================================================="
echo "Please run the script as: "
echo "bash run.sh EVAL_PATH CKPT_PATH"
echo "For example: bash run.sh path/evalset path/ckpt"
echo "It is better to use the absolute path."
echo "=============================================================================================================="

EVAL_PATH=$1
CKPT_PATH=$2

python val.py \
--ckpt_url "$CKPT_PATH" \
--device_id 1 \
--eval_url "$EVAL_PATH" \
--target lfw,cfp_fp,agedb_30,calfw,cplfw \
> eval.log 2>&1 &
