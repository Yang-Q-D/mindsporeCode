#ifndef ARCFACE_MINSPORE_PORT_H
#define ARCFACE_MINSPORE_PORT_H
#include <algorithm>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include <opencv2/opencv.hpp>


#include "MxBase/CV/Core/DataType.h"
#include "MxBase/DvppWrapper/DvppWrapper.h"
#include "MxBase/ErrorCode/ErrorCode.h"
#include "MxBase/ModelInfer/ModelInferenceProcessor.h"
#include "MxBase/PostProcessBases/ObjectPostProcessBase.h"
#include "MxBase/Tensor/TensorContext/TensorContext.h"

struct InitParam {
  uint32_t deviceId;
  bool softmax;
  bool checkTensor;
  std::string modelPath;
};

class ArcFaceOpencv {
 public:
  static const int IMG_C = 3;
  static const int IMG_H = 112;
  static const int IMG_W = 112;
  static const int FEATURE_NUM = 512;
  APP_ERROR Init(const InitParam &initParam);
  APP_ERROR DeInit();
  APP_ERROR ReadImage(const std::string &imgPath, cv::Mat *imageMat);
  APP_ERROR ResizeImage(const cv::Mat &srcImageMat,
                        uint8_t (&imageArray)[IMG_H][IMG_W][IMG_C]);
  APP_ERROR NormalizeImage(uint8_t (&imageArray)[IMG_H][IMG_W][IMG_C],
                           float (&imageArrayNormal)[IMG_H][IMG_W][IMG_C]);
  APP_ERROR ArrayToTensorBase(float (&imageArray)[IMG_H][IMG_W][IMG_C],
                              MxBase::TensorBase *tensorBase);
  APP_ERROR Inference(const std::vector<MxBase::TensorBase> &inputs,
                      std::vector<MxBase::TensorBase> *outputs);
  APP_ERROR Process(const std::string &imgPath, const std::string &resultPath);
  // get infer time
  double GetInferCostMilliSec() const { return inferCostTimeMilliSec; }

 private:
  APP_ERROR SaveResult(MxBase::TensorBase *tensor,
                       const std::string &resultpath);

 private:
  std::shared_ptr<MxBase::DvppWrapper> dvppWrapper_;
  std::shared_ptr<MxBase::ModelInferenceProcessor> model_;
  MxBase::ModelDesc modelDesc_;
  uint32_t deviceId_ = 0;
  // infer time
  double inferCostTimeMilliSec = 0.0;
};

#endif
