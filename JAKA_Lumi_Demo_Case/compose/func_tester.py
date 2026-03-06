import os
import time
import sys
import json
from utilfs.tools import radian_to_degree

# 添加脚本所在目录到系统路径，确保能正确找到配置文件
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utilfs.jaka_integrated import AGVIntegrated

# 从配置文件加载站点配置
def load_stations(config_path):
    """从配置文件加载站点配置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            
        if "stations" in user_config:
            print("成功从配置文件加载站点信息")
            return user_config["stations"]
        else:
            print("警告: 配置文件中没有站点信息，请先配置站点")
            return {}
    except Exception as e:
        print(f"加载站点配置失败: {e}")
        return {}
    
def load_ext_axis_limits(config_path):
    """从配置文件加载外部轴关节限制参数"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            
        if "extAxisLimits" in user_config:
            print("成功从配置文件加载外部轴关节限制参数")
            return user_config["extAxisLimits"]
        else:
            print("警告: 未找到外部轴限制配置，使用默认值")
            return {
                "joint1": {"min": 0, "max": 200, "desc": "升降，单位mm"}, 
                "joint2": {"min": -140, "max": 140, "desc": "腰部旋转，单位度"},
                "joint3": {"min": -180, "max": 180, "desc": "头部旋转，单位度"},
                "joint4": {"min": -5, "max": 35, "desc": "头部俯仰，单位度"}
            }

    except Exception as e:
        print(f"加载站点配置失败: {e}")
        return {}

def load_config(config_path):
    """加载系统配置"""
    try:
        # 使用绝对路径加载配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            
        # 从userCmdControl.json的systemConfig部分获取系统配置
        if "systemConfig" in user_config:
            return user_config["systemConfig"]
        else:
            print("警告: userCmdControl.json中没有systemConfig部分，使用默认配置")
            # return {
            #     "robot_ip": "192.168.10.90",
            #     "ext_base_url": "http://192.168.10.100",
            #     "agv_ip": "192.168.10.10",
            #     "agv_port": 31001
            # }
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        # return {
        #     "robot_ip": "192.168.10.90",
        #     "ext_base_url": "http://192.168.10.100",
        #     "agv_ip": "192.168.10.10",
        #     "agv_port": 31001
        # }

def callback(agv_data):
    """AGV数据接收回调函数"""
    # 直接使用已经解析好的字典数据
    try:
        # 检查agv_data是否为字典类型
        if isinstance(agv_data, dict):

            print(f"#"*20)
            print(f"收到AGV数据：")
            print(f"running_status: {agv_data.get('results').get('running_status')}")
            print(f"move_status: {agv_data.get('results').get('move_status')}")
            print(f"move_target: {agv_data.get('results').get('move_target')}")
            print(f"charge_state: {agv_data.get('results').get('charge_state')}")
            print(f"estop_state: {agv_data.get('results').get('estop_state')}")
            print(f"current_pose: {agv_data.get('results').get('current_pose')}")
            print(f"power_percent: {agv_data.get('results').get('power_percent')}")
            print(f"soft_estop_state: {agv_data.get('results').get('soft_estop_state')}")
            print(f"#"*20)

        else:
            print("AGV数据不是字典类型")
    except Exception as e:
        print(f"处理AGV数据时发生错误: {e}")
        
def main():
    """主函数"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf', 'userCmdControlMock.json')

    # 加载系统配置
    system_config = load_config(config_path)

    # 创建集成控制实例
    control = AGVIntegrated(
        system_config = system_config,
        debug=False
    )
    print("系统初始化完成")

    control.agv_request_data(callback)
    # 等待AGV数据接收线程启动
    time.sleep(5)
    # control.agv_set_point_as_marker('marker')
    control.agv_estop()
    time.sleep(5)
    control.agv_estop_release()
    time.sleep(5)
    control.agv_moveto('marker_lab1_outdoor')
    control.agv_moveto('marker')
    control.agv_moveto('charge_point_1F_6010')

    control.agv_stop_data()

if __name__ == "__main__":
    main()
