import rclpy
from rclpy.node import Node
from std_msgs.msg import *
from sensor_msgs.msg import JointState
from std_srvs.srv import SetBool
from transitions import Machine, State
from k1_msgs.srv import JointMove
import time

class StateMachineNode(Node):

    states = ['DEFAULT', 'OPERATIONAL']

    def __init__(self):
        super().__init__('state_machine_node')
        self.machine = Machine(model=self, states=StateMachineNode.states, initial='DEFAULT')
        self.machine.add_transition(trigger='to_operational', source='DEFAULT', dest='OPERATIONAL', after='activate_services')
        self.machine.add_transition(trigger='to_default', source='OPERATIONAL', before='move_to_default_pose', dest='DEFAULT', after='deactivate_all_services')
        self.machine.add_transition(trigger='shutdown', source='*', dest='DEFAULT', before='deactivate_all_services', after='node_shutdown')


        # force mode service requires start in advance
        self.pre_service_clients = {
            'start_force_control_mode_enable': self.create_client(SetBool, '/force_control_mode_enable'),
        }


        # Initialize service service_clients for nodes A-D
        self.service_clients = {
            'start_arm_servo_mode': self.create_client(SetBool, '/right_arm/servo_move_enable'),
            'start_arm_vr_robot_pose_converter': self.create_client(SetBool, '/right_arm/vr_robot_pose_converter'),
            # 'start_right_arm_servo_mode': self.create_client(SetBool, '/right_arm/servo_move_enable'),
            # 'start_right_arm_vr_robot_pose_converter': self.create_client(SetBool, '/right_arm/vr_robot_pose_converter'),
            # 'B': self.create_client(SetBool, '/node_B/set_bool'),
            # 'C': self.create_client(SetBool, '/node_C/set_bool'),
            # 'D': self.create_client(SetBool, '/node_D/set_bool')
        }

        # Initialize service service_clients for nodes E and F
        self.special_service_clients = {
            'start_recording': self.create_client(SetBool, 'start_recording'),
            'save_data': self.create_client(SetBool, 'save_data'),
        }

        #self.publisher_left_command_gripper_val = self.create_publisher(JointState, 'left_gripper/set_pos', 10)
        self.publisher_command_gripper_val = self.create_publisher(JointState, 'right_gripper/set_pos', 10)
        # self.publisher_left_command_gripper_val = self.create_publisher(Int32, 'left_gripper/set_pos', 10)
        #self.publisher_right_command_gripper_val = self.create_publisher(JointState, 'right_gripper/set_pos', 10)

        self.arm_joint_move_client = self.create_client(JointMove, 'joint_move')
        # self.right_arm_joint_move_client = self.create_client(JointMove, 'right_arm/joint_move')


        self.subscriptions_list = [
            # self.create_subscription(String, '/vr_left_side_button', lambda msg: self.to_operational() if msg.data == 'LG=T' else None, 10),
            # self.create_subscription(String, '/vr_right_side_button', lambda msg: self.to_operational() if msg.data == 'RG=T' else None, 10),
            # self.create_subscription(String, '/vr_b_button', lambda msg: self.to_default() if msg.data == 'B=T' else None, 10),
            # self.create_subscription(String, '/vr_y_button', lambda msg: self.shutdown() if msg.data == 'Y=T' else None, 10),
            # self.create_subscription(String, '/vr_x_button', self.x_button_callback, 10),  # X button callback
            # self.create_subscription(String, '/vr_a_button', self.a_button_callback, 10)   # A button callback
            self.create_subscription(String, '/vr_left_side_button', self.left_side_button_callback, 10),
            self.create_subscription(String, '/vr_right_side_button', self.right_side_button_callback, 10),
            self.create_subscription(String, '/vr_left_front_button', self.left_front_button_callback, 10),
            self.create_subscription(String, '/vr_right_front_button', self.right_front_button_callback, 10),
            self.create_subscription(String, '/vr_b_button', self.b_button_callback, 10),
            self.create_subscription(String, '/vr_y_button', self.y_button_callback, 10),
            self.create_subscription(String, '/vr_x_button', self.x_button_callback, 10),  # X button callback
            self.create_subscription(String, '/vr_a_button', self.a_button_callback, 10)   # A button callback
        ]
        
        self.get_logger().info('State machine node has been started.')

    def activate_services(self):
        self.get_logger().info('Activating services.')

        for client in self.service_clients.values():
            if client.service_is_ready():
                request = SetBool.Request()
                request.data = True
                future = client.call_async(request)

    def move_to_default_pose(self):
        request = SetBool.Request()
        request.data = False
        future = self.service_clients["start_arm_servo_mode"].call_async(request)
        
        time.sleep(0.1)
        
        for client in self.pre_service_clients.values():
            if client.service_is_ready():
                request = SetBool.Request()
                request.data = True
                future = client.call_async(request)

        time.sleep(1)

        self.get_logger().info('Move to default pose.')
        request = JointMove.Request()
        request.move_mode = 0 # absolute move
        request.is_blocking = False
        request.speed = 1.0
        # left arm value
        # request.joint_positions = [-1.359192608283104, -0.9613273519984766, 2.034198696491911, 
                                #   -1.481068949949868, 0.3909188458616899, -0.9122486934323962, 0.382808040271289,
                                #   -2.03533306109991, 1.05267788504786, 1.556727709524621, -1.5725765626319308,
                                #    -0.5133885994741321, 1.0164448497764575, 0.507399053106668]
        # building E demo horizon
        # request.joint_positions = [0.25576054858724906,-1.3941690064930703,-4.929490486040264,
        #                            -1.2750153784594176, -0.27841492227813547, 1.386524464369335,1.8050020591200155,
        #                            -3.470377778080485,1.3798224000416772,1.572506749461851,
        #                            -1.3929821826017144,-2.963062924403293,1.5340745993329359,1.728312291787385]
        
        # E demo vertical
        request.joint_positions = [0.31834805013333334
,-1.4057579687466666
,-0.8645662835200001
,-0.29656634144000005
,-1.3688966155733333,
-0.0
]
   
        future = self.arm_joint_move_client.call_async(request)


    def deactivate_services(self, service_clients=None):
        if service_clients is None:
            service_clients = self.service_clients.values()

        self.get_logger().info('Deactivating services.')
        for client in service_clients:
            if client.service_is_ready():
                request = SetBool.Request()
                request.data = False
                future = client.call_async(request)

    def deactivate_all_services(self):
        self.get_logger().info('stop all services.')
        self.deactivate_services(list(self.service_clients.values()) + list(self.special_service_clients.values()))
    
    def left_side_button_callback(self, msg):
        if msg.data == 'LG=T' and self.state != 'OPERATIONAL':
            self.get_logger().info('left trans to operational.')
            self.to_operational()

    def right_side_button_callback(self, msg):
        if msg.data == 'RG=T' and self.state != 'OPERATIONAL':
            self.get_logger().info('right trans to operational.')
            self.to_operational()

    def left_front_button_callback(self, msg):
        if self.state == 'OPERATIONAL':
            current_time = self.get_clock().now().to_msg()
            #msg_gripper = Int32()
            msg_gripper = JointState()
            msg_gripper.header.stamp = current_time
            if msg.data == 'LT=T':
                msg_gripper.position= [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                #msg_gripper.data = 0
                self.publisher_command_gripper_val.publish(msg_gripper)
                self.get_logger().info('invoke gripper close')
            if msg.data == 'LT=F':
                msg_gripper.position= [0.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                #msg_gripper.data = 500
                self.publisher_command_gripper_val.publish(msg_gripper)
                self.get_logger().info('invoke gripper open.')

    def right_front_button_callback(self, msg):
        if self.state == 'OPERATIONAL':
            current_time = self.get_clock().now().to_msg()
            #msg_gripper = Int32()
            msg_gripper = JointState()
            msg_gripper.header.stamp = current_time
            if msg.data == 'RT=T':
                msg_gripper.position= [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                #msg_gripper.data = 0
                self.publisher_command_gripper_val.publish(msg_gripper)
                self.get_logger().info('invoke right gripper close')
            if msg.data == 'RT=F':
                msg_gripper.position= [0.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                #msg_gripper.data = 500
                self.publisher_command_gripper_val.publish(msg_gripper)
                self.get_logger().info('invoke right gripper open.')

    def b_button_callback(self, msg):
        if self.state != 'DEFAULT' and msg.data == 'B=T':
            self.get_logger().info('trans to default.')
            self.to_default()

    def y_button_callback(self, msg):
        if msg.data == 'Y=T':
            self.get_logger().info('shutdown node.')
            self.shutdown()

    def x_button_callback(self, msg):
        if self.state == 'OPERATIONAL' and msg.data == 'X=T':
            self.get_logger().info('call service record.')
            self.call_service('start_recording')

    def a_button_callback(self, msg):
        if self.state == 'OPERATIONAL' and msg.data == 'A=T':
            self.get_logger().info('call service write to disk.')
            self.call_service('save_data')

    def call_service(self, service_name):
        if service_name in self.special_service_clients and self.special_service_clients[service_name].service_is_ready():
            request = SetBool.Request()
            request.data = True
            future = self.special_service_clients[service_name].call_async(request)

    def node_shutdown(self):
        self.get_logger().info('Shutting down the node.')
        self.destroy_node()
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    state_machine_node = StateMachineNode()
    try:
        rclpy.spin(state_machine_node)
    except KeyboardInterrupt:
        pass
    finally:
        # Ensure that the node is properly shut down even on keyboard interrupt
        state_machine_node.shutdown()

if __name__ == '__main__':
    main()
