# LUMI 大模型分拣机器人应用

## 项目简介

本项目基于视觉大模型与机器人集成，面向多站点分拣、自动标定、智能检测与抓取等场景。支持多站点任务调度、手眼标定、视觉识别与抓取、AGV联动等功能。

---

## 目录结构

- `multi_station_demo.py` 多站点分拣主控脚本
- `visualDetect_ali.py` 视觉识别与抓取主流程
- `visualValidCalib.py` 标定结果验证与像素-世界坐标映射
- `AutoCalibProccess.py` 手动手眼标定采集与计算
- `utilfs/` 机器人与工具函数库
- `conf/` 配置文件（机器人参数、标定参数、站点配置等）
- `requirements.txt` 依赖环境
- `JAKA_SDK_LINUX/` JAKA机器人SDK（需配置环境变量）
- `images/` 检测结果与采集图片保存目录

---

## 环境配置

1. **依赖安装**
   ```bash
   pip install -r requirements.txt
   ```
   - 依赖主要包括：`opencv-python`, `numpy`, `matplotlib`, `dashscope` 等。

2. **Orbbec相机SDK**
   - 推荐使用 [pyorbbecsdk](https://github.com/orbbec/pyorbbecsdk) 或本项目自带的 `OrbbecSDK` 目录。
   - 确保相机驱动和SDK已正确安装。

3. **JAKA机器人SDK**
   - 将 `JAKA_SDK_LINUX` 路径加入环境变量：
     ```bash
     export LD_LIBRARY_PATH=/path/to/JAKA_SDK_LINUX:$LD_LIBRARY_PATH
     ```

---

## 配置文件说明

### `conf/userCmdControl.json`

- **cameraParams**：相机对齐、同步、图片保存路径
- **objects**：分拣目标与放置目标名称
- **operationMode**：操作模式（`both`/`grasp_only`/`put_only`/`grasp_priority`）
- **robotParams**：机器人初始位姿、抓取/放置偏移、抬升高度等
- **calibrateParams**：标定板参数、机器人IP、标定图片保存路径
- **genNearPointParams**：像素点深度搜索参数
- **systemConfig**：机器人、AGV、外部轴等系统IP与端口
- **stations**：多站点配置（站点名、AGV标记、机器人/外部轴初始位、站点操作模式）

### `conf/CalibParams-lumi-hand.json`

- 相机内参、畸变、旋转、平移矩阵（标定结果）

---

## 主要功能与脚本

### 1. 多站点分拣任务（`multi_station_demo.py`）

- 支持多站点自动调度，AGV移动、机器人抓取/放置、视觉检测一体化。
- 站点配置、操作模式均可在 `userCmdControl.json` 中灵活设定。
- 运行方式：
  ```bash
  python multi_station_demo.py
  ```

### 2. 视觉检测与抓取（`visualDetect_ali.py`）

- 支持自动/手动两种模式，自动识别目标物体与放置点，自动完成抓取与放置动作。
- 支持命令行参数：
  - `--auto` 自动执行（不等待人工确认）
  - `--camera-sn` 指定相机序列号
  - `--list-cameras` 列出所有可用相机
- 运行方式：
  ```bash
  python visualDetect_ali.py --auto
  ```

### 3. 手动手眼标定（`AutoCalibProccess.py`）

- 按 `k` 采集一组图片与机器人位姿，按 `p` 执行标定计算，按 `q` 退出。
- 标定结果保存在 `conf/CalibParams-lumi-hand.json`。

### 4. 标定结果验证（`visualValidCalib.py`）

- 实时显示相机画面，点击像素点可输出其世界坐标，辅助验证标定精度。

---

## 典型流程

1. **手眼标定**  
   运行 `AutoCalibProccess.py`，采集标定图片与位姿，生成标定参数。

2. **标定验证**  
   运行 `visualValidCalib.py`，点击画面验证像素-世界坐标映射。

3. **配置参数**  
   编辑 `conf/userCmdControl.json`，设定机器人、相机、站点、目标物体等参数。

4. **主要分拣任务运行**  
   运行 `multi_station_demo.py` 或 `visualDetect_ali.py`，实现多站点分拣或单站点视觉抓取。

---

## 注意事项

- 需提前配置好机器人、相机、AGV等硬件网络与SDK环境。
- 标定参数需与实际相机/机器人安装位置一致。
- 运行前请确保 `conf/` 下配置文件参数正确，且图片保存目录存在。

---

## 参考/扩展

- [阿里大模型账号注册](https://help.aliyun.com/zh/dashscope/?spm=a2c4g.11186623.0.0.36b87defCVLRg8)
- [dashscope_api_key获取](https://dashscope.console.aliyun.com/apiKey)
- [Orbbec相机配置](https://github.com/orbbec/pyorbbecsdk)

---

如需更详细的接口说明、二次开发指导，请参考各脚本源码及注释。 


