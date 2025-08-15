import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from dm_control import mujoco
sys.path.append("/home/slishy/Code/act-Mine/JAKASDK_OpenLoop/JAKA_SDK_WIN_DualArm")
import jkrc

RAD2DEG = 180/3.1415926
DEG2RAD = 3.1415926/180

# =================================================================================
# Basic Tools
# =================================================================================
# rpy, rotate in 'zxz'
def rpy2rot(rpy):
    # rpy: [rx, ry, rz]
    rx, ry, rz = rpy
    R_x = np.array([[1, 0, 0],
                    [0, np.cos(rx), -np.sin(rx)],
                    [0, np.sin(rx), np.cos(rx)]])
    R_y = np.array([[np.cos(ry), 0, np.sin(ry)],
                    [0, 1, 0],
                    [-np.sin(ry), 0, np.cos(ry)]])
    R_z = np.array([[np.cos(rz), -np.sin(rz), 0],
                    [np.sin(rz), np.cos(rz), 0],
                    [0, 0, 1]])
    R = R_z @ R_y @ R_x
    return R

def rpy2quat(rpy):
    # rpy: [rx, ry, rz]
    rx, ry, rz = rpy
    q0 = np.cos(rx/2)*np.cos(ry/2)*np.cos(rz/2) + np.sin(rx/2)*np.sin(ry/2)*np.sin(rz/2)
    q1 = np.sin(rx/2)*np.cos(ry/2)*np.cos(rz/2) - np.cos(rx/2)*np.sin(ry/2)*np.sin(rz/2)
    q2 = np.cos(rx/2)*np.sin(ry/2)*np.cos(rz/2) + np.sin(rx/2)*np.cos(ry/2)*np.sin(rz/2)
    q3 = np.cos(rx/2)*np.cos(ry/2)*np.sin(rz/2) - np.sin(rx/2)*np.sin(ry/2)*np.cos(rz/2)
    return np.array([q0, q1, q2, q3])

# Quaternion
def quat2rot(quat):
    # quat: [w, x, y, z]
    w, x, y, z = quat
    R = np.array([[1-2*y**2-2*z**2, 2*x*y-2*z*w, 2*x*z+2*y*w],
                  [2*x*y+2*z*w, 1-2*x**2-2*z**2, 2*y*z-2*x*w],
                  [2*x*z-2*y*w, 2*y*z+2*x*w, 1-2*x**2-2*y**2]])
    return R

def quat2rpy(quat):
    # quat: [w, x, y, z]
    w, x, y, z = quat
    rpy = np.zeros(3)
    rpy[0] = np.arctan2(2*(w*x+y*z), 1-2*(x**2+y**2))
    rpy[1] = np.arcsin(2*(w*y-z*x))
    rpy[2] = np.arctan2(2*(w*z+x*y), 1-2*(y**2+z**2))
    return rpy

# Transformation
def tr2pose(T):
    pos = T[:3,3]
    rpy = np.zeros(3)
    rpy[0] = np.arctan2(T[2,1], T[2,2])
    rpy[1] = np.arctan2(-T[2,0], np.sqrt(T[2,1]**2 + T[2,2]**2))
    rpy[2] = np.arctan2(T[1,0], T[0,0])
    return np.concatenate((pos, rpy))

# Pose
def pose2tr(pose):
    # pose: [x, y, z, rx, ry, rz]
    pos = pose[:3]
    rpy = pose[3:]
    T = np.eye(4)
    T[:3, 3] = pos
    # print("rpy: ", rpy)
    T[:3, :3] = rpy2rot(rpy)
    return T

# Xpos Xquat
def xpos_xquat2tr(xpos, xquat):
    # xpos: [x, y, z]
    # xquat: [w, x, y, z]
    T = np.eye(4)
    T[:3, 3] = xpos
    T[:3, :3] = quat2rot(xquat)
    return T

