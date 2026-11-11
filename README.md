# Vision Pursuit Robot

![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble-blue) ![Ubuntu 22.04](https://img.shields.io/badge/Ubuntu-22.04-orange) ![Python 3](https://img.shields.io/badge/Python-3-green) ![OpenCV](https://img.shields.io/badge/OpenCV-vision-red)

> An autonomous ROS 2 mobile robot that locates a colored target with a camera, pursues it, avoids obstacles using a lidar, and stops when it arrives. Built on the **TortoiseBot** platform.

## Contents

- [Overview](#overview)
- [Key features](#key-features)
- [Demo](#demo)
- [Toolkit](#toolkit)
- [Getting started](#getting-started)
- [Usage](#usage)
- [What we learned](#what-we-learned)
- [Repository structure](#repository-structure)
- [Documentation](#documentation)
- [Roadmap](#roadmap)
- [Team](#team)
- [Acknowledgements](#acknowledgements)

## Overview

The Vision Pursuit Robot is the result of a hands-on robotics course project. We started with Python fundamentals, moved through ROS 2 concepts in turtlesim, built perception and obstacle avoidance in Gazebo and RViz2, and finally deployed the complete system on a physical TortoiseBot.

The robot runs a finite state machine (FSM) that combines two behaviors:

- **Perception:** a camera finds a colored object and measures how far it is from the center of the image.
- **Safety:** a 2D lidar watches the area in front of the robot so that it never drives blindly into an obstacle.

| State | Behavior |
|---|---|
| **Search** | Move forward until the target is seen |
| **Pursue** | Steer toward the target and drive at it |
| **Avoid** | Turn away from an obstacle while the target is not in view |
| **Stop** | Halt once the target has been reached |

## Key features

- Color-based target detection using HSV masking, contours and image moments
- Lidar obstacle sensing with separate trigger and release distances (hysteresis) to prevent flickering
- Priority-based state machine, so safety checks always run before searching
- Proportional steering with a dead zone and turn-rate limit
- Distributed setup: sensors run on the Raspberry Pi, decision logic runs on a laptop
- Developed first in simulation (Gazebo Ignition and RViz2), then deployed on hardware

## Demo


https://github.com/user-attachments/assets/1617168d-4c09-4209-9ffa-6db6a6c183ba


## Toolkit

Everything used to build the project, hardware and software together.

| Category | Tool | Purpose |
|---|---|---|
| Platform | TortoiseBot kit by RigBetel Labs | Chassis, drive system and electronics |
| Hardware | Raspberry Pi 4 Model B | Onboard computer |
| Hardware | 2D YDLIDAR with data converter box | Obstacle sensing |
| Hardware | USB webcam | Vision |
| Hardware | 2 BO motors with L298N motor driver | Drive system |
| Hardware | 11.1 V Li-ion battery and power distribution module | Power |
| Software | Ubuntu 22.04 | Operating system |
| Software | ROS 2 Humble | Robot middleware |
| Software | Python 3 | Programming language |
| Software | OpenCV and cv_bridge | Image processing and ROS integration |
| Software | Gazebo Ignition | Physics simulation |
| Software | RViz2 | Visualization of sensor data |
| Software | TortoiseBot bring-up (RigBetel Labs) | Starts the robot's lidar and drive stack |
| Software | Git and GitHub | Version control |

The full parts breakdown is in [hardware/parts-list.md](hardware/parts-list.md). Installation steps for each software tool are in [docs/installation.md](docs/installation.md).

## Getting started

**Prerequisites:** Ubuntu 22.04, ROS 2 Humble, and a TortoiseBot or equivalent robot (for the hardware part).

1. Follow the [installation guide](docs/installation.md) to set up ROS 2, Gazebo Ignition, RViz2 and OpenCV.
2. Assemble the robot using the official [assembly guide](https://github.com/rigbetellabs/tortoisebot/wiki/2.-Hardware-Assembly). Our notes are in [docs/hardware-build.md](docs/hardware-build.md).
3. Clone this repository:

```bash
git clone https://github.com/sm21707/vision-pursuit-robot.git
```

## Usage

### On the real robot

The robot and the laptop must be on the same network.

1. Connect to the Raspberry Pi over SSH. See the TortoiseBot setup guide for Wi-Fi configuration and credentials.

```bash
ssh tortoisebot@<ROBOT_IP>
```

2. On the Pi, start the lidar and robot bring-up:

```bash
ros2 launch tortoisebot_bringup autobringup.launch.py use_sim_time:=False exploration:=True slam_only:=True
```

3. In a second terminal on the Pi, start the camera feed:

```bash
ros2 run image_tools cam2image --ros-args \
  -p width:=320 -p height:=240 \
  -p frequency:=20.0 \
  -p reliability:=best_effort \
  -p depth:=1
```

4. On the laptop, confirm that `/image` and `/scan` are visible with `ros2 topic list`, then start the vision pursuit node (final package coming soon).

### In simulation

Gazebo Ignition and RViz2 are used for early testing. See [docs/installation.md](docs/installation.md) for setup. The simulation code is in `src/03_simulation/`.

## What we learned

- [OpenCV: the techniques we used](docs/opencv.md)
- [System architecture](docs/architecture.md)

## Repository structure

```
vision-pursuit-robot/
├── README.md
├── docs/
│   ├── installation.md       # setting up ROS 2, Gazebo, RViz2, OpenCV
│   ├── architecture.md       # how the software fits together
│   ├── opencv.md             # what we learned about OpenCV
│   ├── hardware-build.md     # assembling and testing the robot
│   └── resources.md          # tutorials and documentation we used
├── hardware/
│   └── parts-list.md
├── src/
│   ├── 01_python_oops/       # Python OOP practice
│   ├── 02_turtlesim/         # shapes, boundary, go-to-goal with PID, FSM
│   ├── 03_simulation/        # color detector and obstacle detector
│   └── 04_hardware/          # code that ran on final hardware 
└── test/
    └── motor_test.py         # checks both motors before running the robot
```

## Documentation

| Document | Contents |
|---|---|
| [Installation](docs/installation.md) | Installing ROS 2, Gazebo Ignition, RViz2, OpenCV and the TortoiseBot software |
| [Architecture](docs/architecture.md) | Nodes, topics, state machine and design decisions |
| [OpenCV](docs/opencv.md) | Color detection techniques we learned |
| [Hardware build](docs/hardware-build.md) | Assembly, testing and sensor integration |
| [Resources](docs/resources.md) | Tutorials and documentation that helped us |

## Roadmap

- Publish the final vision pursuit package
- Add demo videos of the robot pursuing a target and avoiding obstacles
- Publish the motor test and simulation world files

## Team

Built by Shreya, Soham and Pranjal.

## Acknowledgements

This project would not exist without **[RigBetel Labs](https://rigbetellabs.com)** and their open-source **[TortoiseBot](https://github.com/rigbetellabs/tortoisebot)**. The robot used in this project is designed and open-sourced by them. In particular:

- **The robot itself:** the kit, chassis design and electronics layout.
- **The assembly guide:** we built the robot by following their [Hardware Assembly guide](https://github.com/rigbetellabs/tortoisebot/wiki/2.-Hardware-Assembly).
- **The software stack:** the bring-up package we use to start the lidar and drive system, and the lidar driver, come from their repository. We did not write them. Our work is the perception, decision-making and control software that runs on top of it.
- **The documentation and community:** their wiki and Discord made setup and debugging much easier.

Thank you to RigBetel Labs for making robotics accessible to learners. We also relied on the tutorials listed in [docs/resources.md](docs/resources.md).
