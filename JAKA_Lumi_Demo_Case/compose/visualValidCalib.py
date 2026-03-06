import json
from utilfs.tools import pixel_to_world, loadJsonFile, generatorNearPoints
# from OrbbecSDK.pyorbbecsdk import *
from pyorbbecsdk import *
# from OrbbecSDK.orbbecCamera import Camera
# from pyorbbecsdk import *
from OrbbecSDK.orbbecUtils import frame_to_bgr_image
# from pyorbbecsdk.orbbecUtils import frame_to_bgr_image
# from pyorbbecsdk import *
# from orbbecUtils import frame_to_bgr_image
import cv2
import numpy as np
import sys
import time
from utilfs.jaka import *
# from utils.log import *

PI=3.1415926

ESC_KEY = 27
PRINT_INTERVAL = 1  # seconds
MIN_DEPTH = 20  # 20mm
MAX_DEPTH = 10000  # 10000mm


# TemporalFilter 类，实现一种时间滤波器。
# 时间滤波器通常用于视频处理中，用于减少图像的噪声和闪烁，提高图像的平滑性和视觉效果
# 通过将当前帧与前一帧进行混合来减少噪声和平滑图像。
class TemporalFilter:
    def __init__(self, alpha):
        # alpha：浮点数，表示滤波器的权重。alpha值通常在0到1间，决定当前帧与前一帧在滤波过程中的权重比例
        self.alpha = alpha
        # 用于存储上一帧的图像数据，初始值为 None
        self.previous_frame = None

    # 类的一个方法，用于处理传入的图像帧。
    # frame：传入的当前帧图像。
    def process(self, frame):
        # None（即没有前一帧），则直接将当前帧作为结果
        if self.previous_frame is None:
            result = frame
        else:
            # 如果有前一帧，则用cv2.addWeighted函数将当前帧与前一帧进行加权平均混合。
            # frame：当前帧。
            # self.alpha：当前帧的权重。
            # self.previous_frame：前一帧。
            # 1 - self.alpha：前一帧的权重。
            # 0：伽马校正参数（通常设置为 0）
            result = cv2.addWeighted(frame, self.alpha, self.previous_frame, 1 - self.alpha, 0)
        # 将处理后的结果存储为下一帧的前一帧。
        self.previous_frame = result
        # 返回处理后的图像帧。
        return result

with open("/home/jam/JAKA_WORK/LUMI/upload_files/LUMI_DEMO-v1/conf/conf/Cali.json", "r") as f:
    data = json.load(f)
print("CalibParams：",data)

# with open("./conf/CalibParams.json", "r") as f:
#     data = json.load(f)
# print("CalibParams：",data)

# mapJsonData = loadJsonFile('./conf/userCmdControl.json')
# print(mapJsonData["calibrateParams"])

# tcp = JAKA(mapJsonData["calibrateParams"]["robotIP"])
# print('tcp:',tcp)


# # 看世界坐标系下的情况 
# tcp_world = JAKA(mapJsonData["calibrateParams"]["robotIP"]) # 
# tcp_world.set_user_frame_id_origin(0) # 切换到世界坐标系
# ret_world = tcp_world.get_user_frame_id_origin()
# print("初始坐标系id(ret_world)为： ", ret_world)

# # tcp.joint_move_origin([PI / 2, PI / 2, -PI / 2, PI / 2, PI / 2, PI / 2], 50, 0)
# # print(tcp.get_tcp_pos())
# # homePos=[PI / 2, PI / 2, -PI / 2, PI / 2, PI / 2, PI / 2]

