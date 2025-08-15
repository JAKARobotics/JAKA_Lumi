import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from pyDHgripper import AG95
import threading
# from eval import left_robot


class GripperController:
    def __init__(self, gripper, name, node):
        self.gripper = gripper
        self.name = name
        self.node = node  # Pass the ROS 2 node for logging
        self.pos_publisher = None
        self.force_subscription = None
        self.pos_subscription = None
        self.vel_subscription = None

    def setup_publishers(self):
        self.pos_publisher = self.node.create_publisher(Int32, f'{self.name}/current_pos', 10)

    def setup_subscriptions(self):
        self.force_subscription = self.node.create_subscription(
            Int32, f'{self.name}/set_force', self.force_callback, 10
        )
        self.pos_subscription = self.node.create_subscription(
            Int32, f'{self.name}/set_pos', self.pos_callback, 10
        )
        self.vel_subscription = self.node.create_subscription(
            Int32, f'{self.name}/set_vel', self.vel_callback, 10
        )

    def force_callback(self, msg):
        self.gripper.set_force(val=msg.data)
        self.node.get_logger().info(f'{self.name} force set to: {msg.data}')

    def pos_callback(self, msg):
        self.gripper.set_pos(val=msg.data)
        self.node.get_logger().info(f'{self.name} position set to: {msg.data}')

    def vel_callback(self, msg):
        self.gripper.set_vel(val=msg.data)
        self.node.get_logger().info(f'{self.name} velocity set to: {msg.data}')

    def publish_position(self):
        current_pos = self.gripper.read_pos()
        msg = Int32()
        msg.data = current_pos
        self.pos_publisher.publish(msg)
        self.node.get_logger().info(f'{self.name} current position: {current_pos}')


class DHGripperNode(Node):
    def __init__(self):
        super().__init__('dhgripper_node')

        # Initialize grippers
        self.grippers = {
            'left_gripper': GripperController(AG95(port='/dev/ttyUSB0'), 'left_gripper', self),
            'right_gripper': GripperController(AG95(port='/dev/ttyUSB1'), 'right_gripper', self),
        }

        # Setup publishers and subscriptions for each gripper
        for gripper in self.grippers.values():
            gripper.setup_publishers()
            gripper.setup_subscriptions()

        # Timer to publish current positions
        self.timer = self.create_timer(0.001, self.timer_callback)  # 10 Hz
        self.lock = threading.Lock()  # To ensure thread-safe operations

    def timer_callback(self):
        threads = []
        for gripper in self.grippers.values():
            thread = threading.Thread(
                    target=gripper.publish_position,
                    daemon=True  # Thread exits when main program does
            )
            threads.append(thread)
            thread.start()

            # Wait for all threads to complete (optional)
        for thread in threads:
            thread.join()


def main(args=None):
    rclpy.init(args=args)
    node = DHGripperNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()