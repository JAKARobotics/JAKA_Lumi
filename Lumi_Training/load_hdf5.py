import os
import h5py
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 定义关节和状态名称
JOINT_NAMES = ["l1", "l2", "l3", "l4", "l5", "l6", "l7"]
STATE_NAMES = JOINT_NAMES + ["gripper"]


def visualize_joints(qpos_list, command_list, plot_path=None, ylim=None, label_overwrite=None):
    if label_overwrite:
        label1, label2 = label_overwrite
    else:
        label1, label2 = 'qpos', 'action'

    qpos = np.array(qpos_list)  # ts, dim
    command = np.array(command_list)
    num_ts, num_dim = qpos.shape
    h, w = 2, num_dim
    num_figs = num_dim
    fig, axs = plt.subplots(num_figs, 1, figsize=(w, h * num_figs))

    # 绘制关节状态
    all_names = [name + '_left' for name in STATE_NAMES] + [name + '_right' for name in STATE_NAMES]
    for dim_idx in range(num_dim):
        ax = axs[dim_idx]
        ax.plot(qpos[:, dim_idx], label=label1)
        ax.set_title(f'Joint {dim_idx}: {all_names[dim_idx]}')
        ax.legend()

    # 绘制关节命令
    for dim_idx in range(num_dim):
        ax = axs[dim_idx]
        ax.plot(command[:, dim_idx], label=label2)
        ax.legend()

    if ylim:
        for dim_idx in range(num_dim):
            ax = axs[dim_idx]
            ax.set_ylim(ylim)

    plt.tight_layout()
    plt.savefig(plot_path)
    print(f'关节数据已保存到：{plot_path}')
    plt.close()


def initialize_windows(camera_names, screen_width=1920, screen_height=1080):
    num_cameras = len(camera_names)
    if num_cameras == 0:
        print("错误：未检测到相机数据。")
        return

    window_width = screen_width // num_cameras
    window_height = screen_height // 2

    # 动态创建窗口
    for i, camera_name in enumerate(camera_names):
        cv2.namedWindow(camera_name, cv2.WINDOW_NORMAL)
        cv2.moveWindow(camera_name, window_width * i, 0)
        cv2.resizeWindow(camera_name, window_width, window_height)


# HDF5 文件夹路径
# hdf5_folder_path = "/home/jaka/ros2_ws/datasets/process/synthetic_demo_data_shift3/augmented_hdf5"
hdf5_folder_path = "/home/jaka/datasets"

# 获取文件夹中的所有 HDF5 文件
hdf5_files = [os.path.join(hdf5_folder_path, f) for f in os.listdir(hdf5_folder_path) if f.endswith('.hdf5')]

if not hdf5_files:
    print("错误：在指定文件夹中没有找到 HDF5 文件。")
    exit()

# 循环播放每个 HDF5 文件中的图像数据
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

        # 初始化窗口
        initialize_windows(camera_names)

        # 获取关节状态和命令数据
        qpos_list = np.array(hdf5_file['/observations/qpos'])
        command_list = np.array(hdf5_file['/action'])

        # 获取图像帧数
        num_frames = min(len(image_dict[camera]) for camera in camera_names)
        print(f"当前文件 {hdf5_file_path} 的 episode 长度: {num_frames}")

        # 显示相机图像
        for i in range(num_frames):
            for camera_name in camera_names:
                frame = image_dict[camera_name][i]
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                cv2.imshow(camera_name, frame_bgr)

            # 等待按键
            key = cv2.waitKey(60)
            if key == ord('q'):  # 按 'q' 键退出
                cv2.destroyAllWindows()
                exit()
            elif key == ord('n'):  # 按 'n' 键跳到下一个文件
                plot_path = os.path.join(hdf5_folder_path,
                                         f"{os.path.basename(hdf5_file_path)}_joint_visualization.png")
                visualize_joints(qpos_list[:num_frames], command_list[:num_frames], plot_path=plot_path)
                break
        else:
            # 如果没有按 'n' 跳转到下一个文件，则显示关节数据的总结图
            plot_path = os.path.join(hdf5_folder_path, f"{os.path.basename(hdf5_file_path)}_joint_visualization.png")
            visualize_joints(qpos_list[:num_frames], command_list[:num_frames], plot_path=plot_path)

            # 加载并显示关节图像
            joint_image = cv2.imread(plot_path)
            cv2.imshow('Joint Visualization', joint_image)

            # 等待按键继续或退出
            while True:
                key = cv2.waitKey(0)
                if key == ord('q'):  # 按 'q' 键退出
                    cv2.destroyAllWindows()
                    exit()
                elif key == ord('n'):  # 按 'n' 键跳到下一个文件
                    break

# 释放资源
cv2.destroyAllWindows()
