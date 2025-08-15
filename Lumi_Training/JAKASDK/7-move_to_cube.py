# 机械臂移动到方块的位置
import numpy as np
from math import pi
import matplotlib.pyplot as plt
from dm_control import mujoco
import time
import os

from JAKA_utils import *
np.set_printoptions(precision=2, suppress=True)
XML_DIR = '../assets'

# image show tool
def show_robot(physics, camera_id=0):
    physics.step()
    img = physics.render(height=240, width=320, camera_id=camera_id)
    fig, ax = plt.subplots(1, 1, figsize=(img.shape[0], img.shape[1]))
    plt_img = ax.imshow(img)
    plt.show()
    return plt_img

# ---------- 初始化 ----------
# 启动模拟环境
xml_path = os.path.join(XML_DIR, f'bimanual_JAKA_pos.xml')
physics = mujoco.Physics.from_xml_path(xml_path)

# 启动 JAKA 机器人
ip_left = '192.168.2.222'
ip_right = '192.168.2.223'
lrobot = init_robot(ip_left)
rrobot = init_robot(ip_right)
lrobot.set_full_dh_flag(1)
rrobot.set_full_dh_flag(1)
# ---------- 获得转移矩阵 ----------
# tr_SIM2JAKA_left = get_transfer_matrix(robot, physics, 'left_arm')
# 将虚拟的姿态乘上这个矩阵可以获得到真实机器人的末端位姿
tr_SIM2JAKA_right = get_right_transfer_matrix(rrobot, physics)
print("tr_SIM2JAKA_right : " ,tr_SIM2JAKA_right)
tr_SIM2JAKA_left = get_left_transfer_matrix(lrobot, physics)
print("tr_SIM2JAKA_left : " ,tr_SIM2JAKA_left)

# # 测试 unit: mm
pose_SIM2JAKA = transfer_SIM2JAKA(tr_SIM2JAKA_left, [152.61 ,388.03 ,949.56  ,-2.82 , -1.31  , 2.67])
print("右臂当前末端真实值：: ", pose_SIM2JAKA)
# pose_JAKA2SIM = transfer_JAKA2SIM(tr_SIM2JAKA_right, [388, -101, -400, -110*DEG2RAD, 0, 0])
# print("pose_JAKA2SIM: ", pose_JAKA2SIM)

# ---------- 生成轨迹 ----------
# 初始位置
START_LEFT_THETA = np.array([-0.6457718232379003, -1.0995574287564276, 0.7504915783575616, -1.204277183876087, 0.4712388980384684, 1.0471975511965976, 3.784579533429505e-21])
START_RIGHT_THETA = np.array([0.6459845908728367, -1.1034952671598064, -0.7624523260870136, -1.2064142769752697, -0.48055950138812953, -1.0510644578917985, 0.31504842464567123])
physics.data.qpos[:7] = START_LEFT_THETA
physics.data.qpos[15:22] = START_RIGHT_THETA


# 目标位置
cube_pose = sample_box_pose() # [x, y, z, q1, q2, q3, q4]
# cube_pos = physics.named.data.xpos['box'] # no use
cube_pose[:3] = [-0.1218  , 0.41175  ,0.45 ]
cube_pos = [-0.1218  , 0.41175  ,0.45 ]
print('&&&&&&',cube_pose)
# print("方块在SIM环境下位置(mm): ", cube_pos*1000)
# show_robot(physics, 'show_middle')
# show_robot(physics, 'top')
box_start_idx = physics.model.name2id('red_box_joint', 'joint')
np.copyto(physics.data.qpos[box_start_idx : box_start_idx + 7], cube_pose)
show_robot(physics, 'show_middle')

# 逆解
# TARGET_LEFT_POSE = mujoco_inverse_from_SDK(robot, physics, tr_SIM2JAKA_left, START_LEFT_THETA, cube_pos)
#目标位置的关节角度值
TARGET_LEFT_POSE = mujoco_inverse_from_SDK(lrobot, tr_SIM2JAKA_left, START_LEFT_THETA, cube_pos)
print("左臂目标位置(deg): ", np.array(TARGET_LEFT_POSE)*RAD2DEG)
physics.data.qpos[:7] = TARGET_LEFT_POSE
show_robot(physics, 'show_middle')
# # ---------- 初始化机械臂位姿 ----------

# ---------- 生成轨迹 ----------
physics.reset()
physics.data.qpos[:7] = START_LEFT_THETA
physics.data.qpos[15:22] = START_RIGHT_THETA
box_start_idx = physics.model.name2id('red_box_joint', 'joint')
np.copyto(physics.data.qpos[box_start_idx : box_start_idx + 7], cube_pose)

#补偿100个过度点
thetas_inj = np.linspace(START_LEFT_THETA, TARGET_LEFT_POSE, 1000)

# ---------- 仿真控制运动 ----------
ax = plt.subplot()
img = physics.render(height=480, width=640)
plt_img = ax.imshow(img)
plt.ion()

for i in range(1000):
    physics.data.qpos[:7] = thetas_inj[i]
    # physics.data.ctrl[15:22] = thetas_inj[i]
    
    physics.step()
    print("theta: ", physics.data.qpos[:7])
    # ret = lrobot.kine_forward7(joint_pos)
    print("方块位置", physics.named.data.xpos['box']*1000)

    img = physics.render(height=480, width=640, camera_id='show_middle')
    plt_img.set_data(img)
    viewer = physics.render()
    time.sleep(0.02)
    plt.pause(0.02)
# for i in range(1000):
#     # physics.data.qpos[15:22] = thetas_inj[i]
#     # physics.data.ctrl[15:22] = thetas_inj[i]
    
#     physics.step()
#     # print("theta: ", physics.data.qpos[:7])

#     # print("方块位置", physics.named.data.xpos['box']*1000)

#     img = physics.render(height=480, width=640, camera_id='top')
#     plt_img.set_data(img)
#     viewer = physics.render()
#     time.sleep(0.02)
#     plt.pause(0.02)

