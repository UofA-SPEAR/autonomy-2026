#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'ackermann_nav'
    pkg_share = get_package_share_directory(pkg_name)
    
    urdf_file = os.path.join(pkg_share, 'urdf', 'ackermann_stereo.urdf')
    
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()
    
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': False
        }]
    )
    
    static_tf_camera = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera_to_base_link',
        arguments=['0.45', '0', '0.3', '0', '0', '0', 'base_link', 'camera_link']
    )
    
    pointcloud_to_laserscan = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        remappings=[
            ('cloud_in', '/zed/zed_node/point_cloud/cloud_registered'),
            ('scan', '/scan')
        ],
        parameters=[{
            'target_frame': 'camera_link',
            'transform_tolerance': 0.01,
            'min_height': -0.5,
            'max_height': 2.0,
            'angle_min': -1.5708,
            'angle_max': 1.5708,
            'angle_increment': 0.0087,
            'scan_time': 0.1,
            'range_min': 0.3,
            'range_max': 20.0,
            'use_inf': True,
            'inf_epsilon': 1.0,
            'concurrency_level': 1
        }]
    )
    
    ekf_config = os.path.join(pkg_share, 'config', 'ekf.yaml')
    robot_localization = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config, {'use_sim_time': False}]
    )
    
    return LaunchDescription([
        robot_state_publisher,
        static_tf_camera,
        pointcloud_to_laserscan,
        robot_localization
    ])
