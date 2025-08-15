# JAKA SDK 基础操作
import numpy as np

from JAKA_SDK_WIN_DualArm import jkrc
from JAKA_utils import *
RAD2DEG = 180/3.1415926

COORD_BASE = 0 # 世界或者当前的用户坐标系
COORD_JOINT = 1 # 关节空间
COORD_TOOL = 2 #工具坐标系

ABS = 0 # 绝对运动
INCR = 1 # 增量运动
# 启动 JAKA 机器人
ip_left = '192.168.2.222'
ip_right = '192.168.2.223'
robot = init_robot(ip_left)

ret2 = robot.get_tcp_position()
t = transfer_JAKA2SIM(ret2[1])
print(t)
ret2[1][3] = ret2[1][3]*RAD2DEG
ret2[1][4] = ret2[1][4]*RAD2DEG
ret2[1][5] = ret2[1][5]*RAD2DEG
print(ret2)