def xpos_xquat2pose(xpos, xquat):
    # [x, y, z, rx, ry, rz]
    return np.concatenate((xpos, quat2rpy(xquat)))

# JAKA API
def JAKA_pose2tr(pose, robot):
    # pose: [x, y, z, rx, ry, rz]
    _, rot = robot.rpy_to_rot_matrix(pose[3:])
    JAKA_T_total = np.eye(4)
    JAKA_T_total[:3, :3] = rot
    JAKA_T_total[:3, 3] = pose[:3]

    return JAKA_T_total

# =================================================================================
# JAKA SDK Tools
# =================================================================================
def init_robot(ip='192.168.2.222'):
    robot = jkrc.RC(ip) #返回一个机器人对象
    # 登录
    robot.login()
    # 打开电源
    robot.power_on()
    # # 关闭电源
    # robot.power_off()
    # # 注销
    # robot.logout()
    flag, _ = robot.get_robot_status()
    if flag == -1:
        raise Exception("机器人未连接")
    print("机器人已连接✔")
    return robot
def get_left_transfer_matrix(robot , physics):
    # 获得从 SIM2JAKA 的转移矩阵, 注意模型里轴的方向需要与实际机器人一致
    theta1 = np.array([-0.22369246110698057, -0.7501153758314308, 0.5360440750040432, -1.1680385236835042, -3.2656943366699953, -1.2238649962747896, 0.0])
    # theta2 = np.array(
    #     [0.016645006113534245, -0.5882215347015856, -0.11718570647709768, -1.689546318335413, -0.2572095025086101,
    #      -0.7259444214265669, -1.364552674939218])
    # 正解
    # mm
    # pose_mujoco1, T_mujoco1 = mujoco_kine_forward7(physics, theta1, arm)
    pose_mujoco, T_mujoco = mujoco_kine_forward7(physics, theta1, 'left_arm')
    print("pose_mujoco : ", pose_mujoco)
    # _, pose_JAKA1 = robot.kine_forward7(theta1)
    _, pose_JAKA = robot.kine_forward7(theta1)
    print("pose_JAKA2 : ", pose_JAKA)
    # T_JAKA1 = JAKA_pose2tr(pose_JAKA1, robot)
    T_JAKA = JAKA_pose2tr(pose_JAKA, robot)
    # transfer_matrix1 = T_JAKA1 @ np.linalg.inv(T_mujoco1)
    # 矩阵np.linalg.inv求逆运算
    transfer_matri = T_JAKA @ np.linalg.inv(T_mujoco)
    return transfer_matri
def get_right_transfer_matrix(robot , physics):
    # 获得从 SIM2JAKA 的转移矩阵, 注意模型里轴的方向需要与实际机器人一致
    # theta1 = np.array([-0.22369246110698057, -0.7501153758314308, 0.5360440750040432, -1.1680385236835042, -3.2656943366699953, -1.2238649962747896, 0.0])
    theta1 = np.array(
        [0.016645006113534245, -0.5882215347015856, -0.11718570647709768, -1.689546318335413, -0.2572095025086101,
         -0.7259444214265669, -1.364552674939218])
    # 正解
    # mm
    # pose_mujoco1, T_mujoco1 = mujoco_kine_forward7(physics, theta1, arm)
    pose_mujoco, T_mujoco = mujoco_kine_forward7(physics, theta1, 'right_arm')
    print("pose_mujoco : ", pose_mujoco)
    # _, pose_JAKA1 = robot.kine_forward7(theta1)
    _, pose_JAKA = robot.kine_forward7(theta1)
    print("pose_JAKA2 : ", pose_JAKA)
    # T_JAKA1 = JAKA_pose2tr(pose_JAKA1, robot)
    T_JAKA = JAKA_pose2tr(pose_JAKA, robot)
    # transfer_matrix1 = T_JAKA1 @ np.linalg.inv(T_mujoco1)
    # 矩阵np.linalg.inv求逆运算
    transfer_matri = T_JAKA @ np.linalg.inv(T_mujoco)
    return transfer_matri
