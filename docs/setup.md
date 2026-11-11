# Setup

How to install everything needed to run the project on a laptop, plus the resources we learned from. Tested on **Ubuntu 22.04 with ROS 2 Humble**. What each tool is and how we used it is explained in [concepts.md](concepts.md).

Commands change over time, so the official documentation is linked for each tool. If a command here fails, follow the official page.

**Contents**
1. [Operating system](#1-operating-system)
2. [ROS 2 Humble](#2-ros-2-humble)
3. [Gazebo Ignition](#3-gazebo-ignition)
4. [RViz2](#4-rviz2)
5. [OpenCV and image tools](#5-opencv-and-image-tools)
6. [TortoiseBot software](#6-tortoisebot-software)
7. [Check that everything works](#7-check-that-everything-works)
8. [Resources](#8-resources)

## 1. Operating system

ROS 2 Humble is designed for **Ubuntu 22.04 LTS (Jammy Jellyfish)**, which is its officially supported platform, so we used it for the whole project. Other Ubuntu versions may need extra work or a different ROS 2 release.

```bash
lsb_release -a
```

## 2. ROS 2 Humble

Follow the official guide, [ROS 2 Humble on Ubuntu](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html), and choose the **desktop** install, which includes RViz2. Then load it in every new terminal, or add the line to `~/.bashrc`:

```bash
source /opt/ros/humble/setup.bash
```

Documentation home: [docs.ros.org/en/humble](https://docs.ros.org/en/humble/index.html)

## 3. Gazebo Ignition

Official guide: [Gazebo Fortress on Ubuntu](https://gazebosim.org/docs/fortress/install_ubuntu)

```bash
sudo apt-get update
sudo apt-get install lsb-release wget gnupg
sudo wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt-get update
sudo apt-get install ignition-fortress
```

Check it:

```bash
ign gazebo --version
ign gazebo
```

To let ROS 2 and Gazebo exchange data:

```bash
sudo apt install ros-humble-ros-gz-sim ros-humble-ros-gz-bridge ros-humble-ros-gz-interfaces
```

## 4. RViz2

RViz2 comes with the ROS 2 desktop install. If it's missing:

```bash
sudo apt install ros-humble-rviz2
```

Start it with `rviz2`. Project page: [github.com/ros2/rviz](https://github.com/ros2/rviz)

## 5. OpenCV and image tools

```bash
sudo apt install python3-opencv ros-humble-cv-bridge ros-humble-image-tools
```

| Package | Purpose |
|---|---|
| `python3-opencv` | OpenCV for Python |
| `ros-humble-cv-bridge` | Converts ROS image messages to OpenCV images |
| `ros-humble-image-tools` | Provides the `cam2image` camera node |

## 6. TortoiseBot software

The robot's bring-up software and lidar driver come from RigBetel Labs' [TortoiseBot repository](https://github.com/rigbetellabs/tortoisebot), not from us. Our kit's SD card came pre-flashed with it, so the Raspberry Pi needed no extra installation.

To reproduce it on another machine, follow their README (use the `ros2-humble` branch):

```bash
mkdir -p ~/tb_ws/src && cd ~/tb_ws/src
git clone -b ros2-humble https://github.com/rigbetellabs/tortoisebot.git
cd ~/tb_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-ignore ydlidar_sdk ydlidar_ros2_driver v4l2_camera tortoisebot_firmware tortoisebot_imu
source install/setup.bash
```

The hardware-only packages are built on the robot itself. Their README explains how, and how to connect the robot to your Wi-Fi.

> **Note:** their setup has you enter your Wi-Fi name and password in a file on the SD card. Keep that file out of any repository.

## 7. Check that everything works

```bash
ros2 --help
rviz2
ign gazebo
python3 -c "import cv2; print(cv2.__version__)"
```

If all four run without errors, the setup is complete.

## 8. Resources

| Topic | Resource |
|---|---|
| Python OOP | [OOPS in Python] by [Rishabh Mishra]: [video](https://youtu.be/ecJCVJOSfcs) |
| ROS 2 basics | [ROS2 Tutorials - ROS2 Humble For Beginners](https://www.youtube.com/playlist?list=PLLSegLrePWgJudpPUof4-nVFHGkB62Izy) by Robotics Back-End |
| ROS 2 documentation | [ROS 2 Humble docs](https://docs.ros.org/en/humble/index.html) |
| Color detection | [Detecting color with Python and OpenCV] by [Felipe Tambasco]: [video](https://www.youtube.com/watch?v=aFNDh5k3SjU&t=999s) |
| PID control | [PID Control] by [Brian Douglas]: [video](https://youtu.be/UR0hOmjaHp0) |
| Robot assembly | [TortoiseBot Hardware Assembly guide](https://github.com/rigbetellabs/tortoisebot/wiki/2.-Hardware-Assembly) by RigBetel Labs |
| Robot software | [TortoiseBot repository](https://github.com/rigbetellabs/tortoisebot) by RigBetel Labs |
