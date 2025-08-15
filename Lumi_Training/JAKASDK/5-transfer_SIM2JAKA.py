# 获得 模拟环境双臂 到 JAKA双臂的转换矩阵
import numpy as np
from math import pi
import matplotlib.pyplot as plt
from dm_control import mujoco
import os

from JAKA_utils import *
np.set_printoptions(precision=2, suppress=True)

# 启动模拟环境
XML_DIR = '../assets'
xml_path = os.path.join(XML_DIR, f'bimanual_JAKA_pos.xml')
physics = mujoco.Physics.from_xml_path(xml_path)

theta1 = np.array([10, 45, 20, 30, 5, 10, 10])*DEG2RAD
theta2 = np.array([4, 60, 70, 50, 10, 30, 40])*DEG2RAD
theta1 = np.array([0, 0, 0, 0, 0, 0, 0])*DEG2RAD
theta2 = np.array([90, 90, 0, 0, 0, 0, 0])*DEG2RAD
# ---------- Sim 环境 正运动学测试 ----------
print("====================== Sim转JAKA 正运动学测试 ======================")

pose_mujoco1, T_mujoco1 = mujoco_kine_forward7(physics, theta1, 'left_arm')
print("mujoco l7绝对位置", pose_mujoco1)
pose_mujoco2, T_mujoco2 = mujoco_kine_forward7(physics, theta2, 'left_arm')


# ---------- JAKA 环境 正运动学测试 ----------
print("====================== JAKA 正运动学测试 ======================")
ip_left = '192.168.2.222'
ip_right = '192.168.2.223'
robot = init_robot(ip_left)
# robot = init_robot(ip_right)

_, pose_JAKA1 = robot.kine_forward7(theta1)
T_JAKA1 = JAKA_pose2tr(pose_JAKA1, robot)
print("JAKA l7绝对位置", pose_JAKA1)
_, pose_JAKA2 = robot.kine_forward7(theta2)
T_JAKA2 = JAKA_pose2tr(pose_JAKA2, robot)

T_Sim2JAKA = T_JAKA1 @ np.linalg.inv(T_mujoco1)
print("T_Sim2JAKA: ", T_Sim2JAKA)
T_Sim2JAKAA = T_JAKA2 @ np.linalg.inv(T_mujoco2)
print("delta_T", T_Sim2JAKA-T_Sim2JAKAA)

print("mujoco delta x", (pose_mujoco1[0] - pose_mujoco2[0]))
print("mujoco delta y", (pose_mujoco1[1] - pose_mujoco2[1]))
print("mujo delta z", (pose_mujoco1[2] - pose_mujoco2[2]))

print("JAKA delta x", (pose_JAKA1[0] - pose_JAKA2[0]))
print("JAKA delta y", (pose_JAKA1[1] - pose_JAKA2[1]))
print("JAKA delta z", (pose_JAKA1[2] - pose_JAKA2[2]))


a = ((pose_mujoco1[0] - pose_mujoco2[0]) + (pose_JAKA1[0] - pose_JAKA2[0]))/1000
print("a: ", a) 
a = ((pose_mujoco1[1] - pose_mujoco2[1]) + (pose_JAKA1[1] - pose_JAKA2[1]))/1000
print("a: ", a) 



print("====================== JAKA 逆运动学测试 ======================")
theta = np.array([-50, -70, 60, -75, 16, 70, -150])*DEG2RAD

pose_in_SIM = mujoco_kine_forward7(physics, theta, 'left_arm')[0]
print("SIM中位姿: ", pose_in_SIM)
T_Sim2JAKA = get_transfer_matrix(robot, physics, 'left_arm')
print("SIM到JAKA位姿: ", transfer_SIM2JAKA(T_Sim2JAKA, pose_in_SIM))

pose_in_JAKA = robot.kine_forward7(theta)[1]
print("JAKA中位姿: ", pose_in_JAKA)


# ans = mujoco_inverse_from_SDK(robot, T_Sim2JAKA, theta, pose_in_SIM)
# print("逆解: ", ans)

ans = robot.kine_inverse7(theta, pose_in_JAKA)
if len(ans) == 1:
    raise Exception("逆解失败")
target_theta = ans[1]
print("目标转角: ", target_theta)