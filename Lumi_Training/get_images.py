import rclpy
from pendulum_msgs.msg import JointState
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import message_filters


class SyncCameraSubscriber(Node):
    def __init__(self):
        super().__init__('sync_camera_subscriber')
        self.bridge = CvBridge()
        self.topic_status = {
            '/head_camera/color/image_raw': False,
            '/front_camera/color/image_raw': False,
            '/right_camera/color/image_raw': False,
            '/left_camera/color/image_raw': False
        }

        # 订阅四个相机的图像话题
        self.head_cam_sub = message_filters.Subscriber(self, Image, '/head_camera/color/image_raw')
        self.front_cam_sub = message_filters.Subscriber(self, Image, '/front_camera/color/image_raw')
        self.right_cam_sub = message_filters.Subscriber(self, Image, '/right_camera/color/image_raw')
        self.left_cam_sub = message_filters.Subscriber(self, Image, '/left_camera/color/image_raw')
        # self.test = message_filters.Subscriber(self, JointState, '/left_arm/joint_states')
        # 创建单独的订阅者以检查每个话题是否有数据
        self.create_subscription(Image, '/head_camera/color/image_raw', self.head_cam_callback, 10)
        self.create_subscription(Image, '/front_camera/color/image_raw', self.front_cam_callback, 10)
        self.create_subscription(Image, '/right_camera/color/image_raw', self.right_cam_callback, 10)
        self.create_subscription(Image, '/left_camera/color/image_raw', self.left_cam_callback, 10)

        # 使用 ApproximateTimeSynchronizer 同步四个话题
        self.ts = message_filters.ApproximateTimeSynchronizer(
            [self.head_cam_sub, self.right_cam_sub, self.left_cam_sub, self.front_cam_sub],
            queue_size=10,  # 增大队列大小
            slop=1  # 允许的时间误差（秒）
            ,allow_headerless = True
        )
        self.ts.registerCallback(self.image_callback)

        self.get_logger().info("Synchronized camera subscriber initialized.")

        # 定时检查未接收到数据的话题
        self.create_timer(0.5, self.check_topic_status)

    def head_cam_callback(self, msg):
        self.topic_status['/head_camera/color/image_raw'] = True

    def front_cam_callback(self, msg):
        self.topic_status['/front_camera/color/image_raw'] = True

    def right_cam_callback(self, msg):
        self.topic_status['/right_camera/color/image_raw'] = True

    def left_cam_callback(self, msg):
        self.topic_status['/left_camera/color/image_raw'] = True

    def check_topic_status(self):
        for topic, status in self.topic_status.items():
            if not status:
                self.get_logger().error(f"ERROR: No data received from {topic}!")

    def image_callback(self, head_msg, right_msg, left_msg, front_msg):
        try:
            self.get_logger().info("Received synchronized images.")

            # 检查哪些话题没有数据
            for topic, status in self.topic_status.items():
                if not status:
                    self.get_logger().warn(f"No data received from {topic}!")

            # 将 ROS 图像消息转换为 OpenCV 格式
            head_image = self.bridge.imgmsg_to_cv2(head_msg, desired_encoding='bgr8')
            right_image = self.bridge.imgmsg_to_cv2(right_msg, desired_encoding='bgr8')
            left_image = self.bridge.imgmsg_to_cv2(left_msg, desired_encoding='bgr8')
            front_image = self.bridge.imgmsg_to_cv2(front_msg, desired_encoding='bgr8')

            # 显示图像
            cv2.imshow("Head Camera", head_image)
            cv2.imshow("Right Camera", right_image)
            cv2.imshow("Left Camera", left_image)
            cv2.imshow("Front Camera", front_image)

            # 等待 1 毫秒并检查是否按下 'q' 键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.get_logger().info("Exiting image display.")
                cv2.destroyAllWindows()
                rclpy.shutdown()

        except Exception as e:
            self.get_logger().error(f"Failed to convert or display images: {e}")


def main(args=None):
    rclpy.init(args=args)
    sync_camera_subscriber = SyncCameraSubscriber()

    try:
        rclpy.spin(sync_camera_subscriber)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        sync_camera_subscriber.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
