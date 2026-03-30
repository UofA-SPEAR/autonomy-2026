#!/usr/bin/env python3
"""
fusion.launch.py

Launches the point cloud fusion node.
Run after zed_cameras.launch.py.

Usage:
    ros2 launch zed_fusion fusion.launch.py
"""

# ── ROS2 ────────────────────────────────────────
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='zed_fusion',
            executable='cloud_merger',
            name='cloud_merger',
            output='screen',
        )
    ])