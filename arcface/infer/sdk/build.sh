#!/bin/bash

# The number of parameters must be 2.
if [ $# -ne 4 ]
then
  echo "Wrong parameter format."
  echo "Usage:"
  echo "         bash $0 [INPUT_PATH] [PIPELINE_PATH] [OUTPUT_PATH] [DATASET_NAME]"
  echo "Example: "
  echo "         bash build.sh ../data/input/data/ ../data/config/arcface.pipeline ../data/sdk_out/ lfw"

  exit 1
fi

# The path of a folder containing eval images.
image_path=$1
# The path of pipeline file.
pipeline_dir=$2
# The path of a folder used to store all results.
result_dir=$3
# The name of pipeline eval dataset.
dataset_name=$4

if [ ! -d $image_path ]
then
  echo "Please input the correct directory containing images."
  exit
fi

if [ ! -d $result_dir ]
then
  mkdir -p $result_dir
fi

set -e

CUR_PATH=$(cd "$(dirname "$0")" || { warn "Failed to check path/to/run.sh" ; exit ; } ; pwd)
echo "enter $CUR_PATH"

# Simple log helper functions
info() { echo -e "\033[1;34m[INFO ][MxStream] $1\033[1;37m" ; }
warn() { echo >&2 -e "\033[1;31m[WARN ][MxStream] $1\033[1;37m" ; }

export LD_LIBRARY_PATH=${MX_SDK_HOME}/lib:${MX_SDK_HOME}/opensource/lib:${MX_SDK_HOME}/opensource/lib64:/usr/local/Ascend/ascend-toolkit/latest/acllib/lib64:${LD_LIBRARY_PATH}

#to set PYTHONPATH, import the StreamManagerApi.py
export PYTHONPATH=$PYTHONPATH:${MX_SDK_HOME}/python

if [ ! "${MX_SDK_HOME}" ]
then
export GST_PLUGIN_SCANNER=${MX_SDK_HOME}/opensource/libexec/gstreamer-1.0/gst-plugin-scanner
fi

if [ ! "${MX_SDK_HOME}" ]
then
export GST_PLUGIN_PATH=${MX_SDK_HOME}/opensource/lib/gstreamer-1.0:${MX_SDK_HOME}/lib/plugins
fi

python3.7 main_sdk_jpg.py --eval_url=$image_path \
                  --PL_PATH=$pipeline_dir \
                  --result_url=$result_dir \
                  --target=$dataset_name
                  
exit 0