import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from k1_msgs.srv import JointMove, LinearMove, KineInverse7
from std_srvs.srv import SetBool
import sys
import time
import math

class JakaRobotClient(Node):
    def __init__(self):
        super().__init__('jaka_robot_client')

        # Clients for services
        self.joint_move_client = self.create_client(JointMove, 'joint_move')
        self.linear_move_client = self.create_client(LinearMove, 'linear_move')
        self.kine_inverse_client = self.create_client(KineInverse7, 'kine_inverse')
        self.servo_move_enable_client = self.create_client(SetBool, 'right_arm/servo_move_enable')

        # Publisher to send servo_j commands
        self.publisher_servo_j = self.create_publisher(JointState, 'robot_command_servo_j', 10)
        self.publisher_servo_p = self.create_publisher(JointState, 'robot_command_servo_p', 10)
        
        # Wait for the services to be available
        while not self.joint_move_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service joint_move not available, waiting again...')
        # while not self.linear_move_client.wait_for_service(timeout_sec=1.0):
        #     self.get_logger().info('Service linear_move not available, waiting again...')
        # while not self.kine_inverse_client.wait_for_service(timeout_sec=1.0):
        #     self.get_logger().info('Service kine_inverse not available, waiting again...')
        # while not self.servo_move_enable_client.wait_for_service(timeout_sec=1.0):
        #     self.get_logger().info('Service servo_move_enable not available, waiting again...')

    def call_joint_move(self, joint_positions, move_mode, is_blocking, speed):
        request = JointMove.Request()
        request.joint_positions = joint_positions
        request.move_mode = move_mode
        request.is_blocking = is_blocking
        request.speed = speed
        future = self.joint_move_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    # def call_linear_move(self, end_position, move_mode, is_blocking, speed):
    #     request = LinearMove.Request()
    #     request.end_position = end_position
    #     request.move_mode = move_mode
    #     request.is_blocking = is_blocking
    #     request.speed = speed
    #     future = self.linear_move_client.call_async(request)
    #     rclpy.spin_until_future_complete(self, future)
    #     return future.result()

    # def call_kine_inverse(self, ref_joint_pos, cartesian_pose):
    #     request = KineInverse.Request()
    #     request.ref_joint_pos = ref_joint_pos
    #     request.cartesian_pose = cartesian_pose
    #     future = self.kine_inverse_client.call_async(request)
    #     rclpy.spin_until_future_complete(self, future)
    #     return future.result()

    def call_servo_move_enable(self, enable):
        request = SetBool.Request()
        request.data = enable
        future = self.servo_move_enable_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    # def publish_servo_j_command(self, joint_positions):
    #     msg = JointState()
    #     msg.header.stamp = self.get_clock().now().to_msg()
    #     # msg.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
    #     msg.position = joint_positions
    #     self.publisher_servo_j.publish(msg)

    def publish_servo_p_command(self, joint_positions):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        # msg.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']   # abs without name, relative with name
        msg.position = joint_positions
        self.publisher_servo_p.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = JakaRobotClient()
    action_publisher = Node('action_publisher')
    #left_gripper_pub = action_publisher.create_publisher(JointState, '/left_gripper/set_pos', 10)
    #right_gripper_pub = action_publisher.create_publisher(JointState, '/right_gripper/set_pos', 10)
    rclpy.spin_once(action_publisher, timeout_sec=1)
    # for i in range(100):
    #     left_gripper_cmd = JointState()
    #     right_gripper_cmd = JointState()
    #     left_gripper_cmd.position = [0.3]
    #     right_gripper_cmd.position = [0.3]
    #     left_gripper_pub.publish(left_gripper_cmd)
    #     right_gripper_pub.publish(right_gripper_cmd)

    
    try:
        # Example usage of the client methods
        # Replace these calls with your own logic or command-line arguments
        print("before")
        # response = node.call_servo_move_enable(False)
        # print(f"Servo Move Enable Response: {response.message}")
        
        response = node.call_joint_move([0.31834805013333334
,-1.4057579687466666
,-0.8645662835200001
,-0.29656634144000005
,-1.3688966155733333,
-0.0
], 0, True, 1.0)
                                        
        time.sleep(1)
        print("after")


        #  # Call servo_move_enable service
        # response = node.call_servo_move_enable(True)
        # print(f"Servo Move Enable Response: {response.message}")

        # servo_pose_relative = [0.0, 0.0, 0.2, 0.0, 0.0, 0.0]
        # servo_pose_abs = [307.691, 499.850, -144.30, -99.530/180*math.pi, 4.659/180*math.pi, -78.6/180*math.pi]
        # # servo_pose_abs_right = [433.788, -356.331, -164.179, -95.296/180*math.pi, -2.540/180*math.pi, -78.470/180*math.pi]

        # for i in range(50):
        #     # servo_pose_abs_left[2] += servo_pose_relative[2]  
        #     # servo_pose_abs_right[2] += servo_pose_relative[2]  
        #     # servo_pose_abs = servo_pose_abs_left + servo_pose_abs_right
        #     servo_pose_abs += servo_pose_relative[2]  
        #     node.publish_servo_p_command(servo_pose_abs)
        #     # servo_pose_rel = servo_pose_relative + servo_pose_relative
        #     # node.publish_servo_p_command(servo_pose_rel)
        #     time.sleep(0.008)
        
        # time.sleep(5)

        # response = node.call_servo_move_enable(False)
        # print(f"Servo Move Enable Response: {response.message}")


    except KeyboardInterrupt:
        pass

    finally:
        action_publisher.destroy_node()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()