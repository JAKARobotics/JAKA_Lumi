import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Int32
import numpy as np
import time
import sys

class FakePublisher(Node):
    def __init__(self):
        super().__init__('fake_data_publisher')
        # 发布机器人关节状态 
        self.left_arm_qpos_pub = self.create_publisher(JointState, '/left_arm/joint_states', 10)
        self.right_arm_qpos_pub = self.create_publisher(JointState, '/right_arm/joint_states', 10)
        # 发布机器人关节速度
        self.left_arm_qvel_pub = self.create_publisher(JointState, '/left_arm/joint_states_vel', 10)
        self.right_arm_qvel_pub = self.create_publisher(JointState, '/right_arm/joint_states_vel', 10)
        # 发布机器人夹爪位置
        self.left_gripper_qpos_pub = self.create_publisher(JointState, '/left_arm/cur_gripper_val', 10)
        self.right_gripper_qpos_pub = self.create_publisher(JointState, '/right_arm/cur_gripper_val', 10)
        # 发布虚拟现实控制的机器人动作
        self.left_vr_pose_pub = self.create_publisher(JointState, '/left_arm/robot_command_servo_j', 10)
        self.right_vr_pose_pub = self.create_publisher(JointState, '/right_arm/robot_command_servo_j', 10)
        self.left_vr_gripper_pub = self.create_publisher(JointState, '/left_arm/gripper_command_val', 10)
        self.right_vr_gripper_pub = self.create_publisher(JointState, '/right_arm/gripper_command_val', 10)

        self.timer = self.create_timer(0.05, self.publish_fake_data)

    def publish_fake_data(self):
        # 创建假的关节状态数据
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = self.get_clock().now().to_msg()  # 设置时间戳为当前时间
        joint_state_msg.position = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]  # 假设7个关节
        joint_state_msg.velocity = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07]  # 假设7个关节速度
        self.left_arm_qpos_pub.publish(joint_state_msg)
        self.right_arm_qpos_pub.publish(joint_state_msg)

        # 发布假的关节速度
        velocity_msg = JointState()
        velocity_msg.header.stamp = self.get_clock().now().to_msg()  # 添加时间戳
        velocity_msg.velocity = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07]  # 假设7个关节速度
        self.left_arm_qvel_pub.publish(velocity_msg)
        self.right_arm_qvel_pub.publish(velocity_msg)

        # 发布假的夹爪位置
        gripper_msg = JointState()
        gripper_msg.header.stamp = self.get_clock().now().to_msg()  # 添加时间戳
        gripper_msg.position = [500.0]  # 假设夹爪位置为500
        self.left_gripper_qpos_pub.publish(gripper_msg)
        self.right_gripper_qpos_pub.publish(gripper_msg)

        # 创建假的VR控制数据
        vr_pose_msg = JointState()
        vr_pose_msg.header.stamp = self.get_clock().now().to_msg()  # 添加时间戳
        vr_pose_msg.position = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]  # 假设7个位置和姿态数据
        self.left_vr_pose_pub.publish(vr_pose_msg)
        self.right_vr_pose_pub.publish(vr_pose_msg)

        # 发布假的VR夹爪控制数据
        vr_gripper_msg = JointState()
        vr_gripper_msg.header.stamp = self.get_clock().now().to_msg()  # 添加时间戳
        vr_gripper_msg.position = [1.0]  # 假设VR夹爪状态为1
        self.left_vr_gripper_pub.publish(vr_gripper_msg)
        self.right_vr_gripper_pub.publish(vr_gripper_msg)

def main(args=None):
    rclpy.init(args=args)
    fake_publisher = FakePublisher()
    try:
        rclpy.spin(fake_publisher)
    except KeyboardInterrupt:
        print('Fake publisher node stopped cleanly')
    except BaseException:
        print('Exception in fake publisher:', file=sys.stderr)
        raise
    finally:
        fake_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()