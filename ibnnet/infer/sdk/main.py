# coding=utf-8

"""
310 infer script
"""

import json
import os
import sys

from StreamManagerApi import StreamManagerApi
from StreamManagerApi import MxDataInput

PL_PATH = '../data/config/ibnnet.pipeline'

if __name__ == '__main__':
    # init stream manager
    stream_manager_api = StreamManagerApi()
    ret = stream_manager_api.InitManager()
    if ret != 0:
        print("Failed to init Stream manager, ret=%s" % str(ret))
        exit()

    # create streams by pipeline config file
    with open(PL_PATH, 'rb') as f:
        pipelineStr = f.read()
    ret = stream_manager_api.CreateMultipleStreams(pipelineStr)

    if ret != 0:
        print("Failed to create Stream, ret=%s" % str(ret))
        exit()

    # Construct the input of the stream
    data_input = MxDataInput()

    dir_name = sys.argv[1]
    res_dir_name = sys.argv[2]
    file_list = os.listdir(dir_name)
    if not os.path.exists(res_dir_name):
        os.makedirs(res_dir_name)

    for file_name in file_list:
        print("Processing file: ", file_name)

        file_path = os.path.join(dir_name, file_name)
        if not (file_name.lower().endswith(".jpg") or file_name.lower().endswith(".jpeg")):
            continue

        with open(file_path, 'rb') as f:
            data_input.data = f.read()

        empty_data = []
        stream_name = b'im_ibnnet'
        in_plugin_id = 0
        unique_id = stream_manager_api.SendData(stream_name, in_plugin_id, data_input)
        if unique_id < 0:
            print("Failed to send data to stream.")
            exit()
        # Obtain the inference result by specifying streamName and uniqueId.
        infer_result = stream_manager_api.GetResult(stream_name, unique_id)
        if infer_result.errorCode != 0:
            print("GetResultWithUniqueId error. errorCode=%d, errorMsg=%s" % (
                infer_result.errorCode, infer_result.data.decode()))
            exit()
        # print the infer result
        infer_res = infer_result.data.decode()
        print("process img: {}, infer result: {}".format(file_name, infer_res))

        load_dict = json.loads(infer_result.data.decode())
        file_real_name = file_name.split('.')[0]
        if load_dict.get('MxpiClass') is None:
            with open(res_dir_name + "/" + file_real_name + '.empty', 'w') as f_write:
                f_write.write("")
            continue
        res_vec = load_dict.get('MxpiClass')

        with open(res_dir_name + "/" + file_real_name + '.res', 'w') as f_write:
            res_list = [str(item.get("classId")) + " " for item in res_vec]
            f_write.writelines(res_list)
            f_write.write('\n')

    # destroy streams
    stream_manager_api.DestroyAllStreams()
