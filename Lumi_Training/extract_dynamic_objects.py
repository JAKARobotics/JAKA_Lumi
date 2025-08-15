import os
import h5py
import cv2
import numpy as np

def extract_dynamic_objects(frame1, frame2):
    # 计算帧间差异
    diff = cv2.absdiff(frame1, frame2)
    # 转换为灰度图像
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    # 设置阈值，将差异转换为二值图像
    _, thresh = cv2.threshold(gray_diff, 50, 255, cv2.THRESH_BINARY)  # 参数30为阈值值，可根据需求调整
    # 定义卷积核，用于图像膨胀
    kernel = np.ones((5, 5), np.uint8)  # 卷积核大小 (5,5)，可调整以影响膨胀效果
    # 膨胀操作，使动态物体区域更明显
    dilated = cv2.dilate(thresh, kernel, iterations=2)  # iterations控制膨胀次数，可调整
    return dilated

def update_image_with_dynamic_objects(frame, dynamic_objects_mask):
    # 创建黑色背景
    black_background = np.zeros_like(frame)
    # 提取动态物体区域
    dynamic_region = cv2.bitwise_and(frame, frame, mask=dynamic_objects_mask)
    # 将动态物体区域添加到黑色背景上
    updated_frame = cv2.add(black_background, dynamic_region)
    return updated_frame

def update_image_with_static_objects(frame, dynamic_objects_mask):
    # 创建静态物体的掩码
    static_region_mask = cv2.bitwise_not(dynamic_objects_mask)
    # 提取静态物体区域
    static_region = cv2.bitwise_and(frame, frame, mask=static_region_mask)
    # 创建黑色背景
    black_background = np.zeros_like(frame)
    # 将静态物体区域添加到黑色背景上
    updated_frame = cv2.add(black_background, static_region)
    return updated_frame

def save_updated_hdf5(original_hdf5_path, new_hdf5_path, updated_images):
    with h5py.File(original_hdf5_path, 'r') as original_file, \
         h5py.File(new_hdf5_path, 'w') as new_file:
        for key in original_file.keys():
            if key != 'observations':
                original_file.copy(key, new_file)
        observations_group = new_file.create_group('observations')
        for key in original_file['observations'].keys():
            if key != 'images':
                original_file['observations'].copy(key, observations_group)
        images_group = observations_group.create_group('images')
        for camera_name, images in updated_images.items():
            images_group.create_dataset(camera_name, data=images)

hdf5_folder_path = "/home/slishy/Code/act-plus-plus/data"
new_hdf5_folder_path = "/home/slishy/Code/act-plus-plus/updated_hdf5"
os.makedirs(new_hdf5_folder_path, exist_ok=True)

hdf5_files = [os.path.join(hdf5_folder_path, f) for f in os.listdir(hdf5_folder_path) if f.endswith('.hdf5')]

if not hdf5_files:
    print("错误：在指定文件夹中没有找到 HDF5 文件。")
    exit()

for hdf5_file_path in hdf5_files:
    print(f"正在处理文件: {hdf5_file_path}")
    updated_images = {}

    with h5py.File(hdf5_file_path, "r") as hdf5_file:
        image_dict = {camera_name: hdf5_file[f'/observations/images/{camera_name}'] for camera_name in hdf5_file["observations/images"]}
        camera_names = list(image_dict.keys())

        if len(camera_names) < 3:
            print(f"错误：在 {hdf5_file_path} 中找到的相机少于三个。跳过...")
            continue

        num_frames = min(len(image_dict[camera_names[0]]), len(image_dict[camera_names[1]]), len(image_dict[camera_names[2]]))
        for camera_name in camera_names:
            images = image_dict[camera_name]
            updated_images[camera_name] = []

            for i in range(1, num_frames):
                frame1 = cv2.cvtColor(images[i - 1], cv2.COLOR_RGB2BGR)
                frame2 = cv2.cvtColor(images[i], cv2.COLOR_RGB2BGR)
                mask = extract_dynamic_objects(frame1, frame2)

                if camera_name == 'front_cam':
                    updated_frame = update_image_with_dynamic_objects(frame2, mask)
                else:
                    updated_frame = update_image_with_static_objects(frame2, mask)

                updated_images[camera_name].append(cv2.cvtColor(updated_frame, cv2.COLOR_BGR2RGB))

            updated_images[camera_name] = np.array(updated_images[camera_name])

    new_hdf5_file_path = os.path.join(new_hdf5_folder_path, os.path.basename(hdf5_file_path).replace(".hdf5", "_updated.hdf5"))
    save_updated_hdf5(hdf5_file_path, new_hdf5_file_path, updated_images)
    print(f"已保存更新后的文件: {new_hdf5_file_path}")
