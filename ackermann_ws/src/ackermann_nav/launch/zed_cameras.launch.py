#!/usr/bin/env python3
'''
Initializes the ZED 2i (front) and ZED-M (back) cameras on the ackermann platform.
Loads per-camera configs, assigns unique namespaces, and publishes point cloud,
depth, and IMU topics for the fusion and EKF localization pipeline.

Date: MAR 5, 2026
'''

from launch_ros.actions import Node                             # for Transform (TF)

import camera_config as 

init_params = sl.InitParameters()
init_params.depth_mode = sl.DEPTH_MODE.ULTRA
init_params.coordinate_units = sl.UNIT.METER

zed1 = sl.Camera()
zed2 = sl.Camera()

# Open by serial number to avoid confusion
init_params.input.set_from_serial_number(SN.SN_CAM1)
zed1.open(init_params)

init_params.input.set_from_serial_number(SN.SN_CAM2)
zed2.open(init_params)

static_tf = Node(
    package='tf2_ros',
    executable='static_transform_publisher',
    name='zed_back_to_front_tf',
    arguments=[
        '0', '0', '-0.3',                                       # x y z (meters) — back cam is 0.3m behind front
        '0', '3.14159', '0',                                    # roll pitch yaw — 180° rotation facing backward
        'zed_front_camera_center',
        'zed_back_camera_center'
    ]
)

T_back_to_front = make_transform(
    tx=0.0,
    ty=0.0,
    tz=-1.1,     # 1.1m behind front camera
    roll=0.0,
    pitch=np.pi, # 180° facing backward
    yaw=0.0

    T_back_to_front = make_transform(
    tx=0.0,
    ty=0.0,
    tz=-1.1,     # 1.1m behind front camera
    roll=0.0,
    pitch=np.pi, # 180° facing backward
    yaw=0.0
)
)
