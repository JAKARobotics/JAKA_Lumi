# coding:UTF-8
'''
JAKA Integrated Control System
集成JAKA机器人、外部轴和AGV的控制功能
'''
import os
import time
import requests
import json
import socket

try:
    from JAKA_SDK_LINUX import jkrc
except:
    raise NameError("JAKA SDK path error! current work path: ", os.path.abspath('.'))

from utilfs.jaka import JAKA

class JAKAIntegrated(JAKA):
    # 默认设置
    DEFAULT_EXT_VEL = 100
    DEFAULT_EXT_ACC = 100
    DEFAULT_ROB_VEL = 90

    def __init__(self, robot_ip, ext_base_url=None, agv_ip=None, agv_port=None):
        """
        初始化集成控制系统
        :param robot_ip: JAKA机器人IP地址
        :param ext_base_url: 外部轴控制基础URL
        :param agv_ip: AGV IP地址
        :param agv_port: AGV端口
        """
        # 调用父类初始化，但不立即连接
        super().__init__(robot_ip, connect=False)
        
        # 外部轴控制相关
        self.ext_base_url = ext_base_url
        if ext_base_url:
            self.EXT_MOVETO_URL = f"{ext_base_url}/moveto"
            self.EXT_SYSINFO_URL = f"{ext_base_url}/sysinfo"
            self.EXT_RESET_URL = f"{ext_base_url}/reset"
            self.EXT_ENABLE_URL = f"{ext_base_url}/enable"
            self.EXT_GETSTATE_URL = f"{ext_base_url}/status"
        
        # AGV控制相关
        self.agv_ip = agv_ip
        self.agv_port = agv_port
        
        # 加载外部轴关节限制
        self.ext_axis_limits = self._load_ext_axis_limits()
    
    def _load_ext_axis_limits(self):
        """加载外部轴关节限制参数"""
        try:
            import json
            with open('./conf/userCmdControl.json', 'r') as f:
                config = json.load(f)
            if "extAxisLimits" in config:
                return config["extAxisLimits"]
            else:
                print("警告: 未找到外部轴限制配置，使用默认值")
                return {
                    "joint1": {"min": 0, "max": 200, "desc": "升降，单位mm"}, 
                    "joint2": {"min": -140, "max": 140, "desc": "腰部旋转，单位度"},
                    "joint3": {"min": -180, "max": 180, "desc": "头部旋转，单位度"},
                    "joint4": {"min": -5, "max": 35, "desc": "头部俯仰，单位度"}
                }
        except Exception as e:
            print(f"加载外部轴限制失败: {e}，使用默认值")
            return {
                "joint1": {"min": 0, "max": 200, "desc": "升降，单位mm"}, 
                "joint2": {"min": -140, "max": 140, "desc": "腰部旋转，单位度"},
                "joint3": {"min": -180, "max": 180, "desc": "头部旋转，单位度"},
                "joint4": {"min": -5, "max": 35, "desc": "头部俯仰，单位度"}
            }
    
    def _adjust_to_joint_limits(self, point):
        """
        调整关节位置以确保在限制范围内
        :param point: 目标位置 [joint1, joint2, joint3, joint4]
        :return: (调整后的位置, 是否被调整, 调整信息)
        """
        if not hasattr(self, 'ext_axis_limits') or self.ext_axis_limits is None:
            self.ext_axis_limits = self._load_ext_axis_limits()
            
        adjusted = False
        messages = []
        result = list(point)  # 复制输入点以进行调整
        
        joint_names = ["joint1", "joint2", "joint3", "joint4"]
        
        for i, (joint_name, value) in enumerate(zip(joint_names, point)):
            if joint_name in self.ext_axis_limits:
                min_val = self.ext_axis_limits[joint_name]["min"]
                max_val = self.ext_axis_limits[joint_name]["max"]
                desc = self.ext_axis_limits[joint_name]["desc"]
                
                if value < min_val:
                    messages.append(f"{joint_name}({desc})超出最小限制: {value} < {min_val}")
                    result[i] = min_val
                    adjusted = True
                elif value > max_val:
                    messages.append(f"{joint_name}({desc})超出最大限制: {value} > {max_val}")
                    result[i] = max_val
                    adjusted = True
        
        adjustment_msg = "; ".join(messages) if messages else "无需调整"
        return result, adjusted, adjustment_msg
    
    #===========================
    # 外部轴控制功能
    #===========================
    
    def ext_check_connection(self):
        """检查外部轴连接状态"""
        if not self.ext_base_url:
            print("外部轴URL未配置")
            return False
        
        try:
            response = requests.get(self.EXT_SYSINFO_URL, timeout=2)
            if response.status_code == 200:
                print("外部轴连接正常")
                return True
            else:
                print(f"外部轴连接错误: {response.status_code}")
                return False
        except Exception as e:
            print(f"外部轴连接异常: {e}")
            return False
    
    def ext_reset(self):
        """重置所有外部轴关节"""
        if not self.ext_base_url:
            print("外部轴URL未配置")
            return False
            
        response = requests.post(self.EXT_RESET_URL, json={})
        if response.status_code == 200:
            print("外部轴重置成功")
            return True
        else:
            print(f"外部轴重置失败: {response.status_code}")
            return False
    
    def ext_enable(self, enable=True):
        """
        使能或禁用外部轴
        :param enable: True表示使能，False表示禁用
        """
        if not self.ext_base_url:
            print("外部轴URL未配置")
            return False
            
        response = requests.post(self.EXT_ENABLE_URL, json={"enable": 1 if enable else 0})
        if response.status_code == 200:
            print("外部轴" + ("使能成功" if enable else "禁用成功"))
            return True
        else:
            print(f"外部轴" + ("使能失败" if enable else "禁用失败") + f": {response.status_code}")
            return False
    
    def ext_get_state(self):
        """
        获取外部轴状态
        :return: 成功返回状态信息，失败返回None
        """
        if not self.ext_base_url:
            print("外部轴URL未配置")
            return None
            
        response = requests.get(self.EXT_GETSTATE_URL)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"获取外部轴状态失败: {response.status_code}")
            return None
    
    def ext_moveto(self, point, vel=None, acc=None):
        """
        控制外部轴移动到指定位置
        :param point: 目标位置坐标 [x, y, z, r]
        :param vel: 速度，默认100
        :param acc: 加速度，默认100
        :return: 成功返回True，失败返回False
        """
        if not self.ext_base_url:
            print("外部轴URL未配置")
            return False
            
        # 检查关节限制并调整到限制范围内
        adjusted_point, was_adjusted, adjustment_msg = self._adjust_to_joint_limits(point)
        if was_adjusted:
            print(f"警告: {adjustment_msg}")
            print(f"原始位置: {point} -> 调整后位置: {adjusted_point}")
            point = adjusted_point
            
        vel = vel if vel is not None else self.DEFAULT_EXT_VEL
        acc = acc if acc is not None else self.DEFAULT_EXT_ACC
        
        response = requests.post(
            self.EXT_MOVETO_URL,
            json={"pos": point, "vel": vel, "acc": acc},
        )
        if response.status_code == 200:
            print('外部轴移动成功!')
            return True
        else:
            print(f"外部轴移动失败: {response.status_code}")
            return False

    #===========================
    # AGV控制功能
    #===========================
    
    def _send_command_to_agv(self, command):
        """
        向AGV发送命令并接收响应
        :param command: 要发送的命令
        :return: JSON格式的响应数据，失败返回None
        """
        if not self.agv_ip or not self.agv_port:
            print("AGV连接信息未配置")
            return None
            
        try:
            # 创建TCP/IP套接字
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # 连接到服务器
                sock.connect((self.agv_ip, self.agv_port))
                
                # 发送命令
                sock.sendall(command.encode('utf-8'))
                
                # 接收响应
                response = sock.recv(4096).decode('utf-8')
                
                # 解析JSON响应
                response_json = json.loads(response)
                return response_json
        except Exception as e:
            print(f"发送AGV命令时发生错误: {e}")
            return None
    
    def agv_get_status(self):
        """
        获取AGV状态
        :return: AGV状态信息，失败返回None
        """
        response = self._send_command_to_agv("/api/robot_status")
        return response
    
    def agv_moveto(self, point_name):
        """
        控制AGV移动到指定标记点
        :param point_name: 目标点位的标记号
        :return: 成功返回True，失败返回False
        """
        # 发送移动命令
        response = self._send_command_to_agv(f"/api/move?marker={point_name}")
        if not response:
            print("发送AGV移动命令失败")
            return False
            
        print(f"AGV开始移动到标记点 {point_name}")
        print(json.dumps(response, indent=4))

        # 等待移动完成
        is_done = False
        while not is_done:
            time.sleep(0.5)
            try:
                response = self._send_command_to_agv("/api/robot_status")
                if response and response['results']['move_status'] == "succeeded":
                    is_done = True
                    print(f"AGV已到达标记点 {point_name}")
            except Exception as e:
                print(f"检查AGV状态时发生错误: {e}")
                return False
                
        return True

    #===========================
    # 集成控制功能
    #===========================
    
    def setup_system(self):
        """
        初始化整个系统
        :return: 成功返回True，失败返回False
        """
        # 连接机器人
        self.jaka_connect()
        robot_ok = True
        
        # 检查外部轴连接
        ext_ok = True
        if self.ext_base_url:
            ext_ok = self.ext_check_connection()
            if ext_ok:
                self.ext_reset()
                self.ext_enable(True)
        
        # AGV无需特别初始化
        
        return robot_ok and ext_ok
    
    def shutdown_system(self):
        """
        关闭整个系统
        """
        # 断开机器人连接
        if self.robot:
            self.robot_disconnect()
        
        # 禁用外部轴
        if self.ext_base_url:
            self.ext_enable(False)
        
        print("系统已关闭")

    def move_to_station(self, station_name, agv_marker):
        """
        移动到指定工作站
        :param station_name: 工作站名称(用于日志)
        :param agv_marker: AGV目标点位标记
        :return: 成功返回True，失败返回False
        """
        print(f"开始移动到工作站: {station_name}")
        
        if self.agv_ip and self.agv_port:
            agv_result = self.agv_moveto(agv_marker)
            if not agv_result:
                print(f"AGV移动到工作站 {station_name} 失败")
                return False
        
        print(f"已到达工作站: {station_name}")
        return True 
    
    # 扩展JAKA类的方法，使其更适用于集成控制系统
    
    def rob_moveto(self, jpos, vel=None):
        """
        控制机器人移动到指定关节角度(度数)
        :param jpos: 目标关节角度 [J1, J2, J3, J4, J5, J6]，单位为度
        :param vel: 关节速度，默认90度/秒
        """
        import math
        
        vel = vel if vel is not None else self.DEFAULT_ROB_VEL
        # print(f"输入的关节角度(度): {jpos}")
        
        # 将角度转换为弧度 - 使用math.radians更精确
        joint_pos = [math.radians(angle) for angle in jpos]
        # print(f"转换后的关节角度(弧度): {joint_pos}")
        
        # 执行关节运动
        # 注意参数顺序: joints, sp, move_mode
        # move_mode=0 表示绝对运动模式
        # print(f"开始执行关节运动, 速度: {vel}, 模式: 绝对运动(0)")
        ret = self.joint_move_origin(joint_pos, vel, 0)
        # print(f"关节运动结果: {ret}")
        return ret 