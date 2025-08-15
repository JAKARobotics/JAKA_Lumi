from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='vr_data_pub',
            executable='vr_data_pub',
            parameters=[{'server_port': 9852}],  # 设置robot_ip参数
            name='vr_socket_server'
        ),
        Node(
            package='vr_data_pub',
            executable='vr_data_distributer',
            name='vr_data_distributor'
        ),
        Node(
            package='k1_robot',
            namespace='/right_arm',
            parameters=[{'robot_ip': '172.30.95.49','robot_running_mode':'act'}],  #teleop or act_exe or test
            executable='robot_interface',
            name='robot_interface'
        ),   
        # Node(
        #     package='jakazu_body_control',
        #     # namespace='/left_arm',
        #     parameters=[{'robot_ip': '172.30.95.93'}],  # 设置robot_ip参数,  index 0 for left arm
        #     executable='jakazu_body_control',
        #     name='jakazu_body_control'
        # ),
        # Node(
        #     package='k1_robot',
        #     # namespace='/left_arm',
        #     executable='control_gripper',
        #     name='control_gripper'
        # ),
#        Node(
#            package='robohub',
#            namespace='/right_arm',
#            parameters=[{'robot_ip': '172.30.95.233'},{'robot_arm_index': 1}],  # 设置robot_ip参数,  index 1 for right arm
#            executable='jaka_driver_node',
#            name='jaka_robot_driver'
#        ),
        # Node(
        #     package='vr_data_pub',
        #     #namespace='/left_arm',
        #     parameters = [{'robot_name':'left'}],
        #     executable='vr_robot_pose_converter_30degree_servo_p',
        #     name='vr_robot_pose_converter'
        # ),
        
        Node(
            package='vr_data_pub',
            namespace='/right_arm',
            parameters=[{'robot_name': 'arm'}],
            executable='vr_robot_pose_converter_lumi_servo_p',
            name='vr_robot_pose_converter'
        )#,


        # can not exit automatically, use terminal now
#        Node(
#            package='vr_data_pub',
#            executable='teleoperation_control',
#            name='vr_state_machine_node'
#        ),
        # remap topic template
#        Node(
#            package='turtlesim',
#            executable='mimic',
#            name='mimic',
#            remappings=[
#                ('/input/pose', '/turtlesim1/turtle1/pose'),
#                ('/output/cmd_vel', '/turtlesim2/turtle1/cmd_vel'),
#            ]
#        )
    ])
