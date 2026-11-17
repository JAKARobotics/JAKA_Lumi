from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='jaka_lumi_body_server',
            executable='lumi_body_server',
            name='lumi_body_server',
            output='screen'
        )
    ])
