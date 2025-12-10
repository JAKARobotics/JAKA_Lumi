# coding:UTF-8
'''
JAKA SDK Python API custom-made software development (CSD)
Discription:
    JAKA robot movement control library.
'''
import os
import time
import sys
# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取compose目录路径（当前目录的父目录）
compose_dir = os.path.dirname(current_dir)
# 将compose目录添加到sys.path
sys.path.append(compose_dir)
try:
    # 方法1：直接导入.so文件
    import sys
    import os
    
    # 将JAKA_SDK_LINUX目录添加到系统路径
    sdk_path = os.path.join(compose_dir, 'JAKA_SDK_WINDOWS')
    sys.path.append(sdk_path)
    
    # 尝试直接导入jkrc.so
    import jkrc
    print("[INFO] 成功导入jkrc.so")
except Exception as e1:
    try:
        # 方法2：作为模块导入
        from JAKA_SDK_WINDOWS import jkrc
        print("[INFO] 成功从JAKA_SDK_WINDOWS模块导入jkrc")
    except Exception as e2:
        raise NameError(f"JAKA SDK path error! 无法导入jkrc模块: {str(e1)} / {str(e2)}")

class JAKA():
    # parameters
    _ABS = 0
    _INRC = 1
    _homePose = None

    def __init__(self, address, connect=True):
        self.address = address
        self.robot = None
        if (connect):
            self.jaka_connect()

    def _login(self):  # 3,5
        self.jaka_connect()

    def _logout(self):  # 4,6
        self.robot_disconnect()

    def _get_sdk_version(self):  # 9
        ret = self.robot.get_sdk_version()
        # print("SDK version	is:", ret[1])
        return ret

    def _get_controller_ip(self):  # 10
        ret = self.robot.get_controller_ip()
        print("controller ip is:", ret[1])
        return ret[1]

    def _drag_mode_enable(self):  # 11
        self.robot.drag_mode_enable(True)
        ret = self.robot.is_in_drag_mode()
        return ret[0]

    def _drag_mode_unable(self):  # 12
        self.robot.drag_mode_enable(False)
        ret = self.robot.is_in_drag_mode()
        return ret[0]

    def _is_in_drag_mode(self):
        ret = self.robot.is_in_drag_mode()
        return ret[0]

    def _set_debug_mode(self):  # 14
        ret = self.robot.set_debug_mode(True)
        return ret[0]

    def _unset_debug_mode(self):  # 15
        ret = self.robot.set_debug_mode(False)
        return ret[0]

    def send_tio(self,channel,cmd):
        return self.robot.send_tio_rs_command(channel, cmd)


    def set_user_frame_origin(self,id,user_frame, name):
        # '''
        # :param id: 用户坐标系 ID，可选 ID 为 1 到 10,0 代表机器人基坐标系
        # :param user_frame:用户坐标系参数[x,y,z,rx,ry,rz]
        # :param name:用户坐标系别名
        # :return:
        # '''
        ret=self.robot.set_user_frame_data(id, user_frame, name)
        if ret[0]==0:
            return 0
        else:
            return -1

    def get_user_frame_origin(self):
        # '''
        # :return: 成功：(0, id, tcp), id : 用户坐标系 ID，可选 ID 为 1 到 10, 0 代表机器人基坐标系
        #                             tcp: 用户坐标系参数[x,y,z,rx,ry,rz]
        # '''
        ret=self.robot.get_user_frame_data()
        return ret

    def set_user_frame_id_origin(self,id):
        ret = self.robot.set_user_frame_id(id)
        if ret[0]==0:
            return 0
        else:
            return -1

    def get_user_frame_id_origin(self):
        ret = self.robot.get_user_frame_id() # 成功：(0, id)，id 值范围为 0 到 10, 0 代表机器人基坐标系
        if ret[0] == 0:
            return ret[1]
        else:
            return -1
    

    def grab_action(self,send_tio):
        if send_tio == 0:
            # open
            self.robot.set_digital_output(1, 0, 0)# IO_TOOL =1,设置 DO1 的引脚输出值为 0
            time.sleep(0.1)
            self.robot.set_digital_output(1, 1, 0)#设置 DO2 的引脚输出值为 0
            time.sleep(0.5)
            
        if send_tio == 1:
            # close
            self.robot.set_digital_output(1, 0, 1)# IO_TOOL =1,设置 DO1 的引脚输出值为 0
            time.sleep(0.1)
            self.robot.set_digital_output(1, 1, 0)#设置 DO2 的引脚输出值为 0
            time.sleep(0.5)
        return 

    def joint_move_origin(self, joints, sp,move_mode):
        # joints = 180*joints/pi
        move_mode=move_mode if move_mode else 0
        sp=sp if sp else 30
        ret=self.robot.joint_move(joint_pos=joints, move_mode=move_mode, is_block=True, speed=sp)
        if ret[0] == 0:
            return 0
        else:
            return -1

    def get_joints(self):
        ret = self.robot.get_joint_position()
        if ret[0] == 0:
            return ret[1]
        else:
            return None

    def tcp_pos(self, homepos):
        ret = self.robot.kine_forward(homepos)
        if ret[0] == 0:
            return ret[1]
        
    def set_analogoutput(self,iotype,index,value):
        ret = self.robot.set_analog_output(iotype,index,value)
        return ret


    # 计算指定位姿在当前工具、当前安装角度以及当前用户坐标系设置下的逆解。
    def kine_inverse_origin(self,ref_pos, cartesian_pose):
        # '''
        # :param ref_pos: 关节空间参考位置，建议选用机器人当前关节位置。
        # :param cartesian_pose: 笛卡尔空间位姿计算结果.
        # :return:(0 , joint_pos)	joint_pos 是一个包含 6 位元素的元组 (j1, j2, j3,	j4, j5, j6)，
        #                                 j1, j2, j3, j4, j5, j6 分别代表关节 1 到关节 6 的角度值
        # '''
        ret=self.robot.kine_inverse(ref_pos, cartesian_pose)
        return ret
    
    
    def liner_move(self, pos, sp):
        # add 180
        pos_now = self.robot.get_joint_position()
        if pos_now[0] == 0:
            print('now pos', pos_now)
            target_joint = self.robot.kine_inverse(pos_now[1], pos)
            if target_joint[0] == 0:
                de = target_joint[1][5] - pos_now[1][5]
                print("1::::", de / 3.1415926 * 180)
                if (abs(de) > (3.1415 / 2)):
                    joint_pos = []
                    for i in target_joint[1]:
                        joint_pos.append(i)
                    if de > 0:
                        joint_pos[5] -= 3.1415
                    else:
                        joint_pos[5] += 3.1415

                    print("2::: ", (joint_pos[5] - pos_now[1][5]) / 3.1415926 * 180)
                    ret, tcp_pos = self.robot.kine_forward(joint_pos)
                else:
                    tcp_pos = pos

                print("move before: ", pos_now)
                ret = self.robot.linear_move(end_pos=tcp_pos, move_mode=self._ABS, is_block=True, speed=120)
                # ret = self.robot.linear_move(end_pos = pos, move_mode = self._ABS, is_block = True, speed = sp)
                pos_now = self.robot.get_joint_position()
                print("move after:", pos_now)
                if (ret[0] == 0):
                    pass
                else:
                    print(ret[0])
            else:
                print(target_joint[0])
            # time.sleep(0.08)
        else:
            print('[JAKA] error!!!!!', pos_now)

    # '''
    # INCRPose : increase position [X, Y, Z, Roll, Pitch, Yaw]
    # '''

    def moveInWorldCoordinate(self, INCRPose, speedInput=20):
        curPose = self.getpos6DoF()
        tarPose = [0, 0, 0, 0, 0, 0]
        for i in range(3):
            INCRPose[i] = curPose[i] + INCRPose[i]
        ret = self.robot.linear_move(end_pos=INCRPose, move_mode=self._ABS, is_block=True, speed=speedInput)
        if (ret[0] == -4):
            print("[JAKA] Inverse solution failed")
        return ret


    # get pose
    # get [X, Y, Z] pose
    def get_posXYZ(self):
        ret = self.robot.get_tcp_position()
        if ret[0] == 0:
            return ret[1][0:3]

    def get_tcp_pos(self):
        ret = self.robot.get_tcp_position()
        if ret[0] == 0:
            return ret[1]

    # get [Roll, Pitch, Yaw] pose
    def get_posRPY(self):
        ret = self.robot.get_tcp_position()
        ret = self.robot.get_robot_status()
        if ret[0] == 0:
        #     return ret[1][18][3:]
        # else:
            print("positon get:", ret)
        # get [X, Y, Z, Roll, Pitch, Yaw] pose

    def get_pos6DoF(self):
        ret = self.robot.get_robot_status()
        return ret[1][18]

    # download program
    def download_file(self, local, remote, opt=2):
        self.robot.init_ftp_client()
        result = self.robot.download_file(local, remote, opt)
        print('download file  from APP state is : ' + str(result))
        self.robot.close_ftp_client()

    # upload  program
    def upload_file(self, local, remote, opt=2):
        self.robot.init_ftp_client()
        result = self.robot.upload_file(local, remote, opt)
        print('upload file to APP, the state is : ' + str(result))
        self.robot.close_ftp_client()

    # run program
    def run_program(self, program):
        # program:'./sdk_exam'
        ret = self.robot.program_load(program)
        if ret[0] == 0:
            print('load program success! start running......')
        self.robot.get_loaded_program()
        ret = self.robot.program_run()
        if ret[0] == 0:
            print('running program over !!! ')

    # disconnect from the robot
    def robot_disconnect(self):
        self.robot.disable_robot()
        print("[JAKA] disable successfully")
        self.robot.power_off()
        print("[JAKA] power_off successfully")
        self.robot.logout()
        print("[JAKA] logout successfully")

    def jaka_connect(self):
        print(self.address)
        self.robot = jkrc.RC(self.address)
        if not self.robot:
            return False
        
        print("[JAKA] logining...")
        ret=self.robot.login(1)[0]
        print("login status: "+str(ret))
        if ret != 0:
            return False


        # 获取power_on结果
        power_result = self.robot.power_on()[0]
        print(f"[JAKA] power_on result: {power_result}")
        
        # 获取enable_robot结果
        enable_result = self.robot.enable_robot()[0]
        print(f"[JAKA] enable_robot result: {enable_result}")

        #检查结果，如果都返回0则成功，否则失败
        if power_result == 0 and enable_result == 0:
            print("[JAKA] power_on和enable_robot都执行成功")
            return True
        else:
            print("[JAKA] power_on或enable_robot执行失败")
            return False

