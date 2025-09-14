#!/usr/bin/env python3
"""
Test script for Inspire RH56 Hand Position Controller

This script demonstrates how to control the hand using the main position controller.
It sends direct position commands to all joints simultaneously.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import math


class HandPositionTest(Node):
    def __init__(self):
        super().__init__('hand_position_test')

        # Initialize shutdown flag
        self._shutdown_requested = False

        # Create publisher for the main hand position controller
        self.hand_publisher = self.create_publisher(
            Float64MultiArray,
            '/inspire_rh56_hand_joint_position_controller/commands',
            10
        )

        # Wait for connections
        self.get_logger().info('Waiting for hand position controller...')

        # Test patterns
        self.get_logger().info('Starting hand position test...')
        self.test_counter = 0
        self.timer = self.create_timer(2.0, self.run_test)

    def run_test(self):
        """Run different test patterns"""
        test_patterns = [
            self.test_hand_open,
            self.test_hand_close,
            self.test_pinch_gesture,
            self.test_finger_wave,
            self.test_partial_close,
            self.test_return_to_open,  # Return to open position at end
        ]

        if self.test_counter < len(test_patterns):
            pattern = test_patterns[self.test_counter]
            self.get_logger().info(f'Running test pattern: {pattern.__name__}')
            pattern()
            self.test_counter += 1
        else:
            self.get_logger().info('All test patterns completed. Stopping.')
            self.timer.cancel()
            # Trigger shutdown after a brief delay
            self.create_timer(1.0, self.shutdown_node)

    def send_hand_command(self, positions):
        """Send command to hand controller"""
        msg = Float64MultiArray()
        msg.data = positions
        self.hand_publisher.publish(msg)
        self.get_logger().info(f'Hand command: {positions}')

    def test_hand_open(self):
        """Test opening the entire hand"""
        # Order: thumb_yaw, thumb_pitch, index, middle, ring, pinky
        # All joints at minimum (open) position
        positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.send_hand_command(positions)

    def test_hand_close(self):
        """Test closing the entire hand"""
        # All fingers closed to maximum safe position
        # Thumb: moderate yaw and pitch for gripping
        # Fingers: near maximum for full closure
        positions = [1.0, 0.5, 1.4, 1.4, 1.4, 1.4]
        self.send_hand_command(positions)

    def test_pinch_gesture(self):
        """Test pinch gesture (thumb and index)"""
        # Thumb positioned for pinch, index closed, others open
        positions = [1.2, 0.4, 1.2, 0.0, 0.0, 0.0]
        self.send_hand_command(positions)

    def test_finger_wave(self):
        """Test finger wave pattern"""
        # Sequential finger movement pattern
        positions = [0.3, 0.2, 0.8, 1.2, 0.6, 0.3]
        self.send_hand_command(positions)

    def test_partial_close(self):
        """Test partial closing of all fingers"""
        # Half-closed position for all joints
        positions = [0.6, 0.3, 0.7, 0.7, 0.7, 0.7]
        self.send_hand_command(positions)

    def test_return_to_open(self):
        """Return hand to open position"""
        # Return all joints to open position
        positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.send_hand_command(positions)

    def shutdown_node(self):
        """Shutdown the node gracefully"""
        self.get_logger().info('Shutting down test node...')
        # Set a flag to trigger shutdown from main loop
        self._shutdown_requested = True


def main():
    rclpy.init()

    hand_test = HandPositionTest()

    try:
        while rclpy.ok() and not hand_test._shutdown_requested:
            rclpy.spin_once(hand_test, timeout_sec=0.1)
    except KeyboardInterrupt:
        hand_test.get_logger().info('Keyboard interrupt received')
    except Exception as e:
        hand_test.get_logger().error(f'Exception: {e}')
    finally:
        hand_test.get_logger().info('Cleaning up...')
        if rclpy.ok():
            hand_test.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()