#!/usr/bin/env python3
"""
transform_utils.py

Helper functions for building 4x4 transform matrices
from translation and Euler angles.
"""

# ── Standard library ────────────────────────────
import numpy as np


def make_transform(tx, ty, tz, roll, pitch, yaw):
    """
    Build a 4x4 homogeneous transform matrix.

    Args:
        tx, ty, tz       : translation in meters
        roll, pitch, yaw : rotation in radians

    Returns:
        4x4 numpy array
    """
    Rx = np.array([
        [1,             0,              0],
        [0,  np.cos(roll), -np.sin(roll)],
        [0,  np.sin(roll),  np.cos(roll)]
    ])

    Ry = np.array([
        [ np.cos(pitch), 0, np.sin(pitch)],
        [             0, 1,             0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])

    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw),  np.cos(yaw), 0],
        [          0,            0, 1]
    ])

    R = Rz @ Ry @ Rx

    T = np.eye(4)
    T[:3, :3] = R
    T[:3,  3] = [tx, ty, tz]

    return T


def apply_transform(xyz, T):
    """
    Apply a 4x4 transform to an (N, 3) array of points.

    Args:
        xyz : (N, 3) numpy array of XYZ points
        T   : 4x4 transform matrix

    Returns:
        (N, 3) transformed points
    """
    ones  = np.ones((len(xyz), 1))
    xyz_h = np.hstack([xyz, ones])
    return (T @ xyz_h.T).T[:, :3]


def extract_valid_xyz(pc_np):
    """
    Flatten and filter NaN/inf points from a (H, W, 4) point cloud.

    Args:
        pc_np : (H, W, 4) numpy array from ZED SDK

    Returns:
        (N, 3) array of valid XYZ points
    """
    xyz   = pc_np[..., :3].reshape(-1, 3)
    valid = np.isfinite(xyz).all(axis=1)
    return xyz[valid]