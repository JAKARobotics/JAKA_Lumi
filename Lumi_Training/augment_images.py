import os
import h5py
import cv2
import numpy as np
from skimage.util import random_noise
import random
from datetime import datetime

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
def augment_image(image):
    augmented = image.copy()

    # 调整亮度
    brightness_factor = random.uniform(0.2, 1.2)
    augmented = cv2.convertScaleAbs(augmented, alpha=brightness_factor, beta=0)

    # 添加噪声
    noise_type = random.choice(["gaussian", "salt", "pepper", "s&p"])
    augmented = (random_noise(augmented, mode=noise_type) * 255).astype(np.uint8)
    # augmented = random_crop_with_black_background(augmented)
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
# 输入和输出文件夹路径
hdf5_folder_path = "/home/Data/synthetic_demo_data_shift1"
output_folder_path = "/home/Data/synthetic_demo_data_shift1/augmented_hdf5"
os.makedirs(output_folder_path, exist_ok=True)

# 获取所有 HDF5 文件
hdf5_files = [os.path.join(hdf5_folder_path, f) for f in os.listdir(hdf5_folder_path) if f.endswith('.hdf5')]

if not hdf5_files:
    print("错误：在指定文件夹中没有找到 HDF5 文件。")
    exit()

# 处理每个 HDF5 文件
for hdf5_file_path in hdf5_files:
    print(f"正在处理文件: {hdf5_file_path}")

    for augment_index in range(3):  # 生成 5 个增强后的文件
        with h5py.File(hdf5_file_path, "r") as hdf5_file:
            # 创建新的 HDF5 文件，文件名包含时间戳和索引
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file_path = os.path.join(
                output_folder_path,
                f"episode_{timestamp}_augment_{augment_index + 1}.hdf5"
            )

            with h5py.File(output_file_path, "w") as new_hdf5_file:
                # 复制原始结构和数据（除 images 外）
                for key in hdf5_file.keys():
                    if key != "observations/images":
                        hdf5_file.copy(key, new_hdf5_file)

                # 处理 `observations/images` 下的图像
                for camera_name in hdf5_file["observations/images"]:

                    images = hdf5_file[f"/observations/images/{camera_name}"]
                    print(f"正在处理相机: {camera_name}，图像数量: {len(images)}")

                    # 删除已有的同名数据集，然后创建新的数据集
                    if f"/observations/images/{camera_name}" in new_hdf5_file:
                        del new_hdf5_file[f"/observations/images/{camera_name}"]

                    # 创建新的数据集用于存储增强后的图像，shape 保持与原始文件一致
                    augmented_images_dataset = new_hdf5_file.create_dataset(
                        f"/observations/images/{camera_name}",
                        shape=images.shape,
                        dtype=np.uint8
                    )

                    # 对每一帧图像进行数据增强并存储
                    if "left" in camera_name or "right" in camera_name:
                        for i, image in enumerate(images):
                            # print(augment_index)
                            if augment_index == 0:
                                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                                image_crop = crop_and_resize_for_stereo(image_bgr)
                                aug_img_rgb = cv2.cvtColor(image_crop, cv2.COLOR_BGR2RGB)
                                augmented_images_dataset[i] = aug_img_rgb
                            else:
                                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                                image_crop = crop_and_resize_for_stereo(image_bgr)
                                augmented_image = augment_image(image_crop)
                                aug_img_rgb = cv2.cvtColor(augmented_image, cv2.COLOR_BGR2RGB)
                                augmented_images_dataset[i] = aug_img_rgb
                    else:
                        for i, image in enumerate(images):
                            # 转换为 BGR 格式
                            if augment_index == 0:
                                augmented_images_dataset[i] = image
                            else:
                                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                            # 生成增强的图像
                                augmented_image = augment_image(image_bgr)

                            # 转回 RGB 格式并保存到新的数据集中
                                aug_img_rgb = cv2.cvtColor(augmented_image, cv2.COLOR_BGR2RGB)
                                augmented_images_dataset[i] = aug_img_rgb

            print(f"增强后的文件已保存到: {output_file_path}")

print("所有图像增强处理完成！")

