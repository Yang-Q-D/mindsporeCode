#!/bin/bash



if [ $# -ne 2 ]
then
  echo "Wrong parameter format."
  echo "Usage:"
  echo "         bash $0 [INPUT_AIR_PATH] [AIPP_PATH] [OUTPUT_OM_PATH_NAME]"
  echo "Example: "
  echo "         bash convert_om.sh  xxx.air xx"

  exit 1
fi

model_path=$1
output_model_name=$2

atc \
--model=$model_path \
--framework=1 \
--output=$output_model_name \
--input_format=NCHW \
--input_shape="x:1,3,112,112" \
--enable_small_channel=1 \
--log=error \
--soc_version=Ascend310

#--insert_op_conf=$aipp_cfg_file