from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='jaka_lumi_body_node',
            executable='lumi_body_node',
            name='lumi_body_node',
            output='screen'
        )
    ])
