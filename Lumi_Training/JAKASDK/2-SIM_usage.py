# dm_control & mujoco 基础使用方法
import numpy as np
from math import pi
import matplotlib.pyplot as plt
from dm_control import mujoco
import os

from JAKA_utils import *
from JAKA_utils import sample_box_pose
np.set_printoptions(precision=2, suppress=True)

# 启动模拟环境
XML_DIR = './assets'
xml_path = os.path.join(XML_DIR, f'bimanual_JAKA_pos.xml')
physics = mujoco.Physics.from_xml_path(xml_path)

# 随机生成方块
cube_pose = sample_box_pose() # [x, y, z, q1, q2, q3, q4]
box_start_idx = physics.model.name2id('red_box_joint', 'joint')
np.copyto(physics.data.qpos[box_start_idx : box_start_idx + 7], cube_pose)

# ---------- Physics 基础信息获取 ----------
# joint 关节
qpos = physics.data.qpos # 37 = 30+7(red_box_joint)
# print("qpos: ", qpos.shape, qpos)

# name 索引
named_qpos = physics.named.data.qpos # joint
named_xpos = physics.named.data.xpos # body
named_xquat = physics.named.data.xquat # body
# print("named_qpos: ", named_qpos)
# print("named_xpos: ", named_xpos)
# print("named_xquat: ", named_xquat)

# actuator, 指定 joint
ctrl = physics.data.ctrl # 30 (no red_box_joint)
# print("ctrl: ", ctrl.shape, ctrl)
print("named ctrl: ", physics.named.data.ctrl)
# 获得 索引l-j2的索引位置
print(type(physics.named.data.ctrl))
print(physics.data.ctrl.index('l-j2'))

# ---------- Visualization ----------

camera_id = 'show_middle' # string or int
img = physics.render(height=480, width=640, camera_id=camera_id)

fig, ax = plt.subplots(1, 1, figsize=(img.shape[0], img.shape[1]))
plt_img = ax.imshow(img)
plt.ion() # interactive mode

duration = 6    # (seconds)
framerate = 30  # (Hz)

# # Simulate and display video.
# frames = []
# physics.reset()  # Reset state and time
# while physics.data.time < duration:
#     print("time: ", physics.data.time)
#     # append data to the traces
#     #   positions.append(physics.named.data.geom_xpos["green_sphere"].copy())
#     #   times.append(physics.data.time)
#     #   speeds.append(get_geom_speed(physics, "green_sphere"))
#     physics.step()
#     img = physics.render(height=480, width=640, camera_id=camera_id)
#     plt_img.set_data(img)
#     if len(frames) < physics.data.time * framerate:
#         camera = mujoco.Camera(physics, max_geom=10000)
#         # camera = mujoco.Camera(physics, max_geom=10000,
#         #                        scene_callback=scene_callback)
#         pixels = camera.render()
#         frames.append(pixels)
#     plt.pause(0.02) # wait for the img to update

# plt.ioff()
# plt.show()