#!/usr/bin/env python3
"""
Hardware info and mounting positions for all ZED cameras
on the ackermann platform. Add new cameras here only.

Version 1.0

"""
import numpy as np
import pyzed.sl as sl

from zed_fusion.camera_information import CAM_SERIAL_NO

# ── Stream presets ───────────────────────────────
class STREAM:
    LOW  = (sl.RESOLUTION.VGA,   15)
    MED  = (sl.RESOLUTION.HD720, 15)
    HIGH = (sl.RESOLUTION.HD2K,  15)


# ── Camera hardware ──────────────────────────────
class CameraInfo:
    def __init__(self, name, resolution=sl.RESOLUTION.HD2K, fps=15):
        self.name       = name
        self.model      = CAM_SERIAL_NO[name]["model"]
        self.serial     = CAM_SERIAL_NO[name]["SN"]
        self.resolution = resolution
        self.fps        = fps

    def set_stream(self, resolution, fps):
        self.resolution = resolution
        self.fps        = fps
        return self


CAMERAS = [
    CameraInfo("zed_front"),
    CameraInfo("zed_back"),
]


# ── Camera positions (relative to zed_front) ────
class Pose:
    def __init__(self, tx, ty, tz, roll, pitch, yaw):
        self.tx    = tx
        self.ty    = ty
        self.tz    = tz
        self.roll  = roll
        self.pitch = pitch
        self.yaw   = yaw

    def set_reference_pt(position):
        pass

    def set_cam_pos(self, tx=0.0, ty=0.0, tz=0.0):
        self.tx = tx
        self.ty = ty
        self.tz = tz

    def set_cam_ang(self, roll=0.0, pitch=0.0, yaw=0.0):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw


class POSES:
    FRONT = Pose(0.0,     0.0,  0.0,  0.0, 0.0,   0.0)
    BACK  = Pose(-0.0127, 0.0, -1.1,  0.0, np.pi, 0.0)