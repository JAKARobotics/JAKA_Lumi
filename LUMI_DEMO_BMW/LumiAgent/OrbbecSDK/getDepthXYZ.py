# ******************************************************************************
#  Copyright (c) 2023 Orbbec 3D Technology, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http:# www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ******************************************************************************
import os
import sys
import cv2
import numpy as np
import time

# Add pyorbbecsdk build directory to Python path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_pyorbbecsdk_build_path = os.path.join(_current_dir, 'pyorbbecsdkMain', 'build')
if os.path.exists(_pyorbbecsdk_build_path) and _pyorbbecsdk_build_path not in sys.path:
    sys.path.insert(0, _pyorbbecsdk_build_path)

from pyorbbecsdk import *
from OrbbecSDK.orbbecUtils import frame_to_bgr_image

ESC_KEY = 27
PRINT_INTERVAL = 1  # seconds
MIN_DEPTH = 20  # 20mm
MAX_DEPTH = 10000  # 10000mm

class TemporalFilter:
    def __init__(self, alpha):
        self.alpha = alpha
        self.previous_frame = None

    def process(self, frame):
        if self.previous_frame is None:
            result = frame
        else:
            result = cv2.addWeighted(frame, self.alpha, self.previous_frame, 1 - self.alpha, 0)
        self.previous_frame = result
        return result

def pix2WorldPos(align_mode = "SW",enable_sync = True):
    pipeline = Pipeline()
    device = pipeline.get_device()
    device_info = device.get_device_info()
    device_pid = device_info.get_pid()

    config = Config()

    # align_mode = "HW" # align mode, HW=hardware mode,SW=software mode,NONE=disable align
    # enable_sync = True  # enable sync
    try:
        profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        color_profile = profile_list.get_default_video_stream_profile()
        config.enable_stream(color_profile)
        profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        assert profile_list is not None
        depth_profile = profile_list.get_default_video_stream_profile()
        assert depth_profile is not None
        print("color profile : {}x{}@{}_{}".format(color_profile.get_width(),
                                                   color_profile.get_height(),
                                                   color_profile.get_fps(),
                                                   color_profile.get_format()))
        print("depth profile : {}x{}@{}_{}".format(depth_profile.get_width(),
                                                   depth_profile.get_height(),
                                                   depth_profile.get_fps(),
                                                   depth_profile.get_format()))
        config.enable_stream(depth_profile)
    except Exception as e:
        print(e)
        return
    if align_mode == 'HW':
          if device_pid == 0x066B:
            #Femto Mega does not support hardware D2C, and it is changed to software D2C
             config.set_align_mode(OBAlignMode.SW_MODE)
          else:
             config.set_align_mode(OBAlignMode.HW_MODE)
    elif align_mode == 'SW':
        config.set_align_mode(OBAlignMode.SW_MODE)
    else:
        config.set_align_mode(OBAlignMode.DISABLE)
    if enable_sync:
        try:
            pipeline.enable_frame_sync()
        except Exception as e:
            print(e)
    try:
        pipeline.start(config)
    except Exception as e:
        print(e)
        return
    flag=True
    while flag:
        if flag==False:
            break
        try:
            frames: FrameSet = pipeline.wait_for_frames(20000)
            if frames is None:
                continue
            color_frame = frames.get_color_frame()
            if color_frame is None:
                continue
            # covert to RGB format
            color_image = frame_to_bgr_image(color_frame)
            if color_image is None:
                print("failed to convert frame to image")
                continue
            depth_frame = frames.get_depth_frame()
            if depth_frame is None:
                continue

            width = depth_frame.get_width()
            height = depth_frame.get_height()
            scale = depth_frame.get_depth_scale()

            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            depth_data = depth_data.reshape((height, width))
            depth_data = depth_data.astype(np.float32) * scale

            temporal_filter = TemporalFilter(alpha=0.5)
            depth_data = np.where((depth_data > MIN_DEPTH) & (depth_data < MAX_DEPTH), depth_data, 0)
            depth_data = depth_data.astype(np.uint16)
            # Apply temporal filtering
            depth_data = temporal_filter.process(depth_data)
            # center_distance = depth_data[center_y, center_x]

            depth_image = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            depth_image = cv2.applyColorMap(depth_image, cv2.COLORMAP_JET)


            # overlay color image on depth image
            depth_image = cv2.addWeighted(color_image, 0.5, depth_image, 0.5, 0)
            flag = False
            return color_image, depth_data, depth_image

            # cv2.imshow("SyncAlignViewer ", depth_image)
            # key = cv2.waitKey(1)
            # if key == ord('q') or key == ESC_KEY:
            #     break
        # except KeyboardInterrupt:
        #     break
        except:
            print("【获取图像数据失败，正在重新获取图像数据......】")
    pipeline.stop()


if __name__ == "__main__":
    pix2WorldPos()
