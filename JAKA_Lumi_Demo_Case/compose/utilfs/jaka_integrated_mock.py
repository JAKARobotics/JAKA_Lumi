# coding:UTF-8
'''JAKA Integrated Control System (Mock Version)
模拟集成JAKA机器人、外部轴和AGV的控制功能，用于无硬件环境下的测试
'''
import os
import time
import json
import random
from datetime import datetime

# 移除对实际JAKA SDK的依赖，创建模拟的JAKA基类
class JAKA:
    def __init__(self, robot_ip, connect=True):
        self.robot_ip = robot_ip
        self.robot = None  # 模拟机器人连接对象
        print(f"[MOCK] JAKA基类初始化，IP: {robot_ip}")
        if connect:
            self.jaka_connect()
    
    def jaka_connect(self):
        """模拟连接机器人"""
        print(f"[MOCK] 正在连接机器人 {self.robot_ip}...")
        time.sleep(0.5)  # 模拟连接延迟
        self.robot = True  # 模拟连接成功
        print(f"[MOCK] 机器人连接成功")
        return True
    
    def robot_disconnect(self):
        """模拟断开机器人连接"""
        if self.robot:
            print(f"[MOCK] 断开机器人连接")
            self.robot = None
            return True
        return False
    
    def joint_move_origin(self, joints, sp, move_mode):
        """模拟关节运动"""
        print(f"[MOCK] 执行关节运动 - 关节角度: {joints}, 速度: {sp}, 模式: {move_mode}")
        time.sleep(1.0)  # 模拟运动延迟
        return 0  # 模拟成功返回0
    
    # 模拟其他可能被调用的方法
    def set_user_coordinate(self, coordinate_id, coordinate):
        print(f"[MOCK] 设置用户坐标系 - ID: {coordinate_id}, 坐标: {coordinate}")
        return True
    
    def get_user_coordinate(self, coordinate_id):
        print(f"[MOCK] 获取用户坐标系 - ID: {coordinate_id}")
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 返回默认坐标
    
    def set_digital_output(self, port, value):
        print(f"[MOCK] 设置数字输出 - 端口: {port}, 值: {value}")
        return True
    
    def get_digital_input(self, port):
        print(f"[MOCK] 获取数字输入 - 端口: {port}")
        return 0  # 返回默认值
    
    def liner_move(self, pose, speed, mode):
        print(f"[MOCK] 执行线性运动 - 位姿: {pose}, 速度: {speed}, 模式: {mode}")
        time.sleep(1.0)
        return 0

