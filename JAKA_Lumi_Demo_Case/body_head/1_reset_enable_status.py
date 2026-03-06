from lumi_url import LUMI_RESET_URL, LUMI_ENABLE_URL,LUMI_STATUS_URL,LUMI_SYSINFO_URL
import requests
import time

# get system infomation, including version, serial num

response = requests.get(LUMI_SYSINFO_URL)
print(f"LUMI_SYSINFO_URL:{response.text}")

# 复位所有轴错误
response = requests.post(LUMI_RESET_URL, json={})
print(f"LUMI_RESET_URL:{response.text}")


# 开启升降柱、头部电机使能
response = requests.post(LUMI_ENABLE_URL, json={"enable": 1})
print(f"LUMI_ENABLE_URL ON:{response.text}")
# 关闭升降柱、头部电机使能
response = requests.post(LUMI_ENABLE_URL, json={"enable": 0})
print(f"LUMI_ENABLE_URL OFF:{response.text}")


# 获取当前运动状态
response = requests.get(LUMI_STATUS_URL)
print(f"LUMI_STATUS_URL:{response.text}")


