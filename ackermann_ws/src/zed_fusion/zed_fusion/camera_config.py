#!/usr/bin/env python3
"""
camera_config.py

Hardware info and mounting positions for all ZED cameras
on the ackermann platform. Add new cameras here only.
"""

# ── Standard library ────────────────────────────
import numpy as np

# ── Third party ─────────────────────────────────
import pyzed.sl as sl

from zed_fusion.camera_information import CAM_SERIAL_NO

# ── Stream presets ───────────────────────────────
class STREAM:
    LOW  = (sl.RESOLUTION.VGA,   15)
    MED  = (sl.RESOLUTION.HD720, 15)
    HIGH = (sl.RESOLUTION.HD2K,  15)


# ── Camera hardware ──────────────────────────────
class CameraInfo:
    def __init__(self, name, model, resolution, fps):
        self.name       = name
        self.model      = model
        self.serial     = CAM_SERIAL_NO[name]
        self.resolution = resolution
        self.fps        = fps

    def set_stream(self, resolution, fps):
        self.resolution = resolution
        self.fps        = fps
        return self


CAMERAS = [
    CameraInfo("zed_front", "zed2i", sl.RESOLUTION.HD2K, 15),
    CameraInfo("zed_back",  "zedm", sl.RESOLUTION.HD2K, 15),
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


class POSES:
    FRONT = Pose(0.0,     0.0,  0.0,  0.0, 0.0,   0.0)
    BACK  = Pose(-0.0127, 0.0, -1.1,  0.0, np.pi, 0.0)