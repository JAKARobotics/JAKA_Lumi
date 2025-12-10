# coding:UTF-8
'''JAKA Integrated Control System
集成JAKA机器人、外部轴和AGV的控制功能
'''
from doctest import FAIL_FAST
import time
from tkinter import N
import requests
import json
import socket
import threading
import logging
import uuid

from utilfs.jaka import JAKA

class AGVIntegrated():
    def __init__(self, system_config = None, debug=False):
        # 配置logging
        self.logger = logging.getLogger(__name__)
        
        # 设置日志级别
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        
        # 确保只添加一次处理器
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            
            # 设置日志格式
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            
            # 添加处理器到logger
            self.logger.addHandler(console_handler)
        
        # AGV控制相关
        self.agv_ip = system_config.get("agv_ip")
        self.agv_port = system_config.get("agv_port")

        # 新增：AGV持续数据接收相关
        self.agv_data_thread = None
        self.agv_data_running = False
        self.agv_data_callback = None
        self.agv_data_topics = []

    #===========================    
    # AGV控制功能
    #===========================
    
    def _send_command_to_agv(self, command):
        """
        向AGV发送带有uuid的命令并接收响应
        :param command: 要发送的命令
        :return: JSON格式的响应数据,失败返回None
        """
        if not self.agv_ip or not self.agv_port:
            print("AGV连接信息未配置")
            return None
            
        try:
            # 创建TCP/IP套接字
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # 连接到服务器
                sock.connect((self.agv_ip, self.agv_port))
                _uuid = uuid.uuid4().hex
                if '?' in command:
                    to_send_command = f"{command}&uuid={_uuid}"
                else:
                    to_send_command = f"{command}?uuid={_uuid}"
                # 发送命令
                sock.sendall(to_send_command.encode('utf-8'))
                if not command.startswith('/api/robot_status'):
                    self.logger.info(to_send_command)
                else:
                    self.logger.debug(to_send_command)
                receiveResponse = False
                while not receiveResponse:
                    # 接收响应
                    response = sock.recv(4096).decode('utf-8')
                    # 解析JSON响应
                    response_json = json.loads(response)
                    self.logger.debug('发送控制指令后响应', response_json)
                    if response_json['type']=='response' and response_json['uuid']==_uuid:
                        receiveResponse = True
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
        '''
        成功时返回
        {
        "type": "response",
        "command": "/api/robot_status",
        "uuid": "",
        "status": "OK",
        "error_message": "",
        "results": 
            {
            "move_target": "target_name", // 移动指令指定的目标点位名称
            "move_status": "running", // 移动指令的执行状态。详细解释⻅后边
            "running_status": "running", // v0.7.12新增，移动任务的具体状态， 详细⻅后面解释
            "move_retry_times": 3, //此次数每增加1，表示机器人进行了新一轮的路径重试；路径规划一
            "charge_state": bool, //true->充电中状态。false->未充电状态。
            "soft_estop_state": bool, // 通过API接口设置的软急停状态, true->急停中，false->非
            "hard_estop_state": bool, // 通过硬件急停按钮设置的硬急停状态, true->急停中，fals
            "estop_state": bool, // hard_estop_state || sofpt_estop_state, true->急停中
            "power_percent": 100, //电量百分比，单位：%
            "current_pose": 
                {
                    "x": 11.0, // 单位：m
                    "y": 11.0, // 单位：m
                    "theta": 0.5, //单位：rad
                }
            "current_floor": 16,
            "chargepile_id": "1234", // v0.9.6新增。充电状态下表示当前正在充电的充电桩ID，非充
            "error_code": "00000000" // v0.7.7新增，16进制错误码，总共8个字节表示，非0表示机
            }
        }
        '''
        return response
    
    # TODO: 待测试
    def agv_get_specified_status(self,query):
        response = self.agv_get_status()
        if response and response['status']=='OK':
            return response['results'][query]
        else:
            return None

    def agv_moveto(self, point_name):
        """
        控制AGV移动到指定标记点
        :param point_name: 目标点位的标记号
        :return: 成功返回True，失败返回False
        """
        # 发送移动命令
        task_completed = False
        while not task_completed:
            response = self._send_command_to_agv(f"/api/move?marker={point_name}")
            self.logger.debug(json.dumps(response, indent=4))
            if not response:
                self.logger.error("发送AGV移动命令失败")
                return False
            status = response.get('status', None)
            if status=='OK':
                task_completed = True
            elif status=='BUSY_NOW':
                self.logger.error("AGV当前正在执行其他任务，无法移动")
                self.agv_cancel_task()
        self.logger.info(f"AGV开始移动到标记点 {point_name}")
        # 等待移动完成
        is_done = False
        while not is_done:
            time.sleep(0.5)
            try:
                response = self._send_command_to_agv("/api/robot_status")
                '''
                TODO: 文档中move_target表示移动指令指定的点位名称。
                当以”location”调用移动接口时, 此字段值为空
                当调用巡游接口时，此字段为当前正在前往的点位名称
                '''
                if response and response['results']['move_status'] == "succeeded":
                    is_done = True
                    print(f"AGV已到达标记点 {point_name}")
            except Exception as e:
                # TODO: 输出其他状态的idle/suceeded/failed/canceld对应响应
                self.logger.error(f"检查AGV状态时发生错误: {e},返回内容{response}")
                return False
                
        return True

    def agv_set_point_as_marker(self,point_name,type=0,num=1):
        '''
        在机器人的当前位置和楼层标记锚点
        :param point_name: 目标点位的标记号
        :return: 成功返回True,失败返回False
        '''
        try:
            response = self._send_command_to_agv(f"/api/markers/insert?name={point_name}&type={type}&num={num}")
            if not response:
                self.logger.error("发送设置marker指令失败")
                return False
            self.logger.debug(json.dumps(response, indent=4))
            '''
            成功设置时返回
                {
                "type": "response",
                "command": "/api/markers/insert",
                "uuid": "",
                "status": "OK",
                "error_message": ""
                }
            '''
            if response and response['status']=='OK':
                print(f"AGV已成功设置marker点 {point_name}")
                return True
            else:
                print(f"AGV设置marker点 {point_name}失败")
                return False

        except Exception as e:
            print(f"AGV设置marker点时发生错误: {e}")
            return False

    def agv_cancel_task(self):
        '''
        判断当前是否有移动任务，若有取消当前的移动任务
        '''
        '''
        {
        "type": "response",
        "command": "/api/move/cancel",
        "uuid": "",
        "status": "OK",
        "error_message": ""
        }
        '''

        '''
        move_status表示当前机器人去move_target的执行状态。
        其取值及解释如下。
        字段值 解释
        idle 表示机器人服务启动后尚未收到任何移动指令。
        running 表示机器人正在去往move_target,此时会拒绝接受新的移动指令。
        succeeded 表示移动任务已经成功完成。
        failed 表示移动任务失败了。
        canceled 表示移动任务被取消了。
        '''
        try:
            # 首先判断是否位于移动状态
            status_response = self.agv_get_status()
        except Exception as e:
            print(f"AGV获取状态时发生错误: {e}")
            return False


        # 若有移动任务，发生取消指令
        if status_response['results']['move_status'] == 'running':
            print("当前AGV正在移动中")
            # 发送取消移动指令
            try:
                response = self._send_command_to_agv("/api/move/cancel")
                self.logger.debug("任务取消：\n",json.dumps(response, indent=4))
                if response and response['status']=='OK':
                    print("已成功取消当前移动任务")
                    return True
                else:
                    print("取消移动任务失败")
                    return False
            except Exception as e:
                print(f"AGV获取状态时发生错误: {e}")
                return False
        else:
            print("当前AGV未在移动中")
            return True

    def agv_estop(self):
        '''
        /api/estop?flag=true //进入急停模式
        /api/estop?flag=false //退出急停模式
        '''

        # TODO：增加当前状态判断
        try:
            response = self._send_command_to_agv("/api/estop?flag=true")
            if response and response['status']=='OK':
                print("已成功急停")
                return True
            else:
                print("急停失败")
                return False
        except Exception as e:
            print(f"AGV急停时发生错误: {e}")
            return False

    def agv_estop_release(self):
        '''
        /api/estop?flag=true //进入急停模式
        /api/estop?flag=false //退出急停模式
        '''
        # TODO：增加当前状态判断
        # TODO：执行前，端侧或后台需提示推行至充电桩，并重新定位
        try:
            response = self._send_command_to_agv("/api/estop?flag=false")
            if response and response['status']=='OK':
                print("已成功取消急停")
                return True
            else:
                print("取消急停失败")
                return False
        except Exception as e:
            print(f"AGV取消急停时发生错误: {e}")
            return False

    # TODO: 待测试
    def agv_position_adjust(self,current_point_name='充电桩名'):
        '''
        '''
        # TODO：增加当前状态判断
        # TODO：执行前，端侧或后台需提示推行至充电桩，并重新定位
        try:
            response = self._send_command_to_agv(f"/api/position_adjust?marker={current_point_name}")
            if response and response['status']=='OK':
                print("已成功重定位机器人位置")
                return True
            else:
                print("重定位机器人位置失败")
                return False
        except Exception as e:
            print(f"AGV重定位时发生错误: {e}")
            return False

    def agv_request_data(self, callback):
        """
        请求AGV服务器以一定频率发送指定topic类型的数据
        :param callback: 数据接收回调函数，接收一个参数：data（JSON格式的AGV数据）
        :return: 成功返回True，失败返回False
        """
        if not self.agv_ip or not self.agv_port:
            print("AGV连接信息未配置")
            return False
        
        if not callback or not callable(callback):
            print("无效的callback参数，必须是可调用函数")
            return False
        
        # 如果已经在接收数据，先停止
        if self.agv_data_running:
            print("AGV数据接收已经在运行，先停止")
            self.agv_stop_data()
        
        self.agv_data_callback = callback
        self.agv_data_running = True
        
        # 创建并启动接收数据的线程
        self.agv_data_thread = threading.Thread(target=self._receive_agv_data, daemon=True)
        self.agv_data_thread.start()
        
        return True
   
    # TODO: 未测试
    def _receive_agv_data(self):
        """
        持续接收AGV数据的线程函数
        """
        # response = self._send_command_to_agv("/api/request_data?topic=robot_status&frequency=1")
        # print(response.get('status'))
        try:
            # 创建新的socket连接用于持续接收数据
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.agv_ip, self.agv_port))
                # 设置socket超时，以便定期检查是否需要停止
                sock.settimeout(2)
                _uuid = uuid.uuid4().hex
                to_send_command = f'/api/request_data?topic=robot_status&frequency=1&uuid={_uuid}'
                # 发送命令
                sock.sendall(to_send_command.encode('utf-8'))
                self.logger.info(to_send_command)
                receiveResponse = False
                while not receiveResponse:
                    # 接收响应
                    response = sock.recv(4096).decode('utf-8')
                    # 解析JSON响应
                    response_json = json.loads(response)
                    self.logger.debug('发送控制指令后响应', response_json)
                    if response_json['type']=='response' and response_json['uuid']==_uuid:
                        receiveResponse = True

                print("开始接收AGV数据")
                while self.agv_data_running:
                    try:
                        # 接收数据
                        response = sock.recv(4096).decode('utf-8')
                        if not response:
                            print("AGV数据为空，跳过")
                            continue
                        # 解析JSON响应
                        response_json = json.loads(response)
                        if response_json.get('type') != 'callback': 
                            continue
                        # 调用回调函数处理数据
                        if self.agv_data_callback and callable(self.agv_data_callback):
                            self.agv_data_callback(response_json)
                    except socket.timeout:
                        # 超时只是为了检查是否需要停止，不是错误
                        self.logger.debug("AGV数据接收超时，继续等待")
                        continue
                    except json.JSONDecodeError as e:
                        self.logger.error(f"解析AGV数据时发生JSON错误: {e}\n 返回json内容：{response_json}")
                    except Exception as e:
                        self.logger.error(f"接收AGV数据时发生错误: {e}")
                        break
                
            print("停止接收AGV数据")
        except Exception as e:
            print(f"AGV数据接收线程发生错误: {e}")

    def agv_stop_data(self):
        """
        停止接收AGV数据
        :return: 成功返回True，失败返回False
        """
        if not self.agv_data_running:
            print("AGV数据接收未在运行")
            return True
        
        # 设置标志位停止线程
        self.agv_data_running = False
        
        # 等待线程结束
        if self.agv_data_thread and self.agv_data_thread.is_alive():
            self.agv_data_thread.join(timeout=3)
        
        if self.agv_data_thread and self.agv_data_thread.is_alive():
            print("警告：AGV数据接收线程未能正常结束")
            return False
        
        # 重置状态
        self.agv_data_thread = None
        self.agv_data_topics = []
        self.agv_data_callback = None
        

