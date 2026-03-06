'''
Initializes the ZED 2i (front) and ZED-M (back) cameras on the ackermann platform.
Loads per-camera configs, assigns unique namespaces, and publishes point cloud,
depth, and IMU topics for the fusion and EKF localization pipeline.

Date: MAR 5, 2026
'''
import pyzed.sl as sl

# --- Serial Numbers --- (rmb to update later)
SN_CAM1 = 12345678   # ZED 2i  (front)
SN_CAM2 = 87654321   # ZED-M   (back)

init_params = sl.InitParameters()
init_params.depth_mode = sl.DEPTH_MODE.ULTRA
init_params.coordinate_units = sl.UNIT.METER

zed1 = sl.Camera()
zed2 = sl.Camera()

# Open by serial number to avoid confusion
init_params.input.set_from_serial_number(SN_CAM1)
zed1.open(init_params)

init_params.input.set_from_serial_number(SN_CAM2)
zed2.open(init_params)