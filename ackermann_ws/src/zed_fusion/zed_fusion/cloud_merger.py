#!/usr/bin/env python3
"""
cloud_merger.py

ROS2 node that subscribes to both ZED point cloud topics,
applies the back camera transform, merges the clouds,
and publishes to /merged/cloud.
"""

# ── Standard library ────────────────────────────
import numpy as np

# ── ROS2 ────────────────────────────────────────
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
import sensor_msgs_py.point_cloud2 as pc2

# ── Local ────────────────────────────────────────
from zed_fusion.camera_config import CAMERAS, POSES
from zed_fusion.transform_utils import make_transform, apply_transform, extract_valid_xyz


class CloudMerger(Node):

    def __init__(self):
        super().__init__('cloud_merger')

        # build transform from back camera to front camera
        p = POSES.BACK
        self.T = make_transform(p.tx, p.ty, p.tz, p.roll, p.pitch, p.yaw)

        # point cloud storage
        self.cloud_front = None
        self.cloud_back  = None

        # ── Subscribers ──────────────────────────
        self.sub_front = self.create_subscription(
            PointCloud2,
            '/zed_front/zed_node/point_cloud/cloud_registered',
            self.cb_front,
            10
        )
        self.sub_back = self.create_subscription(
            PointCloud2,
            '/zed_back/zed_node/point_cloud/cloud_registered',
            self.cb_back,
            10
        )

        # ── Publisher ────────────────────────────
        self.pub = self.create_publisher(
            PointCloud2,
            '/merged/cloud',
            10
        )

        self.get_logger().info('Cloud merger node started')


    def cb_front(self, msg):
        self.cloud_front = msg
        self.merge()


    def cb_back(self, msg):
        self.cloud_back = msg
        self.merge()


    def merge(self):
        # wait until both clouds have arrived
        if self.cloud_front is None or self.cloud_back is None:
            return

        # convert ROS messages to numpy
        front_pts = np.array(list(pc2.read_points(
            self.cloud_front, field_names=('x', 'y', 'z'), skip_nans=True
        )))
        back_pts  = np.array(list(pc2.read_points(
            self.cloud_back,  field_names=('x', 'y', 'z'), skip_nans=True
        )))

        if len(front_pts) == 0 or len(back_pts) == 0:
            return

        # transform back camera points into front camera frame
        back_transformed = apply_transform(back_pts, self.T)

        # merge
        merged = np.vstack([front_pts, back_transformed])

        # publish
        header          = Header()
        header.stamp    = self.get_clock().now().to_msg()
        header.frame_id = 'zed_front_camera_left_optical_frame'

        msg = pc2.create_cloud_xyz32(header, merged.tolist())
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CloudMerger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()