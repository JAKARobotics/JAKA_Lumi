# dm_control 基础运动学仿真
import numpy as np
from math import pi
import matplotlib.pyplot as plt
from dm_control import mujoco
import os

from JAKA_utils import *
np.set_printoptions(precision=2, suppress=True)
sys.path.append("/home/slishy/Code/act-Mine/JAKASDK_OpenLoop/JAKA_SDK_WIN_DualArm")
import jkrc
# 启动模拟环境
XML_DIR = '../assets'
xml_path = os.path.join(XML_DIR, f'bimanual_JAKA_pos.xml')
physics = mujoco.Physics.from_xml_path(xml_path)

# ---------- 初始参数设置 ----------
# 随机生成方块
cube_pose = sample_box_pose() # [x, y, z, q1, q2, q3, q4]
print("方块位置(mm): ", cube_pose[:3]*1000)
# 初始关节转角
START_LEFT_THETA = np.array([15, -10, -60, -80, 75, 65, -150])*DEG2RAD
START_RIGHT_THETA = np.array([15, -10, -60, -80, 75, 65, -150])*DEG2RAD
START_LEFT_THETA = np.array([-0, 90, 0, 90, 0, 90, 0])*DEG2RAD
START_RIGHT_THETA = np.array([0, 90, 0, 90, 0, -90, 0])*DEG2RAD
with physics.reset_context():
    box_start_idx = physics.model.name2id('red_box_joint', 'joint')
    physics.data.qpos[box_start_idx : box_start_idx + 7] = cube_pose
    physics.data.qpos[:7] = START_LEFT_THETA
    physics.data.qpos[13:20] = START_RIGHT_THETA

show_robot(physics, 'show_middle')

# ---------- 正运动分析 ----------
TARGET_LEFT_POSE = np.array([0, -90, 0, 90, 0, 90, 0])*DEG2RAD
TARGET_RIGHT_POSE = np.array([0, -90, 0, 90, 0, 90, 0])*DEG2RAD
TARGET_RIGHT_POSE = np.array([-9, -90, 17, -10, -108, -84, 9])*DEG2RAD
# robot = init_robot('172.30.1.155')
#
# _, pose_JAKA2 = robot.kine_forward7(TARGET_RIGHT_POSE)

SIM_DURATION = 10 # (seconds)
FRAME_RATE = 30 # (fps)
n_frames = int(SIM_DURATION * FRAME_RATE)
now_time = 0

# allocate
sim_time = np.zeros(n_frames)
position = np.zeros((n_frames, 14)) 
velocity = np.zeros((n_frames, 14))
acceleration = np.zeros((n_frames, 14))
frames = []

# simulate and save data
physics.data.ctrl[:7] = TARGET_LEFT_POSE
physics.data.ctrl[9:16] = TARGET_RIGHT_POSE
for i in range(n_frames):
    while physics.data.time * FRAME_RATE < i:
        tic = time.time()
        physics.step()
        now_time += time.time() - tic
    sim_time[i] = now_time
    position[i, :7] = physics.data.qpos[:7]
    position[i, 7:] = physics.data.qpos[9:16]
    velocity[i, :7] = physics.data.qvel[:7]
    velocity[i, 7:] = physics.data.qvel[9:16]
    acceleration[i, :7] = physics.data.qacc[:7]
    acceleration[i, 7:] = physics.data.qacc[9:16]

    frame = physics.render(240, 320, camera_id="show_middle")
    frames.append(frame.copy())

# plot
_, ax = plt.subplots(3, 2, sharex=True, figsize=(7, 10))

ax[0,0].plot(sim_time, position[:, :7] * RAD2DEG)
ax[0,0].set_title('left arm position')
ax[0,0].set_ylabel('deg')

ax[0,1].plot(sim_time, position[:, 7:] * RAD2DEG)
ax[0,1].set_title('right arm position')
ax[0,1].set_ylabel('deg')

ax[1,0].plot(sim_time, velocity[:, :7] * RAD2DEG)
ax[1,0].set_title('left arm velocity')
ax[1,0].set_ylabel('deg/s')

ax[1,1].plot(sim_time, velocity[:, 7:] * RAD2DEG)
ax[1,1].set_title('right arm velocity')
ax[1,1].set_ylabel('deg/s')

ax[2,0].plot(sim_time, acceleration[:, :7] * RAD2DEG)
ax[2,0].set_title('left arm acceleration')
ax[2,0].set_ylabel('deg/s^2')

ax[2,1].plot(sim_time, acceleration[:, 7:] * RAD2DEG)
ax[2,1].set_title('right arm acceleration')
ax[2,1].set_ylabel('deg/s^2')

plt.show()

ax = plt.subplot()
img = physics.render(height=480, width=640)
plt_img = ax.imshow(img)

anim = FuncAnimation(plt.gcf(), lambda i: plt_img.set_data(frames[i]), frames=len(frames), interval=1000/FRAME_RATE)

plt.show()