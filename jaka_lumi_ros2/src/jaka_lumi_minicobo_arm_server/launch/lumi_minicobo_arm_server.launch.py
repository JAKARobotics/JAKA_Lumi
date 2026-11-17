import launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return LaunchDescription([
        # Declare 'ip' and 'model' arguments
        DeclareLaunchArgument('ip', default_value='192.168.10.90', description='IP address'),
        
        # Launch the 'lumi_minicobo_arm_server' node from the 'jaka_lumi_minicobo_arm_server' package
        Node(
            package='jaka_lumi_minicobo_arm_server',
            executable='lumi_minicobo_arm_server',  # the executable to run
            name='lumi_minicobo_arm_server',
            output='screen',
            parameters=[
                {'ip': LaunchConfiguration('ip')},  # Pass 'ip' parameter
            ],
        ),
    ])
