import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, JointState
from cv_bridge import CvBridge
import cv2
import numpy as np
from eval_interface import *
from constants import *
from std_srvs.srv import SetBool
from example_interfaces.srv import AddTwoInts
# 窗口配置
window_width = 1920 // 4
window_height = 1080 // 2
camera_names = ['left_cam', 'front_cam', 'right_cam', 'head_cam']
for i, name in enumerate(camera_names):
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, window_width, window_height)
    cv2.moveWindow(name, window_width * i, 0)


class CameraSubscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber')
        self.bridge = CvBridge()

        # 初始化图像存储变量
        self.images = {
            'head_cam': None,
            'right_cam': None,
            'left_cam': None,
            'front_cam': None
        }

        # 创建四个独立的订阅者
        self.create_subscription(Image, '/head_camera/color/image_raw',
                                 lambda msg: self.image_callback(msg, 'head_cam'), 10)
        self.create_subscription(Image, '/right_camera/color/image_raw',
                                 lambda msg: self.image_callback(msg, 'right_cam'), 10)
        self.create_subscription(Image, '/left_camera/color/image_raw',
                                 lambda msg: self.image_callback(msg, 'left_cam'), 10)
        self.create_subscription(Image, '/front_camera/color/image_raw',
                                 lambda msg: self.image_callback(msg, 'front_cam'), 10)

    def image_callback(self, msg, camera_name):
        try:
            self.images[camera_name] = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f"{camera_name} error: {e}")

    def get_images(self):
        return [self.images[name] for name in camera_names]


class JointStateSubscriber(Node):
    def __init__(self):
        super().__init__('joint_state_subscriber')

        # 初始化状态存储变量
        self.states = {
            'left_arm_pos': None,
            'right_arm_pos': None,
            'left_gripper_pos': None,
            'right_gripper_pos': None,
            'left_arm_vel': None,
            'right_arm_vel': None
        }

        # 创建六个独立的订阅者
        self.create_subscription(JointState, '/left_arm/joint_states',
                                 lambda msg: self.joint_callback(msg, 'left_arm_pos'), 10)
        self.create_subscription(JointState, '/right_arm/joint_states',
                                 lambda msg: self.joint_callback(msg, 'right_arm_pos'), 10)
        self.create_subscription(JointState, '/left_gripper/current_pos',
                                 lambda msg: self.joint_callback(msg, 'left_gripper_pos'), 10)
        self.create_subscription(JointState, '/right_gripper/current_pos',
                                 lambda msg: self.joint_callback(msg, 'right_gripper_pos'), 10)
        self.create_subscription(JointState, '/left_arm/joint_states_vel',
                                 lambda msg: self.joint_callback(msg, 'left_arm_vel'), 10)
        self.create_subscription(JointState, '/right_arm/joint_states_vel',
                                 lambda msg: self.joint_callback(msg, 'right_arm_vel'), 10)

    def joint_callback(self, msg, state_type):
        try:
            if 'pos' in state_type:
                self.states[state_type] = msg.position[:7] if 'arm' in state_type else [msg.position[0]]
            elif 'vel' in state_type:
                self.states[state_type] = msg.velocity[:7]
        except Exception as e:
            self.get_logger().error(f"{state_type} error: {e}")

    def get_states(self):
        # 检查所有状态是否已接收
        if all(v is not None for v in self.states.values()):
            q_pos = np.concatenate([self.states['left_arm_pos'],self.states['left_gripper_pos'],self.states['right_arm_pos'],self.states['right_gripper_pos']])
            q_vel = np.concatenate([
                self.states['left_arm_vel'],
                self.states['left_gripper_pos'],  # 保持原始逻辑
                self.states['right_arm_vel'],
                self.states['right_gripper_pos']
            ])
            return q_pos, q_vel
        return None, None


class servo_move(Node):
    def __init__(self):
        super().__init__('servo_move')
        # Create a service client
        self.client = self.create_client(
            SetBool,
            '/left_arm/servo_move_enable'
        )
    def send_request(self, value):
        request = SetBool.Request()
        request.data = value
        self.client.call_async(request)
def main(args=None):
    rclpy.init(args=args)
    act = ACT("sim_transfer_cube_scripted")

    # 创建订阅节点
    camera_sub = CameraSubscriber()
    joint_sub = JointStateSubscriber()
    action_publisher = Node('action_publisher')
    servo_move_enable = servo_move()
    # 创建控制指令发布者
    left_pub = action_publisher.create_publisher(JointState, '/left_arm/robot_command_servo_j', 10)
    right_pub = action_publisher.create_publisher(JointState, '/right_arm/robot_command_servo_j', 10)
    rclpy.spin_once(servo_move_enable,timeout_sec=1)
    servo_move_enable.send_request(True)

    try:
        for i in range(400):
            # 处理所有待处理消息
            for _ in range(20):
                rclpy.spin_once(camera_sub, timeout_sec=0.1)
                rclpy.spin_once(joint_sub, timeout_sec=0.1)
                rclpy.spin_once(action_publisher, timeout_sec=0.1)

            # 获取最新数据
            images = camera_sub.get_images()
            q_pos, q_vel = joint_sub.get_states()
            # print(images)
            # 数据有效性检查
            if (images is None) or (q_pos is None) or (q_vel is None):
                continue

            # 显示图像
            for name, img in zip(camera_names, images):
                if img is not None:
                    cv2.imshow(name, img)
            cv2.waitKey(1)

            # 构建观测字典
            obs = {
                'qpos': q_pos,
                'qvel': q_vel,
                'images': dict(zip(camera_names, images))
            }

            # 生成控制指令
            action = act.eval_with_temporal_agg(obs,i)
            print(action)
            # 发布控制指令
            left_cmd = JointState()
            left_cmd.position = action[:7].tolist()
            right_cmd = JointState()
            right_cmd.position = action[8:15].tolist()

            left_pub.publish(left_cmd)
            right_pub.publish(right_cmd)

    except KeyboardInterrupt:
        pass
    finally:
        servo_move_enable.send_request(False)
        cv2.destroyAllWindows()
        camera_sub.destroy_node()
        joint_sub.destroy_node()
        action_publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()