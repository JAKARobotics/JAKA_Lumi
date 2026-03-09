import json, requests
from utilfs.lumi_url import LUMI_ENABLE_URL, LUMI_MOVETO_URL, LUMI_GETSTATE_URL
from utilfs.lumi_url import LUMI_RESET_URL, LUMI_STATUS_URL,LUMI_SYSINFO_URL

import time

# get system infomation, including version, serial num

# response = requests.post(LUMI_ENABLE_URL, json={"enable": 0})

# if response.status_code != 200:
#     print(f"Error: {response.status_code}")
# print("disable ok")
# time.sleep(2)

response = requests.get(LUMI_SYSINFO_URL)
print(f"LUMI_SYSINFO_URL:{response.text}")

# 复位所有轴错误
response = requests.post(LUMI_RESET_URL, json={})
print(f"LUMI_RESET_URL:{response.text}")


# 开启升降柱、头部电机使能
response = requests.post(LUMI_ENABLE_URL, json={"enable": 1})
print(f"LUMI_ENABLE_URL ON:{response.text}")

# 2) 读取当前状态，保留其他轴位置
state = requests.get(LUMI_GETSTATE_URL).json()
lift, waist, head, pitch = [j["pos"] for j in state]  # 升降、腰、头旋转、头俯仰
lift = 0
waist = 0
print(lift, waist, head,pitch)
# 3) 将头部旋转设为 30°
requests.post(
    LUMI_MOVETO_URL,
    json={"pos": [lift, waist, head, 0], "vel": 100, "acc": 100},
)


response = requests.post(LUMI_ENABLE_URL, json={"enable": 0})

if response.status_code != 200:
    print(f"Error: {response.status_code}")
print("disable ok")