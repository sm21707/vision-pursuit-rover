import math
import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from sensor_msgs.msg import Image, LaserScan


class vpr_draft_1(Node):
    def __init__(self):
        super().__init__('VPR_draft_1_node')

        self.cmd_vel_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        image_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=1
        )
        self.image_sub = self.create_subscription(
            Image, '/image', self.image_callback, image_qos
        )

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, qos_profile
        )

        self.vel_timer = self.create_timer(0.1, self.vel_cmd_callback)

        self.bridge = CvBridge()

        self.target_color = [0, 255, 0]
        self.min_target_area = 150

        self.kpa = 0.001
        self.center_zone = 2
        self.max_turn_speed = 1.0
        self.pursue_speed = 0.2

        self.search_speed = 0.3
        self.avoid_forward_speed = 0.07
        self.avoid_turn_speed = 0.6

        self.stop_distance = 0.4
        self.clear_distance = 0.5

        self.front_index = 260
        self.front_half_angle = 30.0
        self.side_center_angle = 60.0
        self.side_half_angle = 35.0

        self.lower_hsv, self.upper_hsv = self.get_limits(self.target_color)
        self.kernel = np.ones((5, 5), np.uint8)

        self.obj_error = None
        self.obstacle_ahead = False
        self.turn_direction = 1.0

        # ---------------- lawnmower ----------------
        self.STRAIGHT = 0
        self.TURN = 1
        self.mow_state = self.STRAIGHT
        self.mow_leg = 0             # even = long row, odd = lane shift
        self.mow_turns_done = 0
        self.mow_turn_sign = -1.0     # +1 = left (CCW), -1 = right (CW)

        self.mow_speed = 0.2         # m/s
        self.mow_turn_speed = 0.5    # rad/s
        self.long_leg_time = 8.0     # s, length of a row
        self.lane_shift_time = 4.0   # s, spacing between rows
        self.turn_time = ((math.pi / 2) / self.mow_turn_speed)  # ~90 degrees

        self.mow_state_start = self.get_clock().now()

        self.get_logger().info("VPR_DRAFT_1 Node Active")

    # ------------------------------------------------------------------
    # Lawnmower state machine
    # ------------------------------------------------------------------
    def set_mow_state(self, state):
        self.mow_state = state
        self.mow_state_start = self.get_clock().now()

    def mow_elapsed(self):
        return (self.get_clock().now() - self.mow_state_start).nanoseconds / 1e9

    def lawnmower_cmd(self, vel):

        if self.obstacle_ahead:
            vel.linear.x = 0.0
            vel.angular.z = self.turn_direction * self.avoid_turn_speed
            return

        t = self.mow_elapsed()

        if self.mow_state == self.STRAIGHT:
            leg_time = self.long_leg_time if self.mow_leg % 2 == 0 else self.lane_shift_time
            vel.linear.x = self.mow_speed
            vel.angular.z = 0.0

            # end of leg: timer ran out OR we hit a wall/obstacle
            if t >= leg_time or self.obstacle_ahead:
                self.mow_leg += 1
                self.set_mow_state(self.TURN)

        else:  # TURN
            if not self.obstacle_ahead:
                vel.linear.x = 0.0
                vel.angular.z = self.mow_turn_sign * self.mow_turn_speed
            
            if t >= self.turn_time:
                self.mow_turns_done += 1
                if self.mow_turns_done % 2 == 0:
                    self.mow_turn_sign *= -1.0   # flip direction after every 2 turns
                self.set_mow_state(self.STRAIGHT)

    def get_limits(self, color):
        c = np.uint8([[color]])
        hue = int(cv2.cvtColor(c, cv2.COLOR_BGR2HSV)[0][0][0])
        lower = np.array([max(hue - 20, 0), 40, 40], dtype=np.uint8)
        upper = np.array([min(hue + 20, 180), 255, 255], dtype=np.uint8)
        return lower, upper


    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        width = frame.shape[1]

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        biggest = max(contours, key=cv2.contourArea, default=None)

        if biggest is not None and cv2.contourArea(biggest) >= self.min_target_area:
            x, y, w, h = cv2.boundingRect(biggest)
            center_x = x + w // 2
            self.obj_error = center_x - width // 2
            self.get_logger().info(f"Object error: {self.obj_error}")

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.circle(frame, (center_x, y + h // 2), 5, (0, 0, 255), -1)
        else:
            self.obj_error = None

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()


    def sector(self, ranges, center, half_width):
        n = len(ranges)
        return [ranges[(center + k) % n] for k in range(-half_width, half_width)]


    def clean(self, readings, max_range):
        good = []
        for r in readings:
            if math.isnan(r) or r <= 0.0:
                continue
            if math.isinf(r):
                r = max_range
            good.append(r)

        if len(good) == 0:
            return [max_range]
        return good


    def scan_callback(self, msg):
        max_range = msg.range_max if math.isfinite(msg.range_max) else 10.0

        per_reading = abs(msg.angle_increment)
        if per_reading == 0.0:
            return

        front_hw = int(round(math.radians(self.front_half_angle) / per_reading))
        side_hw = int(round(math.radians(self.side_half_angle) / per_reading))
        side_off = int(round(math.radians(self.side_center_angle) / per_reading))

        sign = 1 if msg.angle_increment > 0 else -1
        left_index = self.front_index + sign * side_off
        right_index = self.front_index - sign * side_off

        self.get_logger().info(
            f"Scan layout: n={len(msg.ranges)} angle_min={msg.angle_min:.3f} "
            f"inc={msg.angle_increment:.4f} -> front={self.front_index}, "
            f"left={left_index % len(msg.ranges)}, right={right_index % len(msg.ranges)}",
            once=True
        )

        front = self.clean(self.sector(msg.ranges, self.front_index, front_hw), max_range)
        left = self.clean(self.sector(msg.ranges, left_index, side_hw), max_range)
        right = self.clean(self.sector(msg.ranges, right_index, side_hw), max_range)

        left_clear = sum(left) / len(left)
        right_clear = sum(right) / len(right)

        self.get_logger().info(
            f"Front: {min(front):.2f} m, Left: {left_clear:.2f} m, "
            f"Right: {right_clear:.2f} m",
            throttle_duration_sec=0.5
        )

        if not self.obstacle_ahead and min(front) < self.stop_distance:
            self.obstacle_ahead = True
            if abs(left_clear - right_clear) > 0.05:
                self.turn_direction = -1.0 if left_clear > right_clear else 1.0


        elif self.obstacle_ahead and min(front) > self.clear_distance:
            self.obstacle_ahead = False

    def vel_cmd_callback(self):
        vel = Twist()

        if self.obj_error is not None:
            # Target seen: pursue it. Restart the current mow leg's timer so the
            # pattern resumes cleanly if the target is lost.
            self.set_mow_state(self.mow_state)

            centered = abs(self.obj_error) < self.center_zone

            if not centered:
                turn = -self.kpa * self.obj_error
                vel.angular.z = -turn

            if self.obstacle_ahead:
                vel.linear.x = 0.0
                if centered:
                    self.get_logger().info("TARGET REACHED", throttle_duration_sec=2.0)
                else:
                    turn = -self.kpa * self.obj_error
                    vel.angular.z = -turn
            else:
                vel.linear.x = self.pursue_speed

        else:

            if self.obstacle_ahead:
                # AVOIDANCE STATE: bypasses the lawnmower completely
                vel.linear.x = self.avoid_forward_speed
                vel.angular.z = self.turn_direction * self.avoid_turn_speed

                # Once clear, the lawnmower restarts with a fresh long row
                self.mow_leg = 0
                self.mow_turns_done = 0
                self.set_mow_state(self.STRAIGHT)
            else:
                # PATH CLEAR: lawnmower search pattern
                self.lawnmower_cmd(vel)

        self.cmd_vel_pub.publish(vel)


def main(args=None):
    rclpy.init(args=args)
    node = vpr_draft_1()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_vel_pub.publish(Twist())
        node.destroy_node()
        cv2.destroyAllWindows()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