def get_transfer_matrix(robot, physics, arm):
    # 获得从 SIM2JAKA 的转移矩阵, 注意模型里轴的方向需要与实际机器人一致
    # theta1 = np.array([-0.22369246110698057, -0.7501153758314308, 0.5360440750040432, -1.1680385236835042, -3.2656943366699953, -1.2238649962747896, 0.0])
    theta2 = np.array([0.016645006113534245, -0.5882215347015856, -0.11718570647709768, -1.689546318335413, -0.2572095025086101, -0.7259444214265669, -1.364552674939218])
    # 正解
    # mm
    # pose_mujoco1, T_mujoco1 = mujoco_kine_forward7(physics, theta1, arm)
    pose_mujoco2, T_mujoco2 = mujoco_kine_forward7(physics, theta2, arm)
    print("pose_mujoco2 : " , pose_mujoco2)
    # _, pose_JAKA1 = robot.kine_forward7(theta1)
    _, pose_JAKA2 = robot.kine_forward7(theta2)
    print("pose_JAKA2 : " ,pose_JAKA2)
    # T_JAKA1 = JAKA_pose2tr(pose_JAKA1, robot)
    T_JAKA2 = JAKA_pose2tr(pose_JAKA2, robot)
    # print("SIM_pose: ", pose_mujoco2 - pose_mujoco1)
    # print("JAKA_pose: ", np.array(pose_JAKA2) - np.array(pose_JAKA1))

    # transfer_matrix1 = T_JAKA1 @ np.linalg.inv(T_mujoco1)
    transfer_matrix1 = T_JAKA2 @ np.linalg.inv(T_mujoco2)
    # print("SIM2JAKA: ", transfer_matrix1)
    # print("SDK解算误差(mm): ", (transfer_matrix1-transfer_matrix2)[:3, 3])

    # displacement = np.array(pose_mujoco2) - np.array(pose_mujoco1)
    # print("dis(mujoco): ", displacement)
    # displacement = np.array(pose_JAKA2) - np.array(pose_JAKA1)
    # print("dis(JAKA): ", displacement)

    # tmp1 = transfer_matrix2 @ T_mujoco1
    # tmp2 = transfer_matrix2 @ T_mujoco2
    # tmp = tr2pose(tmp2) - tr2pose(tmp1)
    # print("dis(JAKA): ", tmp)
    # print('pose1_mujoco', pose_mujoco1)
    # print('pose1_JAKA', pose_JAKA1)
    return transfer_matrix1

def transfer_SIM2JAKA(transfer_matrix, pose):
    # pose: [x, y, z, rx, ry, rz]
    T = pose2tr(pose)
    T_JAKA = transfer_matrix @ T
    return tr2pose(T_JAKA)

def transfer_JAKA2SIM(transfer_matrix, pose):
    # pose: [x, y, z, rx, ry, rz]
    T = pose2tr(pose)
    T_SIM = np.linalg.inv(transfer_matrix) @ T
    return tr2pose(T_SIM)

def convert_to_JAKA_base(pose, tr_SIM2JAKA):
    T1 = pose2tr(pose)
    T2 = tr_SIM2JAKA @ T1
    return tr2pose(T2)

def generate_trajectory_theta2pose(robot, init_theta, target_theta, linear_insert_num):
    thetas = np.linspace(init_theta, target_theta, linear_insert_num)
    # print("thetas: ", thetas)
    # 正解
    traj = []
    for theta in thetas:
        _, ret = robot.kine_forward7(theta)
        traj.append(ret)
    return traj

def inj_thetas(thetas, num):
    # 线性差分
    thetas = np.array(thetas)
    thetas_inj = []
    for i in range(len(thetas)-1):
        thetas_inj.append(thetas[i])
        for j in range(1, num):
            thetas_inj.append(thetas[i] + (thetas[i+1]-thetas[i])*j/num)
    thetas_inj.append(thetas[-1])
    return thetas_inj

