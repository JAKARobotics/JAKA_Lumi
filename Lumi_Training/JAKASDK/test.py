import os
from JAKA_utils import *
np.set_printoptions(precision=2, suppress=True)
XML_DIR = './assets'

# ---------- 初始化 ----------
# 启动模拟环境
xml_path = os.path.join(XML_DIR, f'bimanual_JAKA_pos.xml')
physics = mujoco.Physics.from_xml_path(xml_path)

# ---------- 任务初始化 ----------
# 随机生成方块
cube_pose = sample_box_pose() # [x, y, z, q1, q2, q3, q4]
print("方块在SIM环境下位置(mm): ", cube_pose[:3]*1000)
cube_pose = np.array([0.20, 0.305, 0.523, 1, 0, 0, 0])
# 初始化关节转角
START_LEFT_THETA = np.array([15, -10, -60, -80, 75, 65, -150])*DEG2RAD
START_RIGHT_THETA = np.array([-15, -10, 80, -80, -75, -65, 150])*DEG2RAD
START_RIGHT_THETA = np.array([50, -93, -60, -75, -16, -70, 150])*DEG2RAD
with physics.reset_context():
    # box_start_idx = physics.model.name2id('red_box_joint', 'joint')
    # physics.data.qpos[box_start_idx : box_start_idx + 7] = cube_pose.copy()
    physics.data.qpos[:7] = START_LEFT_THETA
    physics.data.qpos[13:20] = START_RIGHT_THETA
# show_robot(physics, 'show_middle')

# 逆解, 获得目标位姿
# TARGET_LEFT_POSE = mujoco_inverse_from_SDK(robot, physics, tr_SIM2JAKA_left, START_LEFT_THETA, cube_pos)
# 目标转角
TARGET_RIGHT_POSE2 = np.array([0, -90, 0, 90, 0, 90, 0])*DEG2RAD
# 目标上空转角
cube_pose[2] += 0.16
TARGET_RIGHT_POSE4 = np.array([0, -90, 0, 90, 0, 90, 0])*DEG2RAD
cube_pose[2] += 0.1
TARGET_RIGHT_POSE1 = np.array([0, -90, 0, 90, 0, 90, 0])*DEG2RAD
cube_pose[2] += 0.3
TARGET_RIGHT_POSE3 = np.array([0, -90, 0, 90, 0, 90, 0])*DEG2RAD

print("右臂目标转角(deg): ", np.array(TARGET_RIGHT_POSE2)*RAD2DEG)

# 查看目标位姿
# physics.data.qpos[15:22] = TARGET_RIGHT_POSE2
# physics.step()
# show_robot(physics, 'top')
# show_robot(physics, 'show_middle')
# physics.data.qpos[15:22] = TARGET_RIGHT_POSE2
# physics.step()
# show_robot(physics, 'top')
# show_robot(physics, 'show_middle')

# ---------- 完成抓取任务 ----------
SIM_DURATION = 10 # (seconds)
FRAME_RATE = 30 # (fps)
# n_frames = int(SIM_DURATION * FRAME_RATE)
now_time = 0
# allocate
frames = []

# 1. 右臂到达目标上空
target_pose = np.array([0.691, -1.23, -1.6, -1.2, -0.346, -1.1, 0])
mujoco_simulate(physics, target_pose, 'right_arm', camera_id='show_middle', sim_duration=1, frame_rate=FRAME_RATE, frames=frames) 

# 2. 打开夹爪
# mujoco_simulate(physics, target_pose, 'right_open', camera_id='show_middle', sim_duration=1, frame_rate=FRAME_RATE, frames=frames)

# 3. 右臂下降
target_pose = np.array([-0.0628, -1.27, -1.6, -0.99, 0, -0.487, -1.45])
mujoco_simulate(physics, target_pose, 'right_arm', camera_id='show_middle', sim_duration=1, frame_rate=FRAME_RATE, frames=frames)

# 4. 抓取物体
mujoco_simulate(physics, target_pose, 'right_close', camera_id='show_middle', sim_duration=1, frame_rate=FRAME_RATE, frames=frames)
# 4. 右臂上升
target_pose = np.array([0.3, -1.27, -1.6, -0.99, 0, -0.487, -1.45])
mujoco_simulate(physics, target_pose, 'right_arm', camera_id='show_middle', sim_duration=1, frame_rate=FRAME_RATE, frames=frames) 

# 创建视频

ax = plt.subplot()
img = physics.render(height=480, width=640)
plt_img = ax.imshow(img)

anim = FuncAnimation(plt.gcf(), lambda i: plt_img.set_data(frames[i]), frames=len(frames), interval=1000/FRAME_RATE)
anim.save('grab_cube.mp4', writer='ffmpeg', fps=FRAME_RATE)
plt.show()