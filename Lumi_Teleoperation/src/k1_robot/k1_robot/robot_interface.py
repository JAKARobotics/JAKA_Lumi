import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import PoseStamped
from std_srvs.srv import SetBool
from k1_msgs.srv import JointMove, LinearMove, KineInverse7#, Rotm2rpy
from k1_robot import jkrc
import math

import numpy as np

class JakaRobotDriver(Node):
    def __init__(self):
        super().__init__('jaka_robot_driver')
        
        # Publishers for joint states and current TCP position
        self.publisher_joint_states = self.create_publisher(JointState, 'joint_states', 10)
        self.publisher_joint_states_vel = self.create_publisher(JointState, 'joint_states_vel', 10)
        self.publisher_tcp_position = self.create_publisher(JointState, 'cur_tcp_pose', 10)
        self.publisher_gripper_val = self.create_publisher(JointState, 'cur_gripper_val', 10)
        #self.publisher_raw_torque_sensor_val = self.create_publisher(JointState, 'raw_torque_sensor_val', 10)

        timer_period = 0.008  # seconds (8 ms)
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Services for joint move, linear move, inverse kinematics, and servo move enable
        self.joint_move_service = self.create_service(JointMove, 'joint_move', self.joint_move_callback)
        self.linear_move_service = self.create_service(LinearMove, 'linear_move', self.linear_move_callback)
        self.kine_inverse_service = self.create_service(KineInverse7, 'kine_inverse7', self.kine_inverse_callback)
        # self.rotm2rpy_service = self.create_service(Rotm2rpy, 'rotm2rpy', self.rotm2rpy_callback)
        self.servo_move_enable_service = self.create_service(SetBool, 'servo_move_enable', self.servo_move_enable_callback)

        # Subscriber for servo_j6 commands
        self.subscription_servo_j = self.create_subscription(
            JointState,
            'robot_command_servo_j',
            self.servo_j_callback,
            10)

        self.subscription_servo_p = self.create_subscription(
            JointState,
            'robot_command_servo_p',
            self.servo_p_callback,
            10)

        # # Subscriber for gripper value commands
        # self.subscription_gripper_val = self.create_subscription(
        #     JointState,
        #     'gripper_command_val',
        #     self.gripper_val_callback,
        #     10)
        
        self.declare_parameter('robot_running_mode',"teleop")
        self.robot_running_mode = self.get_parameter('robot_running_mode').get_parameter_value().string_value


        self.declare_parameter('robot_ip', "172.30.95.49")
        robot_ip = self.get_parameter('robot_ip').get_parameter_value().string_value
        # self.robot = jkrc.RC("192.168.2.222")  # 替换为实际IP地址
        self.robot = jkrc.RC(robot_ip)  # 替换为实际IP地址
        self.login()
        self.enable_robot()

        self.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        self.tcp_names = ['x', 'y', 'z', 'w', 'x', 'y', 'z']

        self.servo_move_enabled = False  # Track the state of servo_move_enable

    def login(self):
        ret = self.robot.login()
        if ret[0] != 0:
            self.get_logger().error(f'Failed to login. Error code: {ret[0]}')
            exit(1)

    def enable_robot(self):
        ret = self.robot.power_on()  # 上电操作
        if ret[0] != 0:
            self.get_logger().error(f'Failed to power on robot. Error code: {ret[0]}')
            exit(1)
        ret = self.robot.enable_robot()
        if ret[0] != 0:
            self.get_logger().error(f'Failed to enable robot. Error code: {ret[0]}')
            exit(1)

    def shutdown(self):
        self.robot.logout()

    def timer_callback(self):
        # 发布关节状态
        current_time = self.get_clock().now().to_msg()
        msg_joint_state = JointState()
        msg_joint_state.header.stamp = current_time
        msg_joint_state.name = self.joint_names

        msg_tcp_pose = JointState()
        msg_tcp_pose.header.stamp = current_time
        msg_tcp_pose.name = self.tcp_names

        # msg_tcp_pose = PoseStamped()
        # msg_tcp_pose.header.stamp = current_time

        msg_gripper = JointState()
        msg_gripper.header.stamp = current_time
        msg_gripper.name = self.joint_names

        # msg_raw_torque_sensor = JointState()
        # msg_raw_torque_sensor.header.stamp = current_time
        # msg_raw_torque_sensor.name = self.joint_names

        msg_joint_state_vel = JointState()
        msg_joint_state_vel.header.stamp = current_time
        msg_joint_state_vel.name = self.joint_names

        ret_robot_status = self.robot.get_robot_status()
        print(ret_robot_status) 

        if ret_robot_status[0] == 0:
            # self.get_logger().info(f'get robot status : {np.array(ret_robot_status[1][20][5])[:,3]}')
            msg_joint_state.position = ret_robot_status[1][19]
            
            # msg_raw_torque_sensor.position = ret_robot_status[1][21][6]
            # self.get_logger().warn(f'robot status torque sensor. {msg_raw_torque_sensor.position}')
            # temp_var = ret_robot_status[1][21][6]
            # self.get_logger().warn(f'robot status torque sensor. {temp_var}')

            # msg_tcp_pose.position[0] = ret_robot_status[1][18][0]
            # msg_tcp_pose.position[1] = ret_robot_status[1][18][1]
            # msg_tcp_pose.position[2] = ret_robot_status[1][18][2]
            # # 将旋转角转换为四元数
            # quaternion = self.rpy_to_quaternion(ret_robot_status[1][18][3:])
            # msg_tcp_pose.orientation[3] = quaternion[0]
            # msg_tcp_pose.orientation[4] = quaternion[1]
            # msg_tcp_pose.orientation[5] = quaternion[2]
            # msg_tcp_pose.orientation[6] = quaternion[3]
            
            quaternion = self.rpy_to_quaternion(ret_robot_status[1][18][3:])
            msg_tcp_pose.position = [ret_robot_status[1][18][0], ret_robot_status[1][18][1], ret_robot_status[1][18][2],
                                        quaternion[0], quaternion[1], quaternion[2], quaternion[3]]


            msg_joint_state_vel.velocity = list(np.array(ret_robot_status[1][20][5])[:,3])

            # msg_gripper.position = [(float)(ret_robot_status[1][17][2][2]/1000), 0.0, 0.0, 0.0, 0.0, 0.0]
            msg_gripper.position = [0.5, 0.0, 0.0, 0.0, 0.0, 0.0]
            # msg_gripper.position = [float('nan') for _ in self.joint_names]
        else:
            self.get_logger().warn(f'Failed to get robot status. Error code: {ret_robot_status[0]}')

            msg_joint_state.position = [float('nan') for _ in self.joint_names]
            msg_joint_state_vel.position = [float('nan') for _ in self.joint_names]

            msg_tcp_pose.position = [float('nan') for _ in self.joint_names]


            # msg_tcp_pose.position[0] = float('nan')
            # msg_tcp_pose.position[1] = float('nan')
            # msg_tcp_pose.position[2] = float('nan')
            # msg_tcp_pose.position[3] = 1.0  # 默认四元数，表示无旋转,w,x,y,z
            # msg_tcp_pose.position[4] = 0.0
            # msg_tcp_pose.position[5] = 0.0
            # msg_tcp_pose.position[6] = 0.0

            msg_gripper.position = [float('nan') for _ in self.joint_names]


        self.publisher_joint_states.publish(msg_joint_state)
        self.publisher_joint_states_vel.publish(msg_joint_state_vel)
        self.publisher_tcp_position.publish(msg_tcp_pose)
        self.publisher_gripper_val.publish(msg_gripper)



        # self.get_logger().info('Publishing robot states')

    def joint_move_callback(self, request, response):
        try:
            result = self.robot.joint_move(request.joint_positions, request.move_mode, request.is_blocking, request.speed)
            response.success = int(result[0] == 0)
            response.message = "Success" if response.success else f"Error: {result[0]}"
        except Exception as e:
            response.success = 0
            response.message = str(e)
        return response

    def linear_move_callback(self, request, response):
        try:
            result = self.robot.linear_move(request.end_position, request.move_mode, request.is_blocking, request.speed)
            response.success = int(result[0] == 0)
            response.message = "Success" if response.success else f"Error: {result[0]}"
        except Exception as e:
            response.success = 0
            response.message = str(e)
        return response

    def kine_inverse_callback(self, request, response):
        try:
            result = self.robot.kine_inverse(request.ref_joint_pos, request.cartesian_pose)
            response.success = int(result[0] == 0)
            response.message = "Success" if response.success else f"Error: {result[0]}"
            if response.success:
                response.joint_positions = result[1]
            else:
                response.joint_positions = []  # 或者你可以选择填充 NaNs
        except Exception as e:
            response.success = 0
            response.message = str(e)
            response.joint_positions = []
        return response

    def servo_move_enable_callback(self, request, response):
        """ 新增的服务回调函数，用于控制SERVO MOVE模式的使能 """
        try:
            enable = request.data
            if enable:
                if self.robot_running_mode == 'act_exe':
                    self.robot.servo_move_use_joint_NLF(60,60,60)
                elif self.robot_running_mode == 'teleop':
                    self.robot.servo_move_use_carte_NLF(500, 250, 250, 500, 250, 250)
                elif self.robot_running_mode == 'test':
                    self.robot.servo_move_use_joint_LPF(0.5)
                else:
                    self.robot.servo_move_use_carte_NLF(5000, 2500, 2500, 500, 250, 250)     
            result = self.robot.servo_move_enable(enable)
            self.servo_move_enabled = enable  # 更新内部状态
            response.success = int(result[0] == 0)
            response.message = "Enabled SERVO MOVE mode" if enable else "Disabled SERVO MOVE mode"
            if not response.success:
                response.message = f"Error: {result[0]}"
        except Exception as e:
            response.success = False
            response.message = str(e)
        return response

    def servo_j_callback(self, msg):
        """ 回调函数，处理来自/robot_command_servo_j话题的消息 """
        if not self.servo_move_enabled:
            self.get_logger().warn("Servo Move is not enabled. Please enable it first.")
            return

        try:
            joint_positions = list(msg.position)  # 确保我们有正确的数据类型
            move_mode = 0 if len(msg.name) == 0 else 1  # 如果没有提供关节名，则认为是绝对运动

            # 检查是否提供了有效的关节位置
            if len(joint_positions) != 6:
                self.get_logger().error("Invalid number of joint positions provided. Expected 7, got {}".format(len(joint_positions)))
                return

            # 调用servo_j6接口
            result = self.robot.servo_j(joint_positions, move_mode,2)

            if result[0] == 0:
                self.get_logger().info("Successfully sent servo_j6 command.")
            else:
                self.get_logger().error(f"Failed to send servo_j6 command. Error code: {result[0]}")
        except Exception as e:
            self.get_logger().error(f"Exception occurred while processing servo_j6 command: {str(e)}")

    def servo_p_callback(self, msg):
        """ 回调函数，处理来自/robot_command_servo_p话题的消息 """
        if not self.servo_move_enabled:
            self.get_logger().warn("Servo Move is not enabled. Please enable it first.")
            return

        try:
            cart_position = list(msg.position)  # 确保我们有正确的数据类型
            # move_mode = 0 if len(msg.name) == 0 else 1  # 如果没有提供关节名，则认为是绝对运动
            move_mode = 0 # Default absolute motion

            # 检查是否提供了有效位置
            if len(cart_position) != 6:
                self.get_logger().error("Invalid number of parameters provided. Expected 6, got {}".format(len(cart_position)))
                return

            step_num = 1

            # 调用servo_p接口
            result = self.robot.servo_p(cart_position, move_mode, step_num)

            if result[0] == 0:
                self.get_logger().info("Successfully sent servo_p command.")
            else:
                self.get_logger().error(f"Failed to send servo_p command. Error code: {result[0]}")
        except Exception as e:
            self.get_logger().error(f"Exception occurred while processing servo_p command: {str(e)}")
    
    # def gripper_val_callback(self, msg):
    #     try:
    #         gripper_val_array = msg.position
    #         result = self.robot.set_analog_output(iotype=2, index=3,value = (int)(gripper_val_array[0]*1000))
    #         if result[0] == 0:
    #             self.get_logger().info("Successfully sent gripper val command.")
    #         else:
    #             self.get_logger().error(f"Failed to send gripper val command. Error code: {result[0]}")
    #     except Exception as e:
    #         self.get_logger().error(f"Exception occurred while processing gripper val command: {str(e)}")

    def rpy_to_quaternion(self, rpy):
        """ Convert RPY angles to Quaternion """
        roll, pitch, yaw = rpy
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy

        return (w, x, y, z)

def main(args=None):
    rclpy.init(args=args)
    driver = JakaRobotDriver()
    try:
        rclpy.spin(driver)
    except KeyboardInterrupt:
        pass
    finally:
        driver.shutdown()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