def generate_trajectory(robot, start_theta, target_pose_sim):
    # 转换到JAKA坐标系下
    # target_pose_JAKA = convert_to_JAKA_base(target_pose_sim, 'left_arm')
    # target_pose_JAKA = robot.kine_inverse7(target_pose_sim, target_pose_sim)
    # 逆解
    ans = robot.kine_inverse7(start_theta, target_pose_sim)
    # _, joint_pos = robot.kine_inverse7(joint_pos, pose_series[i])
    if len(ans) == 1:
        raise Exception("逆解失败")
    joint_pos = ans[1]

    return joint_pos


# =================================================================================
# dm_control Tools
# =================================================================================

def get_tr_from_name(physics, name):
    # Get the transform matrix of the body with the given name
    xpos = physics.named.data.xpos[name] * 1000 # m -> mm
    xquat = physics.named.data.xquat[name]
    print('xpos: ', xpos)
    print('xquat: ', xquat)
    T = xpos_xquat2tr(xpos, xquat)
    return np.linalg.inv(T)

def get_pose_sim2DH(physics, T, arm):
    if arm == 'left_arm':
        T_DH = get_tr_from_name(physics, 'l1')
        return tr2pose(T @ np.linalg.inv(T_DH))

    elif arm == 'right_arm':
        T_DH = get_tr_from_name(physics, 'r1')
        return tr2pose(T @ np.linalg.inv(T_DH))

def get_T_sim2baseArm(physics):
    return get_tr_from_name(physics, 'JAKA_arm_left'), get_tr_from_name(physics, 'JAKA_arm_right')

def mujoco_kine_forward7(physics, theta, arm):
    xpos = []
    xquat = []
    if arm == 'left_arm':
        physics.data.qpos[:7] = theta
        # print("theta_left(rad): ", theta)
        physics.step()
        xpos = physics.named.data.xpos['JAKA_arm_left/camera_focus'] * 1000 # m -> mm
        xquat = physics.named.data.xquat['JAKA_arm_left/camera_focus']
    elif arm == 'right_arm':
        # print("theta_right(rad): ", theta)
        physics.data.qpos[13:20] = theta
        physics.step()
        xpos = physics.named.data.xpos['JAKA_arm_right/camera_focus'] * 1000 # m -> mm
        xquat = physics.named.data.xquat['JAKA_arm_right/camera_focus']
    # print('xpos: ', xpos)
    # print('xquat: ', xquat)
    return xpos_xquat2pose(xpos, xquat), xpos_xquat2tr(xpos, xquat)
