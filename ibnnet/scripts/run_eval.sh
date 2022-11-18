#!/bin/bash


DATA_PATH=$1
CHECKPOINT=$2

python eval.py  \
    --device_id 0 \
    --checkpoint "$CHECKPOINT" \
    --eval_url "$DATA_PATH" \
    > eval.log 2>&1 &
echo "start evaluation"
