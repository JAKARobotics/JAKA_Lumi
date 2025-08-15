import numpy as np


def calculate_velocity(points, dt):
    """
    计算每个点的速度值
    :param points: 包含所有点的列表，每个点是一个元组 (x, y, z, rx, ry, rz)
    :param dt: 时间间隔
    :return: 返回每个点的线速度和角速度
    """
    velocities = []
    for i in range(1, len(points)):
        # 当前点和前一个点
        prev_point = points[i - 1]
        curr_point = points[i]

        # 提取坐标和旋转角度
        x1, y1, z1, rx1, ry1, rz1 = prev_point
        x2, y2, z2, rx2, ry2, rz2 = curr_point

        # 计算线速度
        linear_velocity_x = (x2 - x1) / dt
        linear_velocity_y = (y2 - y1) / dt
        linear_velocity_z = (z2 - z1) / dt

        # 计算角速度
        angular_velocity_rx = (rx2 - rx1) / dt
        angular_velocity_ry = (ry2 - ry1) / dt
        angular_velocity_rz = (rz2 - rz1) / dt

        # 将速度值保存为字典
        velocity = {
            'linear_velocity': (linear_velocity_x, linear_velocity_y, linear_velocity_z),
            'angular_velocity': (angular_velocity_rx, angular_velocity_ry, angular_velocity_rz)
        }
        velocities.append(velocity)

    return velocities


# 示例数据：10个点的坐标和旋转角度
points = [
    (1.0, 2.0, 3.0, 0.1, 0.2, 0.3),
    (1.1, 2.1, 3.1, 0.2, 0.3, 0.4),
    (1.2, 2.2, 3.2, 0.3, 0.4, 0.5),
    (1.3, 2.3, 3.3, 0.4, 0.5, 0.6),
    (1.4, 2.4, 3.4, 0.5, 0.6, 0.7),
    (1.5, 2.5, 3.5, 0.6, 0.7, 0.8),
    (1.6, 2.6, 3.6, 0.7, 0.8, 0.9),
    (1.7, 2.7, 3.7, 0.8, 0.9, 1.0),
    (1.8, 2.8, 3.8, 0.9, 1.0, 1.1),
    (1.9, 2.9, 3.9, 1.0, 1.1, 1.2)
]

# 时间间隔（假设为 0.1 秒）
dt = 0.1

# 计算每个点的速度
velocities = calculate_velocity(points, dt)

# 输出结果
for i, velocity in enumerate(velocities):
    print(f"点 {i + 1} 到点 {i + 2} 的速度：")
    print(f"  线速度 (m/s): {velocity['linear_velocity']}")
    print(f"  角速度 (rad/s): {velocity['angular_velocity']}")
    print()