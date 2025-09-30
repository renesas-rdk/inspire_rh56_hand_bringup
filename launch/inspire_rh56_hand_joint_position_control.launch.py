#!/usr/bin/env python3
# ********************************************************************************************************************
# Copyright [2025] Renesas Electronics Corporation and/or its licensors. All Rights Reserved.
#
# The contents of this file (the "contents") are proprietary and confidential to Renesas Electronics Corporation
# and/or its licensors ("Renesas") and subject to statutory and contractual protections.
#
# Unless otherwise expressly agreed in writing between Renesas and you: 1) you may not use, copy, modify, distribute,
# display, or perform the contents; 2) you may not use any name or mark of Renesas for advertising or publicity
# purposes or in connection with your use of the contents; 3) RENESAS MAKES NO WARRANTY OR REPRESENTATIONS ABOUT THE
# SUITABILITY OF THE CONTENTS FOR ANY PURPOSE; THE CONTENTS ARE PROVIDED "AS IS" WITHOUT ANY EXPRESS OR IMPLIED
# WARRANTY, INCLUDING THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NON-INFRINGEMENT; AND 4) RENESAS SHALL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL, OR CONSEQUENTIAL DAMAGES,
# INCLUDING DAMAGES RESULTING FROM LOSS OF USE, DATA, OR PROJECTS, WHETHER IN AN ACTION OF CONTRACT OR TORT, ARISING
# OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE CONTENTS. Third-party contents included in this file may
# be subject to different terms.
# ********************************************************************************************************************

"""
Launch file for Inspire RH56 Hand with Joint Group Position Controller and Gripper Action Adapter

This launch file starts:
- ros2_control_node: Main controller manager for hardware interface
- robot_state_publisher: Publishes TF transforms from URDF
- joint_state_broadcaster: Publishes joint states from hardware
- joint_group_position_controller: Provides direct position commands for individual joints or groups
- hand_gripper_action_adapter: Converts gripper commands to hand joint positions
- foxglove_bridge: WebSocket bridge for Foxglove Studio visualization

Usage:
  # For physical hand with serial interface:
  ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_position_control.launch.py
  ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_position_control.launch.py serial_port:=/dev/ttyUSB1
  ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_position_control.launch.py hand_side:=right

  # For SIMULATION/TESTING without physical hand (RECOMMENDED for testing):
  ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_position_control.launch.py use_mock_hardware:=true

  # Use different gripper configurations:
  ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_position_control.launch.py gripper_mapping:=gripper_joint_mapping_2finger.yaml
  ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_position_control.launch.py gripper_mapping:=gripper_joint_mapping_3finger.yaml

  Then connect Foxglove Studio to ws://<foxglove_bridge_ip>:8765

Test position commands in another terminal with:
  # Direct joint control:
  ros2 topic pub -1 /inspire_rh56_hand_joint_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [1.3, 0.6, 0.0, 0.0, 1.4, 1.4]}"

  # Gripper command interface:
  ros2 topic pub -1 /gripper_command control_msgs/msg/GripperCommand "{position: 0.03, max_effort: 10.0}"
  ros2 action send_goal /gripper_cmd control_msgs/action/ParallelGripperCommand "{command: {position: [0.025], effort: [10.0]}}"

Or run the Python test script:
  python3 ros2_ws/install/inspire_rh56_hand_bringup/share/inspire_rh56_hand_bringup/test/test_hand_position.py

Observe the hand moving in Foxglove Studio.

NOTE: Use 'use_mock_hardware:=true' for simulation or safe testing without physical hardware!
"""

