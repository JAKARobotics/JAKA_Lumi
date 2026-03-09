from utilfs.jaka_integrated import JAKAIntegrated
from utilfs.python_open_gripper import ensure_initialized, move_gripper,command_gripper
from utilfs.lumi_url import LUMI_ENABLE_URL, LUMI_MOVETO_URL, LUMI_GETSTATE_URL
from utilfs.lumi_url import LUMI_RESET_URL, LUMI_STATUS_URL,LUMI_SYSINFO_URL

import time
import serial
import json, requests

# export LD_LIBRARY_PATH="/home/cih/Desktop/repos/JAKA_Lumi/04. JAKA Lumi Demo Case [示例]/LUMI_DEMO-v2/JAKA_SDK_LINUX:$LD_LIBRARY_PATH"

def load_config():
    """加载系统配置"""
    default_cfg = {
        "robot_ip": "192.168.10.90",
        "ext_base_url": "http://192.168.10.90:5000/api/extaxis",
        "agv_ip": "192.168.10.10",
        "agv_port": 31001,
    }
    try:
        with open('./conf/userCmdControl.json', 'r') as f:
            user_config = json.load(f)
            
        # 从userCmdControl.json的systemConfig部分获取系统配置
        if "systemConfig" in user_config:
            return user_config["systemConfig"]
        else:
            print("警告: userCmdControl.json中没有systemConfig部分，使用默认配置")
            return default_cfg
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return default_cfg

config = load_config()

control = JAKAIntegrated(
        robot_ip=config["robot_ip"],
        ext_base_url=config.get("ext_base_url"),
        agv_ip=config.get("agv_ip"),
        agv_port=config.get("agv_port")
    )

control.jaka_connect()

response = requests.get(LUMI_SYSINFO_URL)
print(f"LUMI_SYSINFO_URL:{response.text}")

# 复位所有轴错误
response = requests.post(LUMI_RESET_URL, json={})
print(f"LUMI_RESET_URL:{response.text}")


# 开启升降柱、头部电机使能
response = requests.post(LUMI_ENABLE_URL, json={"enable": 1})
print(f"LUMI_ENABLE_URL ON:{response.text}")

# control.rob_moveto([0,0,0,0,0,0])

# control.robot.grab_action(1)

# control.rob_moveto([130,-60,0,35,-40,0],135)

# control.rob_moveto([130,-60,10,35,-12,0],135)

# control.rob_moveto([130,-60,0,35,-40,0],135)

# control.rob_moveto([130,-60,10,35,-12,0],135)

# control.rob_moveto([130,-60,0,35,-40,0],135)

# control.rob_moveto([0,-90,0,0,-90,0],135)

# control.rob_moveto([0,0,0,0,0,0])

# 2) 读取当前状态，保留其他轴位置
# state = requests.get(LUMI_GETSTATE_URL).json()
# lift, waist, head, pitch = [j["pos"] for j in state]  # 升降、腰、头旋转、头俯仰

# waist = 0

# 手臂出厂初始位置
# control.rob_moveto([0,120,-120,0,-90,0],45)

# requests.post(
#     LUMI_MOVETO_URL,
#     json={"pos": [lift, waist, head, 30], "vel": 100, "acc": 100},
# )

# control.rob_moveto([55,-47,-99.118,137.660,-62.822,-111.643],45)

# control.rob_moveto([66.036,-61.929,-63.635,140.258,-40.901,-102.124],45)
# control.rob_moveto([55,-47,-99.118,137.660,-62.822,-111.643],45)
# control.rob_moveto([59.267,-30.730,-77.547,115.592,-33.558,-76.149],45)
# control.rob_moveto([65.433,-49.846,-48.038,104.483,-27.209,-63.290],45)
# control.rob_moveto([98.871,-41.383,-50.385,104.482,13.811,-63.399],45)

# control.rob_moveto([55.445,-86.209,-68.331,141.150,-66.965,-117.892],45)

# control.rob_moveto([64.555,-101.178,-31.059,144.434,-46.963,-110.069],45)

# control.rob_moveto([91.588,-88.442,-61.406,181.807,-57.796,-138.886],45)

# control.rob_moveto([66.036,-61.929,-63.635,140.258,-40.901,-102.124],45)

control.rob_moveto([91,-55.087,-81.792,181.527,-47.280,-135.079],45)
# sample usage: open then close
# command_gripper(0, position=1000)
# time.sleep(1.0)
# command_gripper(0, position=250)
# time.sleep(1.0)
# command_gripper(0, position=1000)
# command_gripper(1, position=0)

# control.rob_moveto([55,-47,-99.118,137.660,-62.822,-111.643],45)

# control.rob_moveto([0,120,-120,0,-90,0],45)


# 设置腰部旋转角度
# waist = -90
# print(lift, waist, head,pitch)
# 3) 将头部旋转设为 30°
# requests.post(
#     LUMI_MOVETO_URL,
#     json={"pos": [lift, waist, head, 30], "vel": 100, "acc": 100},
# )

# control.rob_moveto([73,-95,-11.552,140,-21,-93.617],45)

# control.rob_moveto([55,-47,-99.118,137.660,-62.822,-111.643],45)

# control.rob_moveto([0,120,-120,0,-90,0],45)