#!/usr/bin/env python3
"""
Test script for Inspire RH56 Hand Joint Trajectory Controller

This script demonstrates how to control the hand using the joint trajectory controller.
It sends predefined trajectories to open and close the hand.
"""

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import math


class HandTrajectoryTest(Node):
    def __init__(self):
        super().__init__('hand_trajectory_test')

        # Initialize shutdown flag
        self._shutdown_requested = False

        # Create publisher for joint trajectories
        self.trajectory_publisher = self.create_publisher(
            JointTrajectory,
            '/inspire_rh56_hand_joint_trajectory_controller/joint_trajectory',
            10
        )

        # Wait for connections
        self.get_logger().info('Waiting for trajectory controller...')
        while self.trajectory_publisher.get_subscription_count() == 0:
            self.get_logger().info('Waiting for trajectory controller to connect...', throttle_duration_sec=1.0)
            rclpy.spin_once(self, timeout_sec=0.1)

        # Define joint names
        self.joint_names = [
            'thumb_proximal_yaw_joint',
            'thumb_proximal_pitch_joint',
            'index_proximal_joint',
            'middle_proximal_joint',
            'ring_proximal_joint',
            'pinky_proximal_joint'
        ]

        # Test patterns
        self.get_logger().info('Starting hand trajectory test...')
        self.test_counter = 0
        self.timer = self.create_timer(4.0, self.run_test)  # Increased to 4 seconds for trajectory completion

    def run_test(self):
        """Run different test patterns"""
        test_patterns = [
            self.open_hand,
            self.close_hand,
            self.pinch_gesture,
            self.point_gesture,
            self.wave_gesture,
            self.return_to_open,  # Return to open position at end
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

    def send_trajectory(self, positions, duration_sec=1.0):
        """Send a trajectory to the hand"""
        trajectory = JointTrajectory()
        trajectory.header.stamp = self.get_clock().now().to_msg()
        trajectory.joint_names = self.joint_names

        # Create trajectory point
        point = JointTrajectoryPoint()
        point.positions = positions
        point.velocities = [0.0] * len(positions)
        point.time_from_start = Duration(sec=int(duration_sec), nanosec=int((duration_sec % 1) * 1e9))

        trajectory.points = [point]

        self.trajectory_publisher.publish(trajectory)
        self.get_logger().info(f'Sent trajectory: {positions}')

    def open_hand(self):
        """Open all fingers"""
        positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.send_trajectory(positions)

    def close_hand(self):
        """Close all fingers"""
        # All fingers closed to maximum safe position for proper closing
        positions = [1.0, 0.5, 1.4, 1.4, 1.4, 1.4]
        self.send_trajectory(positions)

    def pinch_gesture(self):
        """Pinch gesture - thumb and index finger"""
        # Better thumb positioning for pinch
        positions = [1.2, 0.4, 1.2, 0.0, 0.0, 0.0]
        self.send_trajectory(positions)

    def point_gesture(self):
        """Pointing gesture - index finger extended"""
        # Close all but index finger
        positions = [0.8, 0.3, 0.0, 1.2, 1.2, 1.2]
        self.send_trajectory(positions)

    def wave_gesture(self):
        """Wave gesture - sequential finger movement"""
        # Create a more interesting wave pattern
        positions = [0.3, 0.2, 0.8, 1.2, 0.6, 0.3]
        self.send_trajectory(positions, 2.0)

    def return_to_open(self):
        """Return hand to open position"""
        # Return all joints to open position
        positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.send_trajectory(positions)

    def shutdown_node(self):
        """Shutdown the node gracefully"""
        self.get_logger().info('Shutting down test node...')
        # Set a flag to trigger shutdown from main loop
        self._shutdown_requested = True


def main():
    rclpy.init()

    hand_test = HandTrajectoryTest()

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