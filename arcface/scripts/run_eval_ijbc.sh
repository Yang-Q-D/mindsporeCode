#!/bin/bash

echo "=============================================================================================================="
echo "Please run the script as: "
echo "bash run.sh EVAL_PATH CKPT_PATH"
echo "For example: bash run.sh path/evalset path/ckpt"
echo "It is better to use the absolute path."
echo "=============================================================================================================="

EVAL_PATH=$1
CKPT_PATH=$2

python eval_ijbc.py \
--model-prefix "$CKPT_PATH" \
--image-path "$EVAL_PATH" \
--result-dir ms1mv2_arcface_r100 \
--batch-size 128 \
--job ms1mv2_arcface_r100 \
--target IJBC \
--network iresnet100 \
> eval.log 2>&1 &
