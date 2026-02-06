import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import can
import struct
from can.message import Message
import math

class RCCarCanDrive(Node):
    def __init__(self):
        super().__init__('rc_car_can_drive')
        
        # Subscribe to velocity commands
        self.cmd_vel_sub = self.create_subscription(
            Twist, 
            '/cmd_vel', 
            self.cmd_vel_callback, 
            10
        )
        
        # Timer to send commands at regular intervals
        self.timer = self.create_timer(0.1, self.send_commands)
        
        # Initialize CAN bus
        self.bus = can.interface.Bus(interface='socketcan', channel='can0', bitrate=1000000)
        
        # Motor CAN IDs
        self.DRIVE_MOTOR_ID = 0x11
        self.STEERING_MOTOR_ID = 0x12
        
        # Current command values
        self.velocity = 0.0  # m/s
        self.steering_angle = 0.0  # radians
        
        # Limits
        self.max_velocity = 0.3  # m/s - adjust for your RC car
        self.max_steering_angle = 0.6  # radians (~34 degrees) - adjust for your RC car

    def cmd_vel_callback(self, msg):
        # Store velocity command
        self.velocity = max(-self.max_velocity, min(self.max_velocity, msg.linear.x))
        
        # Convert angular velocity to steering angle
        # For an RC car, angular velocity relates to steering angle
        # This is a simple proportional relationship - adjust the factor as needed
        steering_factor = 0.5  # Adjust this based on your car's behavior
        self.steering_angle = max(-self.max_steering_angle, 
                                   min(self.max_steering_angle, 
                                       msg.angular.z * steering_factor))

    def send_commands(self):
        # Send drive command
        drive_msg = self.create_drive_command(self.DRIVE_MOTOR_ID, self.velocity)
        self.bus.send(drive_msg)
        
        # Send steering command
        steering_msg = self.create_steering_command(self.STEERING_MOTOR_ID, self.steering_angle * -1.0)
        self.bus.send(steering_msg)

    def create_drive_command(self, actuator_id, velocity):
        # Construct arbitration ID
        priority = 0x0
        command_id = 0x03  # Drive command
        receiver_node_id = actuator_id
        sender_node_id = 1
        arbitration_id = priority << 24 | command_id << 16 | receiver_node_id << 8 | sender_node_id
        
        # Convert m/s to RPM
        wheel_diameter = 0.10  # 10cm wheels - ADJUST FOR YOUR CAR
        wheel_circumference = 3.14159 * wheel_diameter
        
        rpm = (abs(velocity) * .05) / wheel_circumference
        if velocity < 0:
            rpm = -rpm
        
        data = struct.pack(">f", velocity)
        
        # Create and return CAN message
        message = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=True)
        return message

    def create_steering_command(self, actuator_id, angle):
        # Construct arbitration ID
        priority = 0x0
        command_id = 0x02  # Steering command
        receiver_node_id = actuator_id
        sender_node_id = 1
        arbitration_id = priority << 24 | command_id << 16 | receiver_node_id << 8 | sender_node_id
        
        
        # Pack angle data as float32
        # The -50 multiplier is from the rover code - adjust if needed for your hardware
        data = struct.pack(">f", angle * 10)
        
        # Create and return CAN message
        message = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=True)
        return message

def main(args=None):
    rclpy.init(args=args)
    rc_car_node = RCCarCanDrive()
    rclpy.spin(rc_car_node)
    rc_car_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()