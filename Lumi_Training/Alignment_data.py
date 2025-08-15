import os
import h5py
import numpy as np

# 获取文件夹中的所有 HDF5 文件
hdf5_folder_path = "/home/slishy/Code/act-plus-plus/data"
output_folder_path = os.path.join(hdf5_folder_path, "processed")
os.makedirs(output_folder_path, exist_ok=True)

hdf5_files = [os.path.join(hdf5_folder_path, f) for f in os.listdir(hdf5_folder_path) if f.endswith('.hdf5')]

if not hdf5_files:
    print("错误：在指定文件夹中没有找到 HDF5 文件。")
    exit()

# 计算所有文件的平均帧长度
frame_lengths = []
for hdf5_file_path in hdf5_files:
    with h5py.File(hdf5_file_path, "r") as hdf5_file:
        num_frames = len(hdf5_file["/observations/images"][list(hdf5_file["/observations/images"].keys())[0]])
        frame_lengths.append(num_frames)

# 计算平均帧长度并向上取整到最近的整百
average_length = int(np.ceil(np.mean(frame_lengths) / 100) * 100)
print(f"计算出的平均帧长度（向上取整到整百）：{average_length}")

# 处理文件
for hdf5_file_path in hdf5_files:
    print(f"正在处理文件: {hdf5_file_path}")
    with h5py.File(hdf5_file_path, "r") as hdf5_file:
        # 获取帧长度
        num_frames = len(hdf5_file["/observations/images"][list(hdf5_file["/observations/images"].keys())[0]])

        # 如果帧长度大于或等于平均值，不处理
        if num_frames >= average_length:
            print(f"文件 {hdf5_file_path} 的帧长度为 {num_frames}，大于或等于平均值 {average_length}，跳过处理。")
            continue

        # 获取数据
        images = {k: np.array(hdf5_file[f"/observations/images/{k}"]) for k in hdf5_file["/observations/images"]}
        qpos = np.array(hdf5_file["/observations/qpos"])
        qvel = np.array(hdf5_file["/observations/qvel"])
        commands = np.array(hdf5_file["/action"])

        # 补齐帧数
        for camera_name in images.keys():
            last_frame = images[camera_name][-1]
            num_to_pad = average_length - len(images[camera_name])
            padded_frames = np.tile(last_frame, (num_to_pad, 1, 1, 1))
            images[camera_name] = np.vstack((images[camera_name], padded_frames))

        last_qpos = qpos[-1]
        last_qvel = qvel[-1]
        last_command = commands[-1]

        qpos = np.vstack((qpos, np.tile(last_qpos, (average_length - len(qpos), 1))))
        qvel = np.vstack((qvel, np.tile(last_qvel, (average_length - len(qvel), 1))))
        commands = np.vstack((commands, np.tile(last_command, (average_length - len(commands), 1))))

        # 保存到新的 HDF5 文件
        output_file_path = os.path.join(output_folder_path, os.path.basename(hdf5_file_path))
        with h5py.File(output_file_path, "w") as output_file:
            grp_obs = output_file.create_group("observations")
            grp_images = grp_obs.create_group("images")
            for camera_name, data in images.items():
                grp_images.create_dataset(camera_name, data=data)
            grp_obs.create_dataset("qpos", data=qpos)
            grp_obs.create_dataset("qvel", data=qvel)
            output_file.create_dataset("action", data=commands)

        print(f"文件 {hdf5_file_path} 已补齐并保存到: {output_file_path}")

print("所有文件处理完成！")