class JAKAIntegratedMock(JAKA):
    # 默认设置
    DEFAULT_EXT_VEL = 100
    DEFAULT_EXT_ACC = 100
    DEFAULT_ROB_VEL = 90
    
    def __init__(self, robot_ip, ext_base_url=None, agv_ip=None, agv_port=None):
        """
        初始化模拟集成控制系统
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
        
        # 模拟状态
        self.ext_enabled = False
        self.current_ext_position = [0, 0, 0, 0]
        self.current_robot_position = [0, 0, 0, 0, 0, 0]
        self.agv_status = "idle"
        
        # 相机模拟状态
        self.cameras = {
            "cam1": {
                "name": "主相机",
                "position": "机器人末端",
                "resolution": "1920x1080",
                "status": "online",
                "last_image_path": None
            },
            "cam2": {
                "name": "辅助相机",
                "position": "机器人本体",
                "resolution": "1280x720",
                "status": "online",
                "last_image_path": None
            }
        }
        
        # 加载外部轴关节限制
        self.ext_axis_limits = self._load_ext_axis_limits()
        
        print(f"[MOCK] JAKAIntegratedMock初始化完成 - 机器人IP: {robot_ip}, 外部轴URL: {ext_base_url}, AGV: {agv_ip}:{agv_port}")
    
    def _load_ext_axis_limits(self):
        """模拟加载外部轴关节限制参数"""
        try:
            # 尝试从配置文件加载，如果失败则使用默认值
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conf', 'userCmdControl.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                if "extAxisLimits" in config:
                    print(f"[MOCK] 从配置文件加载外部轴限制: {config_path}")
                    return config["extAxisLimits"]
        except Exception as e:
            print(f"[MOCK] 加载外部轴限制配置失败: {e}，使用默认值")
        
        # 默认限制值
        print(f"[MOCK] 使用默认外部轴限制值")
        return {
            "joint1": {"min": 0, "max": 200, "desc": "升降，单位mm"}, 
            "joint2": {"min": -140, "max": 140, "desc": "腰部旋转，单位度"},
            "joint3": {"min": -180, "max": 180, "desc": "头部旋转，单位度"},
            "joint4": {"min": -5, "max": 35, "desc": "头部俯仰，单位度"}
        }
    
    def _adjust_to_joint_limits(self, point):
        """
        模拟调整关节位置以确保在限制范围内
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
    # 外部轴控制功能（模拟）
    #===========================
    
    def ext_check_connection(self):
        """模拟检查外部轴连接状态"""
        if not self.ext_base_url:
            print("[MOCK] 外部轴URL未配置")
            return False
        
        print(f"[MOCK] 检查外部轴连接: {self.ext_base_url}")
        # 模拟随机连接成功或失败（90%成功率）
        success = random.random() < 0.9
        print(f"[MOCK] 外部轴连接{'正常' if success else '失败'}")
        return success
    
    def ext_reset(self):
        """模拟重置所有外部轴关节"""
        if not self.ext_base_url:
            print("[MOCK] 外部轴URL未配置")
            return False
            
        print("[MOCK] 执行外部轴重置...")
        time.sleep(0.5)
        # 重置到零位
        self.current_ext_position = [0, 0, 0, 0]
        print("[MOCK] 外部轴重置成功")
        return True
    
    def ext_enable(self, enable=True):
        """
        模拟使能或禁用外部轴
        :param enable: True表示使能，False表示禁用
        """
        if not self.ext_base_url:
            print("[MOCK] 外部轴URL未配置")
            return False
            
        print(f"[MOCK] 执行外部轴{'使能' if enable else '禁用'}...")
        time.sleep(0.3)
        self.ext_enabled = enable
        print(f"[MOCK] 外部轴{'使能成功' if enable else '禁用成功'}")
        return True
    
    def ext_get_state(self):
        """
        模拟获取外部轴状态
        :return: 成功返回模拟的状态信息，失败返回None
        """
        if not self.ext_base_url:
            print("[MOCK] 外部轴URL未配置")
            return None
            
        print("[MOCK] 获取外部轴状态")
        # 返回模拟的状态数据
        state = {
            "enabled": self.ext_enabled,
            "position": self.current_ext_position,
            "temperature": random.uniform(30, 40),
            "voltage": random.uniform(23, 25),
            "status": "normal" if self.ext_enabled else "disabled"
        }
        print(f"[MOCK] 外部轴状态: {state}")
        return state
    
    def ext_moveto(self, point, vel=None, acc=None):
        """
        模拟控制外部轴移动到指定位置
        :param point: 目标位置坐标 [x, y, z, r]
        :param vel: 速度，默认100
        :param acc: 加速度，默认100
        :return: 成功返回True，失败返回False
        """
        if not self.ext_base_url:
            print("[MOCK] 外部轴URL未配置")
            return False
            
        if not self.ext_enabled:
            print("[MOCK] 外部轴未使能，无法移动")
            return False
            
        # 检查关节限制并调整到限制范围内
        adjusted_point, was_adjusted, adjustment_msg = self._adjust_to_joint_limits(point)
        if was_adjusted:
            print(f"[MOCK] 警告: {adjustment_msg}")
            print(f"[MOCK] 原始位置: {point} -> 调整后位置: {adjusted_point}")
            point = adjusted_point
            
        vel = vel if vel is not None else self.DEFAULT_EXT_VEL
        acc = acc if acc is not None else self.DEFAULT_EXT_ACC
        
        print(f"[MOCK] 执行外部轴移动 - 目标位置: {point}, 速度: {vel}, 加速度: {acc}")
        # 模拟移动时间
        move_time = 0.5 + (random.random() * 1.0)
        time.sleep(move_time)
        # 更新当前位置
        self.current_ext_position = list(point)
        print(f"[MOCK] 外部轴移动成功! 当前位置: {self.current_ext_position}")
        return True

    #===========================
    # AGV控制功能（模拟）
    #===========================
    
    def _send_command_to_agv(self, command):
        """
        模拟向AGV发送命令并接收响应
        :param command: 要发送的命令
        :return: JSON格式的模拟响应数据，失败返回None
        """
        if not self.agv_ip or not self.agv_port:
            print("[MOCK] AGV连接信息未配置")
            return None
            
        print(f"[MOCK] 向AGV发送命令: {command}")
        time.sleep(0.2)  # 模拟通信延迟
        
        # 模拟不同命令的响应
        if command.startswith("/api/robot_status"):
            # 返回模拟的状态信息
            return {
                "code": 0,
                "results": {
                    "robot_id": "mock_agv_001",
                    "battery": random.uniform(80, 100),
                    "move_status": self.agv_status,
                    "current_marker": "mark_001",
                    "pose": [random.uniform(0, 10), random.uniform(0, 10), random.uniform(0, 360)]
                }
            }
        elif command.startswith("/api/move"):
            # 解析目标标记点
            marker = command.split("marker=")[-1]
            return {
                "code": 0,
                "results": {
                    "status": "start_moving",
                    "target_marker": marker,
                    "estimated_time": random.uniform(5, 20)
                }
            }
        else:
            # 未知命令
            return {
                "code": 1,
                "message": "Unknown command"
            }
    
    def agv_get_status(self):
        """
        模拟获取AGV状态
        :return: AGV状态信息，失败返回None
        """
        response = self._send_command_to_agv("/api/robot_status")
        return response
    
    def agv_moveto(self, point_name):
        """
        模拟控制AGV移动到指定标记点
        :param point_name: 目标点位的标记号
        :return: 成功返回True，失败返回False
        """
        # 发送移动命令
        response = self._send_command_to_agv(f"/api/move?marker={point_name}")
        if not response or response.get("code") != 0:
            print(f"[MOCK] 发送AGV移动命令失败: {response}")
            return False
            
        print(f"[MOCK] AGV开始移动到标记点 {point_name}")
        print(f"[MOCK] {json.dumps(response, indent=4)}")

        # 更新AGV状态
        self.agv_status = "moving"
        
        # 模拟移动过程
        move_time = random.uniform(2, 5)  # 模拟2-5秒的移动时间
        start_time = time.time()
        
        while time.time() - start_time < move_time:
            time.sleep(0.5)

        
        # 更新AGV状态为到达
        self.agv_status = "succeeded"
        print(f"[MOCK] AGV已到达标记点 {point_name}")
        return True

    #===========================
    # 相机控制功能（模拟）
    #===========================
    def get_camera_info(self, camera_id=None):
        """
        模拟获取相机信息
        :param camera_id: 相机ID，如'cam1'或'cam2'，None表示获取所有相机信息
        :return: 相机信息字典
        """
        print(f"[MOCK] 获取相机信息 - ID: {camera_id}")
        
        if camera_id is None:
            # 返回所有相机信息
            print(f"[MOCK] 返回所有相机信息: {self.cameras}")
            return self.cameras
        elif camera_id in self.cameras:
            # 返回特定相机信息
            camera_info = self.cameras[camera_id]
            print(f"[MOCK] 返回相机 {camera_id} 信息: {camera_info}")
            return camera_info
        else:
            # 相机不存在
            print(f"[MOCK] 相机 {camera_id} 不存在")
            return None
    
    def capture_image(self, camera_id='cam1', save_path=None):
        """
        模拟使用指定相机拍摄图像
        :param camera_id: 相机ID，默认为'cam1'
        :param save_path: 图像保存路径，None则使用默认路径
        :return: 成功返回图像路径，失败返回None
        """
        print(f"[MOCK] 使用相机 {camera_id} 拍摄图像")
        
        if camera_id not in self.cameras:
            print(f"[MOCK] 相机 {camera_id} 不存在")
            return None
        
        if self.cameras[camera_id]['status'] != 'online':
            print(f"[MOCK] 相机 {camera_id} 离线，无法拍摄")
            return None
        
        # 生成模拟的图像保存路径
        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # 确保图像目录存在
            img_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images')
            if not os.path.exists(img_dir):
                print(f"[MOCK] 创建图像目录: {img_dir}")
                os.makedirs(img_dir)
            save_path = os.path.join(img_dir, f"{camera_id}_{timestamp}.jpg")
        
        # 模拟拍摄延迟
        print(f"[MOCK] 正在拍摄...")
        time.sleep(0.5)
        
        # 更新相机状态
        self.cameras[camera_id]['last_image_path'] = save_path
        
        print(f"[MOCK] 拍摄成功，图像已保存到: {save_path}")
        return save_path
    
    def set_camera_parameter(self, camera_id, param_name, param_value):
        """
        模拟设置相机参数
        :param camera_id: 相机ID
        :param param_name: 参数名称
        :param param_value: 参数值
        :return: 成功返回True，失败返回False
        """
        print(f"[MOCK] 设置相机 {camera_id} 参数 - {param_name}: {param_value}")
        
        if camera_id not in self.cameras:
            print(f"[MOCK] 相机 {camera_id} 不存在")
            return False
        
        if self.cameras[camera_id]['status'] != 'online':
            print(f"[MOCK] 相机 {camera_id} 离线，无法设置参数")
            return False
        
        # 模拟设置参数
        # 在实际应用中，这里可能需要验证参数的有效性
        print(f"[MOCK] 参数设置成功")
        return True
   
   
    #===========================
    # 门禁控制（模拟）
    #===========================
    def open_door(self,door_id='door1'):
        """
        模拟开门操作
        """
        print("[MOCK] 模拟开门操作")
        self.door_status = f"{door_id}_open"
        return True
    
    def close_door(self,door_id='door1'):
        """
        模拟关门操作
        """
        print("[MOCK] 模拟关门操作")
        self.door_status = f"{door_id}_closed"
        return True
    #===========================
    # 集成控制功能（模拟）
    #===========================
    
    def setup_system(self):
        """
        模拟初始化整个系统
        :return: 成功返回True，失败返回False
        """
        print("[MOCK] 开始初始化系统...")
        
        # 连接机器人
        print("[MOCK] 初始化机器人连接...")
        self.jaka_connect()
        robot_ok = True
        
        # 检查外部轴连接
        ext_ok = True
        if self.ext_base_url:
            print("[MOCK] 初始化外部轴...")
            ext_ok = self.ext_check_connection()
            if ext_ok:
                self.ext_reset()
                self.ext_enable(True)
        
        # 初始化AGV状态
        if self.agv_ip and self.agv_port:
            print("[MOCK] 初始化AGV状态...")
            self.agv_status = "idle"
        
        print(f"[MOCK] 系统初始化完成 - 机器人状态: {'正常' if robot_ok else '异常'}, 外部轴状态: {'正常' if ext_ok else '异常'}")
       
       # 初始化相机状态
        print("[MOCK] 初始化相机状态...")
        for camera_id in self.cameras:
            self.set_camera_parameter(camera_id, 'status', 'online')
        camera_ok = True    
        return robot_ok and ext_ok and camera_ok
    
    def shutdown_system(self):
        """
        模拟关闭整个系统
        """
        print("[MOCK] 开始关闭系统...")
        
        # 断开机器人连接
        if self.robot:
            self.robot_disconnect()
        
        # 禁用外部轴
        if self.ext_base_url and self.ext_enabled:
            self.ext_enable(False)
        
        # 更新AGV状态
        if self.agv_ip and self.agv_port:
            self.agv_status = "offline"
        
        print("[MOCK] 系统已关闭")

    def move_to_station(self, station_name, agv_marker):
        """
        模拟移动到指定工作站
        :param station_name: 工作站名称(用于日志)
        :param agv_marker: AGV目标点位标记
        :return: 成功返回True，失败返回False
        """
        print(f"[MOCK] 开始移动到工作站: {station_name}")
        
        if self.agv_ip and self.agv_port:
            agv_result = self.agv_moveto(agv_marker)
            if not agv_result:
                print(f"[MOCK] AGV移动到工作站 {station_name} 失败")
                return False
        else:
            # 如果没有AGV配置，模拟直接到达
            print(f"[MOCK] 无AGV配置，直接模拟到达工作站 {station_name}")
            time.sleep(1.0)
        
        print(f"[MOCK] 已到达工作站: {station_name}")
        return True 
    
    # 扩展JAKA类的方法，使其更适用于集成控制系统
    
    def rob_moveto(self, jpos, vel=None):
        """
        模拟控制机器人移动到指定关节角度(度数)
        :param jpos: 目标关节角度 [J1, J2, J3, J4, J5, J6]，单位为度
        :param vel: 关节速度，默认90度/秒
        """
        import math
        
        vel = vel if vel is not None else self.DEFAULT_ROB_VEL
        print(f"[MOCK] 输入的关节角度(度): {jpos}")
        
        # 将角度转换为弧度 - 使用math.radians更精确
        joint_pos = [math.radians(angle) for angle in jpos]
        print(f"[MOCK] 转换后的关节角度(弧度): {joint_pos}")
        
        # 执行模拟关节运动
        print(f"[MOCK] 开始执行关节运动, 速度: {vel}, 模式: 绝对运动(0)")
        # 模拟运动时间
        move_time = 1.0 + (random.random() * 1.0)
        time.sleep(move_time)
        # 更新当前位置
        self.current_robot_position = list(jpos)
        print(f"[MOCK] 关节运动完成，当前关节角度(度): {self.current_robot_position}")
        return 0
     
    def grab_action(self, value):
        """
        模拟抓取动作（添加此方法以支持之前的功能调用）
        :param value: 0表示释放，1表示抓取
        :return: 成功返回True
        """
        action = "释放" if value == 0 else "抓取"
        print(f"[MOCK] 执行 {action} 动作")
        time.sleep(0.5)  # 模拟动作延迟
        print(f"[MOCK] {action} 动作完成")
        return True

