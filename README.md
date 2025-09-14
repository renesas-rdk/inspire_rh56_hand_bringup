# inspire_rh56_hand_bringup

ROS 2 package that provides launch files, controller configurations, robot descriptions, and test scripts for the Inspire RH56 6-DOF dexterous hand. This package contains everything needed to bring up and operate the hand.

## Features
- Launch files for different control modes (joint position, joint trajectory)
- Controller configurations for all supported control modes
- Complete hand URDF descriptions (left and right hand configurations)
- Test scripts for validating hand functionality
- Foxglove Studio configuration for visualization

## Related Packages
- **inspire_rh56_hand_ros2_control**: Contains the hardware interface implementation for serial communication
- **inspire_rh56_hand_description**: Contains the hand's visual and collision meshes, joint definitions

## Package layout
- `launch/`: Launch files for different control modes
- `config/`: Controller and controller_manager YAML configurations
- `urdf/`: Complete hand URDF descriptions (left and right)
- `test/`: Example scripts for testing hand functionality

## Prerequisites
- ROS 2 (Jazzy or newer) with `ros2_control` and `ros2_controllers` ecosystem
- A colcon workspace (e.g., `~/ros2_ws`)
- `inspire_rh56_hand_ros2_control` package for hardware interface
- `inspire_rh56_hand_description` package for hand description

## Launch Modes

### Joint Position Control
Provides direct joint position command interface:
```bash
ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_position_control.launch.py
```

### Joint Trajectory Control
Provides FollowJointTrajectory action interface for smooth trajectory execution:
```bash
ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_trajectory_control.launch.py
```

## Launch Arguments
All launch files support the following arguments:
- `serial_port`: Serial port for hand communication (default: "/dev/ttyUSB0")
- `baudrate`: Baudrate for serial communication (default: "115200")
- `use_mock_hardware`: Use mock hardware for testing (default: "false")
- `hand_side`: Which hand to control: left or right (default: "left")

### Examples
```bash
# For physical hand with serial port /dev/ttyUSB1
ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_position_control.launch.py serial_port:=/dev/ttyUSB1

# For right hand configuration
ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_trajectory_control.launch.py hand_side:=right

# For simulation/testing without physical hand
ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_position_control.launch.py use_mock_hardware:=true
```

## Controllers
Controller configurations are provided in `config/`:
- `controller_manager.yaml`: Controller manager settings and available controllers
- `inspire_rh56_hand_joint_position_controller.yaml`: Joint position controller parameters
- `inspire_rh56_hand_joint_trajectory_controller.yaml`: Joint trajectory controller parameters

## Hand Descriptions
Complete hand URDF files in `urdf/`:
- `inspire_rh56_hand_left.urdf.xacro`: Left hand configuration
- `inspire_rh56_hand_right.urdf.xacro`: Right hand configuration

## Joint Information
The hand has 6 controllable joints:
- `thumb_proximal_yaw_joint`: Thumb base yaw rotation
- `thumb_proximal_pitch_joint`: Thumb base pitch rotation  
- `index_proximal_joint`: Index finger base joint
- `middle_proximal_joint`: Middle finger base joint
- `ring_proximal_joint`: Ring finger base joint
- `pinky_proximal_joint`: Pinky finger base joint

## Testing
### Joint Position Test
Run the included test script to validate joint position control:
```bash
# Terminal 1: Launch position controller
ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_position_control.launch.py use_mock_hardware:=true

# Terminal 2: Run test script  
python3 /home/ubuntu/ros2_ws/src/robots/inspire_rh56_hand/inspire_rh56_hand_bringup/test/test_hand_position.py
```

### Joint Trajectory Test
Run the included test script to validate joint trajectory control:
```bash
# Terminal 1: Launch trajectory controller
ros2 launch inspire_rh56_hand_bringup inspire_rh56_hand_joint_trajectory_control.launch.py use_mock_hardware:=true

# Terminal 2: Run test script  
python3 /home/ubuntu/ros2_ws/src/robots/inspire_rh56_hand/inspire_rh56_hand_bringup/test/test_hand_trajectory.py
```

### Manual Commands
Test different control modes manually:

**Joint Position Control:**
```bash
# Open hand (all joints to 0)
ros2 topic pub --once /inspire_rh56_hand_joint_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}"

# Close hand (typical grasp position)
ros2 topic pub --once /inspire_rh56_hand_joint_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [1.3, 0.6, 1.4, 1.4, 1.4, 1.4]}"
```

**Joint Trajectory Control:**
```bash
ros2 action send_goal /inspire_rh56_hand_joint_trajectory_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory "{
  trajectory: {
    joint_names: [thumb_proximal_yaw_joint, thumb_proximal_pitch_joint, index_proximal_joint, middle_proximal_joint, ring_proximal_joint, pinky_proximal_joint],
    points: [
      { positions: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], time_from_start: { sec: 2 } },
      { positions: [0.2, 0.2, 0.7, 0.7, 0.7, 0.7], time_from_start: { sec: 3 } },
      { positions: [0.5, 0.4, 1.4, 1.4, 1.4, 1.4], time_from_start: { sec: 4 } },
      { positions: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], time_from_start: { sec: 5 } }
    ]
  }
}"
```

## Introspection
After launching, you can inspect the system:
```bash
ros2 control list_hardware_interfaces
ros2 control list_controllers
ros2 topic list
ros2 service list
```

## Foxglove Studio
An optional layout is available at `config/foxglove/hand_ros2_control.json`. Import it into Foxglove Studio to visualize:
- Joint states
- Controller feedback  
- Hand model
- Control topics

The launch files automatically start the foxglove_bridge for web-based visualization.

## Hardware Setup
For physical hand operation:
1. Connect the hand via USB-to-Serial adapter
2. Ensure proper permissions for the serial port:
   ```bash
   sudo usermod -a -G dialout $USER
   # Then log out and back in
   ```
3. Verify the serial port exists: `ls /dev/ttyUSB*`
4. Use the correct serial port in launch arguments

## Troubleshooting
- **Serial permission errors**: Add your user to the `dialout` group
- **Hand not responding**: Check serial port and baudrate settings
- **Joint limits**: Ensure commanded positions are within joint limits
- **Mock hardware**: Use `use_mock_hardware:=true` for testing without physical hand

## License and maintainers
Refer to `package.xml` for license and maintainer information.