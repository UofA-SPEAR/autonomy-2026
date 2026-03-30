#!/usr/bin/env python3
"""
zed_cameras.launch.py

Initializes the ZED 2i (front) and ZED-M (back) cameras on the ackermann platform.
Loads per-camera configs, assigns unique namespaces, and publishes point cloud,
depth, and IMU topics for the fusion and EKF localization pipeline.

Usage:
    ros2 launch zed_fusion zed_cameras.launch.py
"""

# ── Standard library ────────────────────────────
import sys
import os

# ── ROS2 ────────────────────────────────────────
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

# ── Local ────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'zed_fusion'))
from zed_fusion.camera_config import CAMERAS, POSES, STREAM


def generate_launch_description():

    zed_share = get_package_share_directory('zed_wrapper')
    nodes = []

    for cfg in CAMERAS:

        # ZED camera node
        zed_node = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                zed_share + '/launch/zed_camera.launch.py'
            ),
            launch_arguments={
                'camera_model':  cfg.model,
                'camera_name':   cfg.name,
                'serial_number': str(cfg.serial),
            }.items()
        )
        nodes.append(zed_node)

        # Static TF (skip front — it's the reference frame)
        if cfg.name != 'zed_front':
            pose = getattr(POSES, cfg.name.split('_')[1].upper())
            tf_node = Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                name=f"{cfg.name}_tf",
                arguments=[
                    str(pose.tx), str(pose.ty), str(pose.tz),
                    str(pose.roll), str(pose.pitch), str(pose.yaw),
                    'zed_front_camera_left_optical_frame',
                    f"{cfg.name}_camera_left_optical_frame"
                ]
            )
            nodes.append(tf_node)

    return LaunchDescription(nodes)