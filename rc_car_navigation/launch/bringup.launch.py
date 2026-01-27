import os
from ament_index_python.packages import get_package_share_directory
import launch
from launch.actions import SetEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    
    # Get package directories
    pkg_share = get_package_share_directory('rc_car_navigation')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    zed_wrapper_dir = get_package_share_directory('zed_wrapper')
    
    # File paths
    urdf_file = os.path.join(pkg_share, 'urdf', 'rc_car.urdf')
    nav2_params_file = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    
    # Read URDF file
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()
    
    # ZED camera launch
    zed_camera_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(zed_wrapper_dir, 'launch', 'zed_camera.launch.py')
        ),
        launch_arguments={
            'camera_model': 'zedm',
        }.items()
    )
    
    # Robot state publisher - publishes YOUR robot's URDF (base_link → base_footprint)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        emulate_tty=True,
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': False
        }]
    )
    
    # Static transform: odom to base_link
    # This connects base_link to the same odom frame that ZED uses
    # Adjust xyz to represent where your robot's base_link is relative to the ZED camera
    static_tf_odom_to_base = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='odom_to_base_link',
        output='screen',
        emulate_tty=True,
        arguments=[
            '0', '0', '0',           # x y z (adjust based on initial position)
            '0', '0', '0',           # roll pitch yaw
            'odom',                  # parent frame
            'base_link'              # child frame (your robot)
        ]
    )
    
    # CMD_VEL to CAN converter node
    cmd_vel_to_can = Node(
        package='rc_car_navigation',
        executable='cmd_vel_to_can',
        name='cmd_vel_to_can',
        output='screen',
        emulate_tty=True,
        parameters=[{'use_sim_time': False}]
    )
    
    # Nav2 navigation stack
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'params_file': nav2_params_file,
            'use_sim_time': 'false',
        }.items()
    )
    
    return launch.LaunchDescription([
        zed_camera_launch,
        robot_state_publisher,
        static_tf_odom_to_base,
        cmd_vel_to_can,
        nav2_launch,
    ])


if __name__ == '__main__':
    generate_launch_description()