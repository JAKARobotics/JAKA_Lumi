import os
import h5py
import cv2
import numpy as np
from datetime import datetime, timedelta

# HDF5 文件夹路径
hdf5_folder_path = "/home/jaka/ros2_ws/datasets"
# 输出图像保存路径
output_folder_path = hdf5_folder_path+"/output_images"

# 确保输出目录存在
os.makedirs(output_folder_path, exist_ok=True)

# 时间戳起点
start_time = datetime.now()  # 可以替换为自定义时间点，例如 datetime(2025, 1, 1, 12, 0, 0)
frame_interval = timedelta(milliseconds=40)  # 假设帧率为25帧/秒，每帧间隔40毫秒

# 获取文件夹中的所有 HDF5 文件
hdf5_files = [os.path.join(hdf5_folder_path, f) for f in os.listdir(hdf5_folder_path) if f.endswith('.hdf5')]

if not hdf5_files:
    print("错误：在指定文件夹中没有找到 HDF5 文件。")
    exit()

# 循环处理每个 HDF5 文件
for hdf5_file_path in hdf5_files:
    print(f"正在处理文件: {hdf5_file_path}")
    with h5py.File(hdf5_file_path, "r") as hdf5_file:
        # 获取所有相机的图像数据
        image_dict = {}
        for camera_name in hdf5_file["observations/images"]:
            image_dict[camera_name] = hdf5_file[f'/observations/images/{camera_name}']

        # 动态获取相机名称
        camera_names = list(image_dict.keys())
        if not camera_names:
            print(f"错误：在 {hdf5_file_path} 中未找到任何相机数据。跳过...")
            continue

        # 获取图像帧数
        num_frames = min(len(image_dict[camera_name]) for camera_name in camera_names)
        print(f"当前文件 {hdf5_file_path} 的 episode 长度: {num_frames}")

        # 显示并保存相机图像
        for i in range(num_frames):
            # 根据帧序号生成时间戳
            timestamp = start_time + i * frame_interval
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 精确到毫秒
            if i % 25 ==0 :
                for camera_name in camera_names:
                    frame = image_dict[camera_name][i]
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    # 保存图像

                    output_image_path = os.path.join(output_folder_path,f"{camera_name + timestamp_str}.png")
                    cv2.imwrite(output_image_path, frame_bgr)

print("图像提取并保存完成！")