class JAKAIntegrated(JAKA):
    # 默认设置
    DEFAULT_EXT_VEL = 100
    DEFAULT_EXT_ACC = 100
    DEFAULT_ROB_VEL = 90

    def __init__(self, system_config = None, ext_axis_limits = None, debug=False):
        """
        初始化集成控制系统
        :param robot_ip: JAKA机器人IP地址
        :param ext_base_url: 外部轴控制基础URL
        :param agv_ip: AGV IP地址
        :param agv_port: AGV端口
        :param debug: 是否启用调试模式
        """
        # 配置logging
        self.logger = logging.getLogger(__name__)
        
        # 设置日志级别
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        
        # 确保只添加一次处理器
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            
            # 设置日志格式
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            
            # 添加处理器到logger
            self.logger.addHandler(console_handler)
        
        # 调用父类初始化，但不立即连接
        super().__init__(system_config["robot_ip"], connect=False)
        self.system_config = system_config
        self.debug = debug
        # 外部轴控制相关
        self.ext_base_url = system_config.get("ext_base_url")
        if self.ext_base_url:
            self.EXT_MOVETO_URL = f"{self.ext_base_url}/moveto"
            self.EXT_SYSINFO_URL = f"{self.ext_base_url}/sysinfo"
            self.EXT_RESET_URL = f"{self.ext_base_url}/reset"
            self.EXT_ENABLE_URL = f"{self.ext_base_url}/enable"
            self.EXT_GETSTATE_URL = f"{self.ext_base_url}/status"
        
        # 加载外部轴关节限制
        self.ext_axis_limits = ext_axis_limits
        
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
                self.logger.info("外部轴连接正常")
                return True
            else:
                self.logger.error(f"外部轴连接错误: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"外部轴连接异常: {e}")
            return False
    
    def ext_reset(self):
        """重置所有外部轴关节"""
        if not self.ext_base_url:
            print("外部轴URL未配置")
            return False
            
        response = requests.post(self.EXT_RESET_URL, json={})
        if response.status_code == 200:
            self.logger.info("外部轴重置成功")
            return True
        else:
            self.logger.error(f"外部轴重置失败: {response.status_code}")
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
            self.logger.info("外部轴" + ("使能成功" if enable else "禁用成功"))
            return True
        else:
            self.logger.error(f"外部轴" + ("使能失败" if enable else "禁用失败") + f": {response.status_code}")
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
            self.logger.error(f"获取外部轴状态失败: {response.status_code}")
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
            self.logger.info('外部轴移动成功!')
            return True
        else:
            self.logger.error(f"外部轴移动失败: {response.status_code}")
            return False

    #===========================
    # 集成控制功能
    #===========================
    
    def setup_system(self):
        """
        初始化整个系统
        :return: 成功返回True，失败返回False
        """

        # 检查外部轴连接
        ext_ok = True
        if self.ext_base_url:
            ext_ok = self.ext_check_connection()
            if ext_ok:
                self.ext_reset()
                self.ext_enable(True)
        
        # 连接机器人
        robot_ok = self.jaka_connect()
        
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
        
        self.logger.info("系统已关闭")

    # 扩展JAKA类的方法，使其更适用于集成控制系统
    
    def rob_moveto(self, jpos, vel=None):
        """
        控制机器人移动到指定关节角度(度数)
        :param jpos: 目标关节角度 [J1, J2, J3, J4, J5, J6]，单位为度
        :param vel: 关节速度，默认90度/秒
        """
        import math
        
        vel = vel if vel is not None else self.DEFAULT_ROB_VEL
        self.logger.info(f"输入的关节角度(度): {jpos}")
        
        # 将角度转换为弧度 - 使用math.radians更精确
        joint_pos = [math.radians(angle) for angle in jpos]
        self.logger.debug(f"转换后的关节角度(弧度): {joint_pos}")
        
        # 执行关节运动
        # 注意参数顺序: joints, sp, move_mode
        # move_mode=0 表示绝对运动模式
        self.logger.info(f"开始执行关节运动, 速度: {vel}, 模式: 绝对运动(0)")
        ret = self.joint_move_origin(joint_pos, vel, 0)
        self.logger.info(f"关节运动结果: {ret}")
        return ret 