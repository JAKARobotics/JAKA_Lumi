import glob
import os
import shutil
from time import sleep

import h5py
import cv2
import numpy as np
# from skimage.util import random_noise
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from sympy.codegen.cnodes import sizeof

def crop_and_resize_for_stereo(image):
    """
    For 'left_cam' and 'right_cam', crops the image from fixed diagonal points and resizes back to original dimensions.
    For other camera names, returns the original image.

    Args:
        image: Input image (numpy array)
        camera_name: Name of the camera ('left_cam', 'right_cam', etc.)

    Returns:
        Processed image (cropped and resized for stereo cameras, original otherwise)
    """
    h, w = image.shape[:2]

    # Define fixed diagonal crop points (adjust these values as needed)

        # Top-left and bottom-right points for left camera
    x1, y1 = int(w * 0.3), int(h * 0.5)  # 10% from top-left
    x2, y2 = int(w * 0.8), int(h * 1)  # 10% from bottom-right

    # Crop the image
    cropped = image[y1:y2, x1:x2]

    # Resize back to original dimensions
    resized = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

    return resized
# 数据增强函数
def augment_image(image, brightness_factor, noise_type):
    augmented = image.copy()

    # 调整亮度
    augmented = cv2.convertScaleAbs(augmented, alpha=brightness_factor, beta=0)

    # 添加噪声
    augmented = (random_noise(augmented, mode=noise_type) * 255).astype(np.uint8)
    return augmented

def random_crop_with_black_background(image, crop_ratio=0.8):
    """
    随机裁剪图像并将背景填充为黑色，保持原始尺寸。
    crop_ratio: 剪裁区域的比例，默认为 80% 的原始尺寸。
    """
    h, w, c = image.shape

    # 随机生成裁剪区域的尺寸
    crop_h = int(h * crop_ratio)
    crop_w = int(w * crop_ratio)

    # 随机选择裁剪的起始位置
    start_x = random.randint(0, w - crop_w)
    start_y = random.randint(0, h - crop_h)

    # 裁剪图像
    cropped_image = image[start_y:start_y + crop_h, start_x:start_x + crop_w]

    # 创建一个黑色背景的画布，大小与原始图像一致
    canvas = np.zeros((h, w, c), dtype=np.uint8)

    # 将裁剪后的图像放回画布的中心
    y_offset = (h - crop_h) // 2
    x_offset = (w - crop_w) // 2
    canvas[y_offset:y_offset + crop_h, x_offset:x_offset + crop_w] = cropped_image

    return canvas

def process_hdf5_file(hdf5_file_path, output_folder_path, shift_index):
    print(f"正在处理文件: {hdf5_file_path}")

    # 创建新的 HDF5 文件，文件名包含时间戳和索引
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = os.path.join(
        output_folder_path,
        f"episode_{timestamp}_synthetic_shift{shift_index}.hdf5"
    )

    with h5py.File(hdf5_file_path, "r") as hdf5_file:
        with h5py.File(output_file_path, "w") as new_hdf5_file:
            # 复制原始结构和数据（除 images 外）
            for key in hdf5_file.keys():
                if key != "/action":
                    hdf5_file.copy(key, new_hdf5_file)

            if f"/action" in new_hdf5_file:
                del new_hdf5_file["/action"]

            qpos = hdf5_file["/observations/qpos"]

            # 创建新的数据集用于存储增强后的图像，shape 保持与原始文件一致
            new_action = new_hdf5_file.create_dataset(
                "/action",
                shape=qpos.shape,
            )

            episode_len = len(qpos)
            print(f"episode_len:{episode_len}")

            for i in range(episode_len):
                if i<episode_len-shift_index:
                    new_action[i] = qpos[i + shift_index]
                else:
                    new_action[i] = qpos[episode_len-1]
    sleep(1)

    print(f"数据合成后的文件已保存到: {output_file_path}")


def assign_action_to_qpos(input_file, output_file):
    """
    将HDF5文件中的/action数据集值全部赋值给/observations/qpos，并保存到新文件

    参数:
        input_file (str): 输入HDF5文件路径
        output_file (str): 输出HDF5文件路径
    """
    # 先复制文件到目标路径（避免直接修改原文件）
    shutil.copyfile(input_file, output_file)

    with h5py.File(output_file, 'r+') as f:  # 使用'r+'模式以读写方式打开文件
        # 检查所需的数据集是否存在
        if 'action' not in f:
            raise ValueError(f"'{input_file}': '/action'数据集不存在")
        if 'observations/qpos' not in f:
            raise ValueError(f"'{input_file}': '/observations/qpos'数据集不存在")

        # 获取action数据
        action_data = f['action'][...]

        # 检查形状是否匹配
        qpos_dataset = f['observations/qpos']
        if action_data.shape != qpos_dataset.shape:
            raise ValueError(f"形状不匹配: action形状为{action_data.shape}, qpos形状为{qpos_dataset.shape}")

        # 赋值操作
        qpos_dataset[...] = action_data

        print(f"处理完成: {input_file} -> {output_file}")


def process_all_hdf5_files(input_dir, output_dir):
    """
    遍历input_dir下所有.hdf5文件，处理后保存到output_dir

    参数:
        input_dir (str): 输入文件夹路径
        output_dir (str): 输出文件夹路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 遍历输入目录下的所有文件
    for filename in os.listdir(input_dir):
        if filename.endswith('.hdf5'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            try:
                assign_action_to_qpos(input_path, output_path)
            except Exception as e:
                print(f"处理 {filename} 时出错: {str(e)}")
def main():
    # input_directory = "/home/jaka/ros2_ws/datasets"  # 替换为你的输入文件夹路径
    # output_directory = "/home/jaka/ros2_ws/datasets/process"  # 替换为你的输出文件夹路径
    #
    # process_all_hdf5_files(input_directory, output_directory)
    # print("所有文件处理完成！")
    # 输入和输出文件夹路径
    shift_index = 1  # 采用偏移n个时间步的qpos作为action
    hdf5_folder_path = "/home/Data"
    output_folder_path = hdf5_folder_path + "/synthetic_demo_data_shift" + str(shift_index)
    os.makedirs(output_folder_path, exist_ok=True)
    for hdf5_file in glob.glob(os.path.join(hdf5_folder_path, '*.hdf5')):
        process_hdf5_file(hdf5_file, output_folder_path, shift_index)
    print("所有数据合成处理完成！")




if __name__ == "__main__":
    main()

