# 仿真环境参数
import numpy as np
from math import pi
import matplotlib.pyplot as plt
from dm_control import mujoco
import os

from JAKASDK_OpenLoop.JAKA_utils import *
from utils import *
# from utils import sample_box_pose, sample_insertion_pose

np.set_printoptions(precision=3, suppress=True)


# ---------- 导入模型 ---------- 
XML_DIR = './assets'
xml_path = os.path.join(XML_DIR, f'bimanual_JAKA_pos_test.xml')
physics = mujoco.Physics.from_xml_path(xml_path)

# ---------- 基本参数 ----------
# 关节转角
qpos = physics.data.qpos # 37 = 30+7(red_box_joint)
named_qpos = physics.named.data.qpos
named_xpos = physics.named.data.xpos
named_xquat = physics.named.data.xquat
# print(qpos)
# print(named_qpos)
# print(named_xpos)
# print(named_xquat)

# 末端位置
mocap_xpos = physics.named.data.xpos['JAKA_arm_right/camera_focus']
mocap_xquat = physics.named.data.xquat['JAKA_arm_right/camera_focus']
# print(mocap_xpos)
# print(mocap_xquat)

# ---------- 正运动学测试 ----------
# plt.show()
# # viewer = physics.render()
# # plt.imshow(viewer)
# j1 = np.linspace(0, pi, 100)
# j2 = np.linspace(0, pi, 100)
# j3 = np.linspace(0, pi, 100)
# j4 = np.linspace(0, pi, 100)
# j5 = np.linspace(0, pi, 100)
# j6 = np.linspace(0, pi, 100)
# j7 = np.linspace(0, pi, 100)

# left_arm_qpos = physics.data.qpos[0:7]
# right_arm_qpos = physics.data.qpos[15:22]
# for i in range(100):
#     physics.data.qpos[15:22] = [j1[i], j2[i], j3[i], j4[i], j5[i], j6[i], j7[i]]

#     physics.step()
#     viewer = physics.render()
#     plt.imshow(viewer)
#     plt.pause(0.01)

# ---------- 逆运动学测试 ----------
# 初始位姿
init_pose = [0, 0, 0, 0, 0, 0]
# 目标位姿
target_pose = [0.3, 0.3, 0.3, 0, 0, 0]
# 生成运动轨迹
traj = generate_trajectory(init_pose, target_pose, 'right_arm')
# 执行运动轨迹
# plt.show()
# for i in range(len(traj)):
#     physics.data.qpos[15:22] = traj[i]
#     physics.step()
#     viewer = physics.render()
#     plt.imshow(viewer)
#     plt.pause(0.01)