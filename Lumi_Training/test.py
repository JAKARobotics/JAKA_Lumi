import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, JointState
import time
rclpy.init(args=None)
action_publisher = Node('action_publisher')
rclpy.spin_once(action_publisher, timeout_sec=0.1)
time.sleep(5)
left_gripper_pub = action_publisher.create_publisher(JointState, '/left_gripper/set_pos', 10)
right_gripper_pub = action_publisher.create_publisher(JointState, '/right_gripper/set_pos', 10)
left_gripper_cmd = JointState()
left_gripper_cmd.position = [0.3]
left_gripper_pub.publish(left_gripper_cmd)
right_gripper_pub.publish(left_gripper_cmd)
