from flask import Flask, request
from utilfs.jaka_integrated import JAKAIntegrated
from utilfs.python_open_gripper import ensure_initialized, move_gripper,command_gripper
from utilfs.lumi_url import LUMI_ENABLE_URL, LUMI_MOVETO_URL, LUMI_GETSTATE_URL
from utilfs.lumi_url import LUMI_RESET_URL, LUMI_STATUS_URL,LUMI_SYSINFO_URL

import time
import serial
import json, requests

# 配置sdk路径
# export LD_LIBRARY_PATH="/home/cih/Desktop/repos/JAKA_Lumi/04. JAKA Lumi Demo Case [示例]/LUMI_DEMO-v2/JAKA_SDK_LINUX:$LD_LIBRARY_PATH"

# 网络分配
# # 让 192.168.10.* 走有线 eno1
# sudo ip route replace 192.168.10.0/24 via 192.168.10.1 dev eno1 metric 50

# # 默认路由走 Wi‑Fi
# sudo ip route replace default via 10.195.170.1 dev wlx502b733410a4 metric 100

# # 移除有线的默认路由（如果还在）
# sudo ip route del default via 192.168.10.1 dev eno1 2>/dev/null


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
    
def rotatewaist(rotateValue):

    print(rotateValue)
    # response = requests.post(LUMI_ENABLE_URL, json={"enable": 0})
    # if response.status_code != 200:
    #     print(f"Error: {response.status_code}")
    # print("disable ok")

    response = requests.get(LUMI_SYSINFO_URL)
    # print(f"LUMI_SYSINFO_URL:{response.text}")

    # 复位所有轴错误
    response = requests.post(LUMI_RESET_URL, json={})
    # print(f"LUMI_RESET_URL:{response.text}")


    # 开启升降柱、头部电机使能
    response = requests.post(LUMI_ENABLE_URL, json={"enable": 1})
    print(f"LUMI_ENABLE_URL ON:{response.text}")
    # while(response.text["status"] == -1):
    #     response = requests.post(LUMI_ENABLE_URL, json={"enable": 1})
    #     print(f"LUMI_ENABLE_URL ON:{response.text}")

        # 2) 读取当前状态，保留其他轴位置
    state = requests.get(LUMI_GETSTATE_URL).json()
    lift, waist, head, pitch = [j["pos"] for j in state]  # 升降、腰、头旋转、头俯仰
    lift = 0
    waist = rotateValue
    print(lift, waist, head,pitch)
    # 3) 将头部旋转设为 30°
    requests.post(
        LUMI_MOVETO_URL,
        json={"pos": [lift, waist, head, 0], "vel": 100, "acc": 100},
    )


def grasp1():
    rotatewaist(0)
    # 手臂出厂初始位置
    control.rob_moveto([0,120,-120,0,-90,0],45)
        
    # 准备抓取
    control.rob_moveto([59.267,-30.730,-77.547,115.592,-33.558,-76.149],45)
    # 到达执行位置
    control.rob_moveto([65.433,-49.846,-48.038,104.483,-27.209,-63.290],45)

    # 抓取
    # sample usage: open then close
    command_gripper(0, position=1000)
    time.sleep(0.5)
    command_gripper(0, position=50)
    # command_gripper(1, position=0)
    time.sleep(0.5)
    # command_gripper(0, position=1000)

    #提起
    control.rob_moveto([98.871,-41.383,-50.385,104.482,13.811,-63.399],45)

    rotatewaist(-90)

    control.rob_moveto([66,-44,-123,162,-72,-122.4],45)

    # 伸手
    control.rob_moveto([73,-95,-11.552,140,-21,-93.617],45)
    # 松开手指
    command_gripper(0, position=1000)
    time.sleep(1.0)
    # 收回胳膊
    control.rob_moveto([55,-47,-99.118,137.660,-62.822,-111.643],45)
    # 回到初始位置
    control.rob_moveto([0,120,-120,0,-90,0],45)

