# coding:UTF-8
'''JAKA SDK Linux Python模块初始化文件'''

# 简单的初始化文件，使Python能够识别该目录为模块
# jkrc将直接从jkrc.so文件导入
pass
# coding:UTF-8
'''JAKA SDK Linux Python模块初始化文件'''

import os
import sys
import ctypes

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 加载libjakaAPI.so动态库
libjaka_path = os.path.join(current_dir, 'libjakaAPI.so')
if os.path.exists(libjaka_path):
    ctypes.CDLL(libjaka_path)
else:
    print(f"[WARNING] 未找到libjakaAPI.so文件: {libjaka_path}")

# 导入jkrc模块
try:
    # 动态加载jkrc.so
    jkrc = ctypes.cdll.LoadLibrary(os.path.join(current_dir, 'jkrc.so'))
    print("[INFO] 成功加载jkrc.so")
except Exception as e:
    print(f"[ERROR] 加载jkrc.so失败: {str(e)}")
    raise ImportError(f"无法加载JAKA SDK: {str(e)}")