def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
    # 检查是否是鼠标左键点击事件
    if event == cv2.EVENT_LBUTTONDOWN:
        # 获取鼠标点击点的坐标，并从深度数据中获取该点的深度值。
        xy = "%d,%d" % (x, y)
        depth = depth_data[y, x]
        # depth = depth_data[x, y]
        print(xy,depth)
        # 如果点击点的深度为0（可能表示没有检测到物体），则生成一些附近的点。
        if int(depth) == 0:
            genCenterPoints = generatorNearPoints([x,y],1,4)  # 试着修改参数看效果

            # genCenterPoints = generatorNearPoints([x,y],mapJsonData["genNearPointParams"]["nearPointInterval"],mapJsonData["genNearPointParams"]["nearPointTimes"])  # 没有调用传入参数
            # 根据附近点获取深度  (遍历生成的附近点，获取第一个非0的深度值。)
            for i, centerPoint in enumerate(genCenterPoints):
                depth = depth_data[centerPoint[0][1], centerPoint[0][0]]
                # depth = depth_data[centerPoint[0][0], centerPoint[0][1]]
                if int(depth) != 0 or i == len(genCenterPoints):
                    break

        # 将像素坐标转换为世界坐标系中的坐标。
        worldPos=pixel_to_world([x,y],depth, data["CameraMatrix"], data["RotationMat"], data["TranslationMat"])
        print("worldPos: ",worldPos)

        # # 获取机器人工具中心点的当前位置。
        # tcpPos = tcp.get_tcp_pos()
        # print("tcpPos: ",tcpPos)
        # end_tcpPos = tcpPos[3:]
        # print('end_tcpPos:',end_tcpPos)

        # # 计算目标TCP位置，通常在Z轴方向上增加一定的距离（这里为150mm）。
        # tmpTcpPos = worldPos.tolist() + tcpPos[3:]
        # tmpTcpPos[2]=tmpTcpPos[2]  # +100 
        # print("tmpTcpPos: ",tmpTcpPos)
   
        # # 获取机器人当前的关节位置。
        # ref_pos = tcp.getjoints()
        # print("ref_pos: ",ref_pos)
        

        # # 使用逆向运动学计算从当前关节位置到目标TCP位置的关节运动。
        # ret = tcp.kine_inverse7_origin(ref_pos, tmpTcpPos)
        # print("ret: ",ret)
        # ret_5kine = ref_pos[4]

        # end_ret = (ret[0], ret[1][:4] + (ret_5kine,) + ret[1][5:])
        # print('end_ret:',end_ret)
        # # logger.info(f"end_ret: {end_ret}")

        
        
        # # 移动机器人
        # # 如果逆向运动学计算成功，则控制机器人移动到计算出的关节位置；否则，输出失败信息。
        # if ret[0] == 0:
        #     print('OK')
        #     # moveRet=tcp.joint_move7_origin(end_ret[1], 0.5, 0)  # 10
        #     # if moveRet==0:
        #     #     print("机器人移动成功")
        #     # else:
        #     #     print("机器人移动失败")
        # else:
        #     print("【机器人逆解失败...】")

        # 在图像上绘制点击点，并显示图像。
        cv2.circle(color_image, (x, y), 1, (255, 0, 0), thickness = -1)
        cv2.putText(color_image, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                    2.0, (255,0,0), thickness = 2)
        cv2.imshow("image", color_image)

if __name__ == "__main__":

    # log_directory = "./Log"  # 修改为你希望保存日志的目录路径
    # logger = setup_logging(log_directory,'AutoCalibProccess')

    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("image", 1280, 720)
    # 为窗口 "image" 设置鼠标回调函数 on_EVENT_LBUTTONDOWN。当鼠标在该窗口中点击时，会触发这个回调函数。
    cv2.setMouseCallback("image", on_EVENT_LBUTTONDOWN)



    # # 获取图像
    # oberrecCamera = Camera()
    # color_image, depth_data, depth_image = oberrecCamera.getColorDepthData()
    # oberrecCamera.close()


    # 创建一个 Pipeline 对象，并通过它获取当前使用的设备。
    pipeline = Pipeline()
    device = pipeline.get_device()
    device_info = device.get_device_info()
    device_pid = device_info.get_pid()

    # OBCameraParam_param = pipeline.getCameraParam()
    # print('OB:',OBCameraParam_param)

    # 创建一个 Config 对象，用于配置流媒体的参数。
    config = Config()

    # 设置对齐模式和同步
    align_mode = "SW"  # align mode, HW=hardware mode,SW=software mode,NONE=disable align
    enable_sync = True  # enable sync

    # 尝试获取颜色和深度传感器的默认视频流配置，并使用 config.enable_stream 方法启用这些流。
    # 如果过程中发生异常，打印异常信息。
    try:
        profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
        # color_profile = profile_list.get_default_video_stream_profile()
        color_profile = profile_list.get_video_stream_profile(1280, 800, OBFormat.MJPG, 30)
        config.enable_stream(color_profile)
        profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
        assert profile_list is not None
        # depth_profile = profile_list.get_default_video_stream_profile()
        depth_profile = profile_list.get_video_stream_profile(1280, 800, OBFormat.Y16, 30)
        assert depth_profile is not None
        # 打印颜色和深度流的配置信息，包括分辨率、帧率和数据格式。
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


    if align_mode == 'HW':
        if device_pid == 0x066B:
            # Femto Mega does not support hardware D2C, and it is changed to software D2C
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

    while True:
        try:
            frames: FrameSet = pipeline.wait_for_frames(100)
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

            #  尝试修改alpha 对识别效果的影响
            temporal_filter = TemporalFilter(alpha=0.5)
            depth_data = np.where((depth_data > MIN_DEPTH) & (depth_data < MAX_DEPTH), depth_data, 0)
            depth_data = depth_data.astype(np.uint16)
            # Apply temporal filtering
            depth_data = temporal_filter.process(depth_data)
            # center_distance = depth_data[center_y, center_x]

            # depth_image = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            # depth_image = cv2.applyColorMap(depth_image, cv2.COLORMAP_JET)
            #
            # # overlay color image on depth image
            # depth_image = cv2.addWeighted(color_image, 0.5, depth_image, 0.5, 0)

            cv2.imshow("image", color_image)

            cv2.resizeWindow('image', 1280, 720)

            key = cv2.waitKey(1)
            if key == ord('q') or key == ESC_KEY:
                break
        except KeyboardInterrupt:
            break
    pipeline.stop()

    # while(1):
    #     cv2.imshow("image", img)
    #     if cv2.waitKey(0)&0xFF==27:
    #         break
    # cv2.destroyAllWindows()


    # cv2.imshow("image", color_image)

    # cv2.resizeWindow('image', 1280, 720)

    # key = cv2.waitKey(1)
    # if key == ord('q') or key == ESC_KEY:
    #     exit