def grasp2():
    
    rotatewaist(0)
    # 手臂出厂初始位置
    control.rob_moveto([0,120,-120,0,-90,0],45)

    # 准备抓取
    control.rob_moveto([55,-47,-99.118,137.660,-62.822,-111.643],45)
    # 到达执行位置
    control.rob_moveto([62.679,-63.42,-58.340,132.840,-39.221,-99.501],45)

    # 抓取
    # sample usage: open then close
    command_gripper(0, position=1000)
    time.sleep(0.5)
    command_gripper(0, position=50)
    # command_gripper(1, position=0)
    time.sleep(0.5)
    # command_gripper(0, position=1000)

    #提起
    control.rob_moveto([91,-55.087,-81.792,181.527,-47.280,-135.079],45)

    rotatewaist(-90)

    control.rob_moveto([66,-44,-123,162,-72,-122.4],45)
    # 伸手
    control.rob_moveto([73,-95,-11.552,140,-21,-93.617],45)
    # 松开手指
    command_gripper(0, position=1000)
    time.sleep(1.0)
    # 收回胳膊
    control.rob_moveto([55,-47,-99.118,137.660,-62.822,-111.643],45)
    # 回到初始位置
    control.rob_moveto([0,120,-120,0,-90,0],45)

def grasp3():
    rotatewaist(0)
    # 手臂出厂初始位置
    control.rob_moveto([0,120,-120,0,-90,0],45)

        
    # 准备抓取
    control.rob_moveto([55.445,-86.209,-68.331,141.150,-66.965,-117.892],45)
    # 到达执行位置
    control.rob_moveto([64.555,-101.178,-31.059,144.434,-46.963,-110.069],45)

    # 抓取
    # sample usage: open then close
    command_gripper(0, position=1000)
    time.sleep(0.5)
    command_gripper(0, position=50)
    # command_gripper(1, position=0)
    time.sleep(0.5)
    # command_gripper(0, position=1000)

    #提起
    control.rob_moveto([91.588,-88.442,-61.406,181.807,-57.796,-138.886],45)

    rotatewaist(-90)

    control.rob_moveto([66,-44,-123,162,-72,-122.4],45)
    # 伸手
    control.rob_moveto([73,-95,-11.552,140,-21,-93.617],45)
    # 松开手指
    command_gripper(0, position=1000)
    time.sleep(1.0)
    # 收回胳膊
    control.rob_moveto([55,-47,-99.118,137.660,-62.822,-111.643],45)
    # 回到初始位置
    control.rob_moveto([0,120,-120,0,-90,0],45)


app = Flask(__name__)

# Numbers that are allowed to pass validation.
VALID_VALUES = {"1", "2", "3"}


@app.route("/grasp", methods=["GET", "POST"])
def grasp():
    """Validate the incoming number parameter."""
    payload = request.get_json(silent=True) or {}
    number = (
        request.args.get("number")
        or request.form.get("number")
        or payload.get("number")
    )

    # if number in VALID_VALUES:
    #     return "success"
    if number == "1":
        grasp1()
        return "success"
    elif number == "2":
        grasp2()
        return "success"
    elif number == "3":
        grasp3()    
        return "success"
    else:
        return "wrong number", 400

if __name__ == "__main__":

    config = load_config()

    control = JAKAIntegrated(
            robot_ip=config["robot_ip"],
            ext_base_url=config.get("ext_base_url"),
            agv_ip=config.get("agv_ip"),
            agv_port=config.get("agv_port")
        )

    control.jaka_connect()

    # response = requests.get(LUMI_SYSINFO_URL)
    # print(f"LUMI_SYSINFO_URL:{response.text}")

    # # 复位所有轴错误
    # response = requests.post(LUMI_RESET_URL, json={})
    # print(f"LUMI_RESET_URL:{response.text}")


    # # 开启升降柱、头部电机使能
    # response = requests.post(LUMI_ENABLE_URL, json={"enable": 1})
    # print(f"LUMI_ENABLE_URL ON:{response.text}")

    app.run(host="0.0.0.0", port=12123)