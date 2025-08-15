# 获得 模拟环境双臂 到 JAKA双臂的转换矩阵
import numpy as np
from math import pi
import matplotlib.pyplot as plt
from dm_control import mujoco
import os

from JAKASDK_OpenLoop.JAKA_utils import *
np.set_printoptions(precision=5, suppress=True)

# 启动模拟环境
XML_DIR = './assets'
xml_path = os.path.join(XML_DIR, f'bimanual_JAKA_pos_test.xml')
physics = mujoco.Physics.from_xml_path(xml_path)

theta = np.array([0, -90, 0, 0, 0, 0, 0])*DEG2RAD
# ---------- Sim 环境 正运动学测试 ----------
print("====================== Sim转JAKA 正运动学测试 ======================")
T_Sim2JAKA = np.array([[-1, 0, 0, -204.99],
                        [0, -1, 0.01, -454.18],
                        [0, 0.01, 1, -1023.99],
                        [0, 0, 0, 1]])

pose_mujoco, T_mujoco = mojoco_kine_forward7(physics, theta, 'left_arm')
# print("l1绝对位置", physics.named.data.xpos['l1']*1000)
T_Sim2JAKA = T_Sim2JAKA @ T_mujoco
pose_Sim2JAKA = tr2pose(T_Sim2JAKA)
# print("mujoco l7绝对位置", pose_mujoco)
print("JAKA l7绝对位置", pose_Sim2JAKA)

# ---------- JAKA 环境 正运动学测试 ----------
print("====================== JAKA 正运动学测试 ======================")
ip_left = '192.168.2.222'
ip_right = '192.168.2.223'
robot = init_robot(ip_left)

_, pose_JAKA = robot.kine_forward7(theta)
print("JAKA l7绝对位置", pose_JAKA)
T_JAKA = JAKA_pose2tr(pose_JAKA, robot)

print("差距 ", pose_Sim2JAKA - pose_JAKA)



# transfer_matrix = T_JAKA @ np.linalg.inv(T_mujoco)
# print("constant: ", transfer_matrix)

# ---------- 获取 Sim环境 到 双臂坐标系 的转换矩阵 ----------

# 对应双臂的基坐标系转移矩阵(mm)
# T_sim2baseArm_left, T_sim2baseArm_right = get_T_sim2baseArm(physics)
# print("T_sim2baseArm_left: ", T_sim2baseArm_left)
# print("T_sim2baseArm_right: ", T_sim2baseArm_right)



# # 关节转角
# pose, T = mojoco_kine_forward7(physics, theta, 'left_arm')
# print("Sim环境计算工具末端(x,y,z,rx,ry,rz)(rad): ", pose)
# pose = get_pose_sim2DH(physics, T, 'left_arm')
# print("Sim环境中, DH基坐标系下工具末端(x,y,z,rx,ry,rz)(rad): ", pose)


# 显示仿真
# physics.step()
# viewer = physics.render()
# plt.imshow(viewer)
# plt.show()
