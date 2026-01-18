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
    
    # Robot state publisher - publishes YOUR robot's URDF
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
    
    # Static transform: zed_camera_link to base_link
    # This connects the ZED's coordinate frame to your robot's coordinate frame
    # Adjust the xyz values to match where your ZED is mounted on the car
    static_tf_zed_to_base = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='zed_to_base_link',
        output='screen',
        emulate_tty=True,
        arguments=[
            '-0.15', '0', '-0.10',  # x y z (negative because going from camera to base)
            '0', '0', '0',           # roll pitch yaw
            'zed_camera_link',       # parent frame (published by ZED)
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
        SetEnvironmentVariable(name='RCUTILS_COLORIZED_OUTPUT', value='1'),
        zed_camera_launch,
        robot_state_publisher,
        static_tf_zed_to_base,
        cmd_vel_to_can,
        nav2_launch,
    ])


if __name__ == '__main__':
    generate_launch_description()