# Hardware Build

> **Credit:** the robot is a **TortoiseBot** designed by [RigBetel Labs](https://rigbetellabs.com). We assembled it by following their official [Hardware Assembly guide](https://github.com/rigbetellabs/tortoisebot/wiki/2.-Hardware-Assembly), and the bring-up software and lidar driver are theirs. This page documents how our own build went and how we tested each part.

The full parts breakdown is in [parts-list.md](../hardware/parts-list.md).

## Build sequence

| Stage | What we did |
|---|---|
| 1. Parts check | Checked the kit against the parts list |
| 2. Assembly | Built the four chassis layers following the official guide |
| 3. Raspberry Pi check | Powered the Pi and confirmed it booted properly |
| 4. Motor test | Ran a test program to confirm both motors respond correctly |
| 5. Camera integration | Brought up the USB webcam and confirmed the image topic |
| 6. Lidar integration | Brought up the lidar and checked the scan in RViz2 |
| 7. Full system run | Ran our code on the robot |

## 1. Parts check

We checked every item in the kit against the parts list before starting.

## 2. Assembly

We assembled the robot layer by layer, following RigBetel Labs' guide: motors and base, the electronics layer with the motor driver and power distribution module, the layer for the Raspberry Pi, and finally the sensor layer for the lidar and camera.

## 3. Raspberry Pi setup and check

The Raspberry Pi 4 came with a pre-flashed SD card, so no operating system installation was needed. After assembly we powered it on and checked that it booted and stayed on.

**Issue and fix:** the Pi kept turning on and off. We first replaced the motor driver, which changed nothing. Testing the cables with a multimeter showed that a USB cable was faulty, and replacing it fixed the problem. We now test cables with a meter before replacing larger parts.

## 4. Motor test

We ran a short test program that drives forward, stops, turns left, turns right and stops, so that wrong wiring or a reversed motor shows up immediately.

**Code:** [test/motor_test.py](../test/motor_test.py)

Run it with the robot lifted off the ground so the wheels spin freely.

**Issue and fix:** the motors were underpowered. The power supply was not providing enough voltage, and changing to a higher-voltage supply fixed it.

## 5. Camera integration

We plugged the USB webcam into the Pi and started the feed with `cam2image`, then viewed it in RViz2 to confirm it was publishing. Both steps run on the Pi over SSH.

```bash
ros2 run image_tools cam2image --ros-args \
  -p width:=320 -p height:=240 \
  -p frequency:=20.0 \
  -p reliability:=best_effort \
  -p depth:=1
```

| Setting | Purpose |
|---|---|
| `width`, `height` | A small 320x240 image keeps the load on the Pi low |
| `frequency` | 20 frames per second |
| `reliability:=best_effort` | Drops a frame instead of waiting to resend it, which avoids lag |
| `depth:=1` | Keeps only the latest frame |

**Issue and fix:** the camera was connected but nothing appeared in ROS 2, because a connected camera does not publish by itself. Starting the `cam2image` node fixed it.

**Issue and fix:** the feed later lagged and the robot reacted late to commands. The Pi was overloaded, so we reduced its work by lowering the camera settings above and running the bring-up in a lighter mode (`slam_only:=True`), which skips the navigation stack.

## 6. Lidar integration

We launched the TortoiseBot bring-up file on the Pi, then adjusted the RViz2 settings until the scan displayed correctly.

```bash
ros2 launch tortoisebot_bringup autobringup.launch.py use_sim_time:=False exploration:=True slam_only:=True
```

`use_sim_time:=False` runs it on the real robot, and `slam_only:=True` starts only the sensors and mapping, without the full navigation stack.

## 7. Running our code on the robot

With every part checked, we ran our vision pursuit code. The sensors run on the Raspberry Pi, and our node runs on a laptop on the same network, which receives `/image` and `/scan` and publishes `/cmd_vel`. See [architecture.md](architecture.md) for how the pieces connect.

**Video:** [watch the full run on the rover](../media/videos/robot/final_video.mp4)