#
# def mujoco_inverse_from_SDK(robot, tr_SIM2JAKA, START_THETA, target_pose):
#     ret = robot.kine_forward7(START_THETA)
#     ret = ret[1]
#     ret = np.array(ret)
#     ret[3] = ret[3] * RAD2DEG
#     ret[4] = ret[4] * RAD2DEG
#     ret[5] = ret[5] * RAD2DEG
#     print("当前手臂真实位置: ", ret)
#     # target_pos = [0,0,0]
#     # target_pos[0] = target_pose[0] * 1000 # m -> mm
#     # target_pos[1] = target_pose[1] * 1000
#     # target_pos[2] = target_pose[2] * 1000
#     target_pos = [0,0,0]
#     target_pos[0] = target_pose[0]
#     target_pos[1] = target_pose[1]
#     target_pos[2] = target_pose[2]
#     print('target_pos',target_pos)
#     target_pose = np.concatenate((target_pos, target_pose[3:]))
#     # target_pose = np.concatenate((target_pos, np.array([180, 0, 90])*DEG2RAD))
#     target_T = pose2tr(target_pose)
#     #虚拟环境的木块位置转换到jaka坐标下的位置
#     target_T_JAKA = tr_SIM2JAKA @ target_T
#     target_pose_JAKA = tr2pose(target_T_JAKA)
#     # x = 165 * DEG2RAD
#     # target_pose_JAKA[5] = x
#     # target_pose_JAKA[0] = ret[0]
#     # target_pose_JAKA[1] = ret[1]
#     # target_pose_JAKA[2] = ret[2]
#     print("目标位置在JAKA系下位置(mm): ", target_pose_JAKA[:3], "角度: ", target_pose_JAKA[3:]*RAD2DEG)
#     # 逆解
#     ans = robot.kine_inverse7(START_THETA, target_pose_JAKA)
#     if len(ans) == 1:
#         raise Exception("逆解失败")
#     target_theta = ans[1]
#     return target_theta
def mujoco_inverse_from_SDK(robot, tr_SIM2JAKA, START_POSE, target_pose):
    ret = robot.kine_forward7(START_POSE)
    ret = ret[1]
    ret = np.array(ret)
    ret[3] = ret[3] * RAD2DEG
    ret[4] = ret[4] * RAD2DEG
    ret[5] = ret[5] * RAD2DEG
    print("当前手臂真实位置: ", ret)
    target_pos = target_pose[:3] * 1000 # m -> mm
    target_pose = np.concatenate((target_pos, target_pose[3:]))
    # target_pose = np.concatenate((target_pos, np.array([180, 0, 90])*DEG2RAD))
    target_T = pose2tr(target_pose)
    target_T_JAKA = tr_SIM2JAKA @ target_T
    target_pose_JAKA = tr2pose(target_T_JAKA)
    print("目标位置在JAKA系下位置(mm): ", target_pose_JAKA[:3], "角度: ", target_pose_JAKA[3:]*RAD2DEG)
    # 逆解
    ans = robot.kine_inverse7(START_POSE, target_pose_JAKA)
    if len(ans) == 1:
        raise Exception("逆解失败")
    target_theta = ans[1]
    return target_theta

def sample_box_pose():
    x_range = [0.49 -0.05, 0.49 +0.05]
    y_range = [0.363-0.05, 0.363+0.05]
    z_range = [0.37,0.37]

    ranges = np.vstack([x_range, y_range, z_range])
    cube_position = np.random.uniform(ranges[:, 0], ranges[:, 1])
    cube_quat = np.array([1, 0, 0, 0])

    #!
    print(f"randomized cube position to {cube_position[:3]}")
    return np.concatenate([cube_position, cube_quat])

def show_robot(physics, camera_id=0):
    img = physics.render(height=480, width=640, camera_id=camera_id)
    fig, ax = plt.subplots(1, 1)
    plt_img = ax.imshow(img)
    plt.show()
    return plt_img

def mujoco_simulate(physics, target_theta, arm, camera_id, sim_duration, frame_rate, frames):
    n_frames = int(sim_duration * frame_rate)
    if arm == 'left_arm':
        physics.data.ctrl[:7] = target_theta
    elif arm == 'right_arm':
        physics.data.ctrl[8:15] = target_theta
    elif arm == 'both_arm':
        physics.data.ctrl[:7] = target_theta[:7]
        physics.data.ctrl[8:15] = target_theta[7:]
    elif arm == 'left_open':
        physics.named.data.ctrl['l_palm_act'] = 0
    elif arm == 'left_close':
        physics.named.data.ctrl['l_palm_act'] = 1
    elif arm == 'right_open':
        physics.named.data.ctrl['r_palm_act'] = 0
    elif arm == 'right_close':
        physics.named.data.ctrl['r_palm_act'] = 1

    print("==========================================")
    init_time=physics.data.time
    now_time=physics.data.time
    for i in range(n_frames):
        while (physics.data.time-init_time) * frame_rate < i:
            tic = time.time()
            physics.step()
            now_time += time.time() - tic
        print("time: ", now_time)

        frame = physics.render(480, 640, camera_id=camera_id)
        frames.append(frame.copy())
