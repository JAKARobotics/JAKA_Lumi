import sys

import numpy
from pygments.lexer import combined

sys.path.append("/home/slishy/Code/ACT/JAKASDK/JAKA_SDK_WIN_DualArm")
import time
import numpy as np
import jkrc

RAD2DEG = 180/3.1415926
DEG2RAD = 3.1415926/180
class Robot:
    def __init__(self, ip):
        self.robot = jkrc.RC(ip)  # 将 robot 保存为实例属性
        self.robot.login()
        self.robot.power_on()
        self.robot.enable_robot()
        self.robot.servo_move_enable(True)
        flag, _ = self.robot.get_robot_status()
        if flag == -1:
            raise Exception("机器人未连接")
        print("机器人已连接✔")

    def get_joint_position(self):
        flag, _ = self.robot.get_joint_position()  # 使用实例属性 self.robot
        grapper = self.robot.get_analog_output(iotype = 2,index = 3)
        grapper = grapper[1] * 0.001
        p = []
        if flag == 0:
            p = list(_)
            p.append(grapper)
            # print("The joint position is:", p)
        else:
            print("Something happened, the error code is:", flag)
            p=[]
        return  p
    def get_joint_vel(self):
        flag, _ = self.robot.get_robot_status()
        vel = []
        for i in range(7):
            vel.append(_[20][5][i][3])
        grapper = self.robot.get_analog_output(iotype=2, index=3)
        grapper = grapper[1] * 0.001
        vel.append(grapper)
        # print("The joint vel is:", vel)
        return vel
    def move_robot(self,joint_pos):

        self.robot.servo_j7_extend(joint_pos,0,18)
    def set_grapper(self,i):
        self.robot.set_analog_output(iotype=2, index=3,value = i * 1000)
if __name__ == '__main__':
    left_robot = Robot("192.168.2.222")
    right_robot = Robot("192.168.2.223")
    # right_robot.set_grapper(1)
    for i in range(100):
        print('robot joint pos:',left_robot.get_joint_position()+right_robot.get_joint_position())
        print('robot joint vel:', left_robot.get_joint_vel() + right_robot.get_joint_vel())