# 添加一个便捷函数，用于创建模拟实例
def create_mock_controller(robot_ip="192.168.10.90", 
                          ext_base_url="http://192.168.10.100",
                          agv_ip="192.168.10.10", 
                          agv_port=31001):
    """
    创建模拟控制器实例
    :param robot_ip: 模拟的机器人IP
    :param ext_base_url: 模拟的外部轴URL
    :param agv_ip: 模拟的AGV IP
    :param agv_port: 模拟的AGV端口
    :return: JAKAIntegratedMock实例
    """
    print(f"[MOCK] 创建模拟控制器实例 - 时间戳: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    controller = JAKAIntegratedMock(robot_ip, ext_base_url, agv_ip, agv_port)
    return controller

# 如果直接运行此文件，则执行简单的测试
if __name__ == "__main__":
    print("===== JAKA集成控制系统模拟测试 =====")
    
    # 创建模拟控制器
    controller = create_mock_controller()
    
    # 测试系统初始化
    print("\n----- 测试系统初始化 -----")
    controller.setup_system()
    
    # 测试外部轴功能
    print("\n----- 测试外部轴移动 -----")
    controller.ext_moveto([100, 30, 45, 10])
    
    # 测试AGV移动
    print("\n----- 测试AGV移动 -----")
    controller.agv_moveto("station_01")
    
    # 测试机器人移动
    print("\n----- 测试机器人移动 -----")
    controller.rob_moveto([0, -30, 0, -60, 0, 0])
    
    # 测试相机功能
    print("\n----- 测试相机功能 -----")
    # 获取相机信息
    all_cameras = controller.get_camera_info()
    cam1_info = controller.get_camera_info('cam1')
    
    # 模拟拍照
    img_path = controller.capture_image()
    print(f"[MOCK] 拍摄的图像路径: {img_path}")
    
    # 使用辅助相机拍照
    img_path2 = controller.capture_image('cam2')
    print(f"[MOCK] 辅助相机拍摄的图像路径: {img_path2}")
    
    # 设置相机参数
    controller.set_camera_parameter('cam1', 'exposure', 100)
    controller.set_camera_parameter('cam1', 'gain', 50)
    
    # 测试工作站移动
    print("\n----- 测试工作站移动 -----")
    controller.move_to_station("测试工作站", "mark_test")
    
    # 测试系统关闭
    print("\n----- 测试系统关闭 -----")
    controller.shutdown_system()
    
    print("\n===== 模拟测试完成 =====")