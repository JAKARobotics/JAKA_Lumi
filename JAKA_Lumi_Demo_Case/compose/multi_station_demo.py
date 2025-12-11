#!/usr/bin/env python3
# coding:UTF-8
'''多站点任务示例脚本
演示如何使用JAKAIntegrated类在多个站点之间移动并执行检测抓取任务
'''
from utilfs.jaka_integrated import AGVIntegrated
import os
import time
import sys
import json

# 添加脚本所在目录到系统路径，确保能正确找到配置文件
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
useMock = False
if not useMock:
    # 导入集成控制类
    from utilfs.jaka_integrated import JAKAIntegrated
else :
    # 导入模拟控制类
    from utilfs.jaka_integrated_mock import JAKAIntegratedMock
# 导入检测抓取模块
# import visualDetect_ali

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

def update_operation_mode(station_config, config_path):
    """更新操作模式到配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_cmd_config = json.load(f)
        
        # 更新操作模式
        user_cmd_config["operationMode"] = station_config["operation_mode"]
        
        with open(config_path, 'w') as f:
            json.dump(user_cmd_config, f, indent=4)
            
        print(f"已更新操作模式为: {station_config['operation_mode']}")
    except Exception as e:
        print(f"更新操作模式失败: {e}")

def execute_task_at_station(arm_control: JAKAIntegrated, agv_control: AGVIntegrated, station_id, station_config, config_path):
    """
    在指定站点执行任务
    :param control: JAKAIntegratedMock控制实例
    :param station_id: 站点ID
    :param station_config: 站点配置信息
    :param config_path: 配置文件路径
    """
    print(f"准备在 {station_config['name']} 执行任务...")
    # 0. 获取状态

    # 1. 移动到站点
    if not agv_control.agv_moveto(station_config['agv_marker']):
        print(f"移动到 {station_config['name']} 失败，跳过此站点任务")
        return False
    
    # 2. 设置机器人和外部轴到初始位
    if arm_control.ext_base_url:
        # 尝试移动外部轴，如果超出限制则会在方法内部打印错误
        ext_result = arm_control.ext_moveto(station_config['ext_home_pos'])
        if not ext_result:
            print(f"警告: 外部轴移动失败，但将继续执行任务")

    arm_control.rob_moveto(station_config['robot_home_pos'])
    
    # 检查操作模式，如果是"none"则跳过后续操作
    operation_mode = station_config.get('operation_mode')
    if operation_mode == 'none':
        print(f"站点 {station_config['name']} 的操作模式为'none'，仅执行移动操作，不执行检测和抓取")
        print(f"在 {station_config['name']} 的移动任务执行完成")
        return True
    elif operation_mode == 'capture':
        print(f"站点 {station_config['name']} 的操作模式为'capture'，执行拍照操作")
        # control.capture_image()
        return True
    elif  operation_mode == 'opendoor':
        print(f"站点 {station_config['name']} 的操作模式为'opendoor'，执行开门操作")
        # control.open_door(door_id=station_config['door_id'])
        return True
    elif operation_mode == 'close door':
        print(f"站点 {station_config['name']} 的操作模式为'close door'，执行关门操作")
        # control.close_door(door_id=station_config['door_id'])
        return True
    else:
        print(f"未知操作模式: {operation_mode}")
        return False
   

def main():
    """主函数"""
    print("=== 多站点任务系统 ===")
    _debug = True
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf', '213whole.json')

    # 加载系统配置
    config = load_config(config_path)
    
    # 加载站点配置
    stations = load_stations(config_path)

    ext_axis_limits = load_ext_axis_limits(config_path)

    if not stations:
        print("没有可用的站点配置，程序退出")
        return

    if not useMock:
        # 创建集成控制实例
        arm_control = JAKAIntegrated(
            system_config = config,
            ext_axis_limits = ext_axis_limits,
            debug=_debug
        )
        agv_control = AGVIntegrated(
            system_config = config,
            debug= False
        )
    else :
        # 创建模拟控制实例
        control = JAKAIntegratedMock(
            robot_ip=config["robot_ip"],
            ext_base_url=config.get("ext_base_url"),
            agv_ip=config.get("agv_ip"),
            agv_port=config.get("agv_port")
        )
    
    # 初始化系统
    if not arm_control.setup_system() :
        print("系统初始化失败，程序退出")
        return
    
    try:
        for i in range(2):
            # 按顺序执行各站点任务
            for station_id, station_config in stations.items():
                print(f"\n===== 开始 {station_config['name']} 任务 =====")
                execute_task_at_station(arm_control, agv_control, station_id, station_config, config_path)
                print(f"===== 完成 {station_config['name']} 任务 =====\n")
                # 任务间暂停
                time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"程序执行过程中发生错误: {e}")
    finally:
        # # 关闭系统
        arm_control.shutdown_system()
        print("程序已退出")

if __name__ == "__main__":
    time.sleep(3)
    main()