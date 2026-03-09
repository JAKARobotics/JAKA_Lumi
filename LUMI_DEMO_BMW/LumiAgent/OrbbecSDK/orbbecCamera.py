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

class Camera():
    print('orbbec camera-------')
    def __init__(self, align_mode="SW", enable_sync=True, serial_number=None):
        """基于官方 quick_start 示例的相机封装，可通过序列号指定设备。"""
        self.pipeline = None
        try:
            ctx = Context()
            dev_list = ctx.query_devices()
            device = None
            count = dev_list.get_count() if hasattr(dev_list, "get_count") else 0
            for idx in range(count):
                # pyorbbecsdk2 支持下标访问
                try:
                    dev = dev_list[idx]
                except Exception:
                    dev = None
                # 兼容旧接口
                if dev is None and hasattr(dev_list, "get_device"):
                    try:
                        dev = dev_list.get_device(idx)
                    except Exception:
                        dev = None
                if dev is None:
                    continue
                if serial_number and dev.get_device_info().get_serial_number() == serial_number:
                    device = dev
                    break
                if device is None:
                    device = dev  # 默认取第一台

            if device is not None:
                try:
                    self.pipeline = Pipeline(device)
                except Exception:
                    self.pipeline = Pipeline()
            else:
                self.pipeline = Pipeline()
        except Exception:
            self.pipeline = Pipeline()

        # 直接使用默认配置启动（与官方 quick_start 一致）
        try:
            self.pipeline.start()
        except Exception:
            pass

    def getColorImage(self):
        # print('--1--')
        # 获取一帧图像
        while True:
            try:
                frames: FrameSet = self.pipeline.wait_for_frames(1000)
                if frames is None:
                    print('frame is none')
                    continue

                color_frame = frames.get_color_frame()
                if color_frame is None:
                    print('color frame is None')
                    continue

                if color_frame is not None:
                    # covert to RGB format
                    color_image = frame_to_bgr_image(color_frame)
                    return color_image
                break
            except Exception as e:
                print("e: ",e)
                return []
    def getColorDepthData(self, timeout_ms=1000, retry=10):
        """获取一帧彩色和深度数据，参考官方 quick_start 处理。"""
        for _ in range(retry):
            try:
                frames: FrameSet = self.pipeline.wait_for_frames(timeout_ms)
                if frames is None:
                    continue

                color_frame = frames.get_color_frame()
                depth_frame = frames.get_depth_frame()
                if color_frame is None or depth_frame is None:
                    continue

                color_image = frame_to_bgr_image(color_frame)
                if color_image is None:
                    continue

                if depth_frame.get_format() != OBFormat.Y16:
                    # 只处理 Y16 深度
                    continue

                width = depth_frame.get_width()
                height = depth_frame.get_height()
                scale = depth_frame.get_depth_scale()

                depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16).reshape((height, width))
                depth_data = depth_data.astype(np.float32) * scale
                depth_data = np.where((depth_data > MIN_DEPTH) & (depth_data < MAX_DEPTH), depth_data, 0).astype(np.uint16)

                temporal_filter = TemporalFilter(alpha=0.5)
                depth_data = temporal_filter.process(depth_data)

                depth_image = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                depth_image = cv2.applyColorMap(depth_image, cv2.COLORMAP_JET)

                return color_image, depth_data, depth_image
            except Exception:
                continue
        return [], [], []

    def close(self):
        self.pipeline.stop()


if __name__ == "__main__":
    orbbecs=Camera()
    # orbbecs.getColorDepthData()
    # color_image, depth_data, depth_image=orbbecs.getColorDepthData()
    color_image=orbbecs.getColorImage()
    
    orbbecs.close()
    print(color_image)
    # print(depth_data)
    # print(depth_image)

    cv2.rectangle(color_image, (10, 10),
                  (100, 100), (0, 0, 255), 2)
    # xx=[822,500]
    xx = [756.0,423.0]
    # tmp=depth_data[int(xx[1]),int(xx[0])]

    # print(tmp)
    cv2.imshow("SyncAlignViewer ", color_image)
    cv2.waitKey(1000)
    # cv2.imshow("SyncAlignViewer ", depth_image)
    # cv2.waitKey(1000)

    # color_image=orbbecs.getColorImage()
    # orbbecs.close()
    # print(len(color_image))
    # cv2.imshow("SyncAlignViewer ", color_image)
    # cv2.waitKey(1000)
