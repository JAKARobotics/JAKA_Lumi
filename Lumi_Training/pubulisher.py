import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray  # 使用标准消息类型
import random


class ArrayPublisher(Node):
    def __init__(self):
        super().__init__('array_publisher')

        # 创建一个发布者，发布Float32MultiArray消息到话题`/16d_array`
        self.publisher = self.create_publisher(Float32MultiArray, '/array', 10)

        # 设置定时器，每秒发布一次
        self.timer = self.create_timer(0, self.timer_callback)

    def timer_callback(self):
        # 创建一个Float32MultiArray消息对象
        msg = Float32MultiArray()

        # 随机生成16维度的数组
        msg.data = [random.uniform(0.0, 100.0) for _ in range(16)]

        # 发布消息
        self.publisher.publish(msg)

        # 打印日志
        self.get_logger().info(f'Publishing: {msg.data}')


def main(args=None):
    rclpy.init(args=args)

    # 创建发布者节点
    array_publisher = ArrayPublisher()

    # 运行节点
    rclpy.spin_once(array_publisher)

    # 销毁节点并关闭ROS 2
    array_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()