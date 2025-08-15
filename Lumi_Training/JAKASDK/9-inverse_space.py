import os
from JAKA_utils import *
np.set_printoptions(precision=2, suppress=True)
XML_DIR = '../assets'

# ---------- 初始化 ----------
# 启动模拟环境
xml_path = os.path.join(XML_DIR, f'bimanual_JAKA_pos.xml')
physics = mujoco.Physics.from_xml_path(xml_path)

# 启动 JAKA 机器人
ip_left = '192.168.2.222'
ip_right = '192.168.2.223'
# robot = init_robot(ip_left)
robot = init_robot(ip_right)
robot.set_full_dh_flag(1)

# ---------- 获得转移矩阵 ----------
# tr_SIM2JAKA_left = get_transfer_matrix(robot, physics, 'left_arm')
tr_SIM2JAKA_right = get_transfer_matrix(robot, physics, 'right_arm')

refpos = np.radians([-30,-45, 50, -85, -30, 55, 0])
START_LEFT_THETA = np.array([15, -10, -60, -80, 75, 65, -150])*DEG2RAD
START_RIGHT_THETA = np.array([50, -93, -60, -75, -16, -70, 150])*DEG2RAD
# 生成桌面的点云
def generate_point_cloud(x1, x2, y1, y2, z, resolution):
    x = np.arange(x1, x2, resolution)
    y = np.arange(y1, y2, resolution)
    X, Y = np.meshgrid(x, y)
    Z = np.ones_like(X) * z
    point_cloud = np.stack([X, Y, Z], axis=-1)
    return point_cloud.reshape(-1, 3)


point_cloud = generate_point_cloud(0, 0, 0.55, 0.41, 0.52, 0.01)

solvable_points = []

for point in point_cloud:
    try:
        mujoco_inverse_from_SDK(robot, physics, tr_SIM2JAKA_right, START_RIGHT_THETA, point)
        solvable_points.append(point)
    except Exception as e:
        print("Error: ", e)
        print("Point: ", point)

# 绘制可以逆解的点的二维平面散点图
plt.scatter([solvable_point[0] for solvable_point in solvable_points], [solvable_point[1] for solvable_point in solvable_points], c='blue')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('Solvable Points on the Plane')
plt.show()


