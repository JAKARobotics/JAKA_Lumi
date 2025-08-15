import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import time

class GripperPublisher(Node):
    def __init__(self):
        super().__init__('right_gripper_publisher')
        self.publisher_ = self.create_publisher(JointState, 'right_gripper/current_pos', 10)
        self.timer = self.create_timer(0.008, self.publish_joint_state)  # 每秒发布一次

    def publish_joint_state(self):
        msg = JointState()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg() 
        msg.name = ['gripper_joint']  # 关节名称
        msg.position = [0.5]  # 关节位置
        msg.velocity = [0.0]  # 关节速度
        msg.effort = [0.0]  # 关节力矩
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg)

def main(args=None):
    rclpy.init(args=args)
    gripper_publisher = GripperPublisher()
    rclpy.spin(gripper_publisher)
    gripper_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()