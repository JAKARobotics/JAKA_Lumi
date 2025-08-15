# 利用 JAKASDK 控制 mujoco 环境中机械臂移动
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

# 启动 JAKA 机器人
ip_left = '192.168.2.222'
ip_right = '192.168.2.223'
robot = init_robot(ip_left)

# ---------- 生成轨迹 ----------
# 生成关节运动轨迹
init_theta = np.array([-35, -10, 0, -65, 0, 70, 0])*DEG2RAD
target_theta = np.array([-90, -10, 0, -65, 0, 70, 0])*DEG2RAD

linear_insert_num = 10
#
trajectory_pose = generate_trajectory_theta2pose(robot, init_theta, target_theta, linear_insert_num)
print("轨迹", trajectory_pose)
# print(np.array(trajectory_pose).shape)

# trajectory_theta = generate_trajectory(robot, trajectory_pose, trajectory_pose[0])
trajectory_theta = generate_trajectory(robot, init_theta, trajectory_pose[0])
print("轨迹", trajectory_theta)
print(np.array(trajectory_theta).shape)

thetas_inj = inj_thetas(trajectory_theta, 10)

# ---------- 仿真控制运动 ----------
plt.show()
for theta in thetas_inj:
    physics.data.qpos[:7] = theta
    physics.step()
    print("theta: ", physics.data.qpos[:7])
    viewer = physics.render()
    plt.imshow(viewer)
    plt.pause(0.001)
    

# plt.show()
# for i in range(len(traj)):
#     physics.data.qpos[15:22] = traj[i]
#     physics.step()
#     viewer = physics.render()
#     plt.imshow(viewer)
#     plt.pause(0.01)