import os
from typing import List

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import FrontendLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs) -> List[Node]:
    """Setup function to evaluate launch configurations at runtime."""
    # Get launch configurations
    serial_port_value = LaunchConfiguration('serial_port').perform(context)
    baudrate_value = LaunchConfiguration('baudrate').perform(context)
    use_mock_hardware_value = LaunchConfiguration('use_mock_hardware').perform(context)
    hand_side_value = LaunchConfiguration('hand_side').perform(context)
    gripper_mapping_value = LaunchConfiguration('gripper_mapping').perform(context)

    # Get package directories
    pkg_share = get_package_share_directory('inspire_rh56_hand_bringup')

    # Select and process the appropriate XACRO file
    if hand_side_value == 'left':
        robot_description_xacro = os.path.join(
            pkg_share, 'urdf', 'inspire_rh56_hand_left.urdf.xacro'
        )
    else:
        robot_description_xacro = os.path.join(
            pkg_share, 'urdf', 'inspire_rh56_hand_right.urdf.xacro'
        )

    # Process XACRO file with parameters
    robot_description_raw = xacro.process_file(
        robot_description_xacro,
        mappings={
            'serial_port': serial_port_value,
            'baudrate': baudrate_value,
            'use_mock_hardware': use_mock_hardware_value
        }
    ).toxml()

    robot_description = {'robot_description': robot_description_raw}

    # Controller configurations
    controller_config = os.path.join(
        pkg_share, 'config', 'controller_manager.yaml'
    )

    position_controller_config = os.path.join(
        pkg_share, 'config', 'inspire_rh56_hand_joint_position_controller.yaml'
    )

    # Foxglove bridge launch file
    foxglove_bridge_launch = os.path.join(
        get_package_share_directory('foxglove_bridge'),
        'launch',
        'foxglove_bridge_launch.xml'
    )

    # Nodes
    nodes: List[Node] = [
        # Controller manager
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            name='controller_manager',
            output='screen',
            parameters=[
                robot_description,
                controller_config,
                position_controller_config
            ],
            remappings=[
                ('/controller_manager/robot_description', '/robot_description'),
            ],
        ),
        # Robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[robot_description],
        ),
        # Joint state broadcaster (always start)
        Node(
            package='controller_manager',
            executable='spawner',
            name='joint_state_broadcaster_spawner',
            output='screen',
            arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        ),
        # Hand position controller
        Node(
            package='controller_manager',
            executable='spawner',
            name='position_controller_spawner',
            output='screen',
            arguments=[
                'inspire_rh56_hand_joint_position_controller',
                '--controller-manager', '/controller_manager',
            ],
        ),
        # Hand gripper action adapter for gripper command interface
        Node(
            package='inspire_rh56_hand_utils',
            executable='hand_gripper_action_adapter',
            name='hand_gripper_action_adapter',
            output='screen',
            parameters=[
                {
                    'action_server_name': 'gripper_cmd',
                    'gripper_command_topic': 'gripper_command',
                    'position_controller_topic': '/inspire_rh56_hand_joint_position_controller/commands',
                    'mapping_config_file': gripper_mapping_value,
                    'execution_duration': 2.0,
                }
            ],
        ),
        # Foxglove bridge for web-based visualization
        IncludeLaunchDescription(
            FrontendLaunchDescriptionSource(foxglove_bridge_launch)
        ),
    ]

    return nodes


def generate_launch_description() -> LaunchDescription:
    """Generate launch description for Inspire RH56 Hand with joint group position control."""
    # Declare arguments
    serial_port_arg = DeclareLaunchArgument(
        'serial_port',
        default_value='/dev/ttyUSB0',
        description='Serial port for hand communication'
    )

    baudrate_arg = DeclareLaunchArgument(
        'baudrate',
        default_value='115200',
        description='Baudrate for serial communication'
    )

    use_mock_hardware_arg = DeclareLaunchArgument(
        'use_mock_hardware',
        default_value='false',
        description='Use mock hardware for testing (true/false)'
    )

    hand_side_arg = DeclareLaunchArgument(
        'hand_side',
        default_value='left',
        description='Which hand to control: left or right'
    )

    gripper_mapping_arg = DeclareLaunchArgument(
        'gripper_mapping',
        default_value='gripper_joint_mapping_3finger.yaml',
        description='Gripper mapping configuration: gripper_joint_mapping_3finger.yaml or gripper_joint_mapping_2finger.yaml'
    )

    return LaunchDescription([
        serial_port_arg,
        baudrate_arg,
        use_mock_hardware_arg,
        hand_side_arg,
        gripper_mapping_arg,
        OpaqueFunction(function=launch_setup)
    ])