#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

import numpy as np
import math
from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import Twist, TwistStamped, PoseStamped
from tf_transformations import euler_from_quaternion


class PurePursuitController(Node):

    def __init__(self):
        super().__init__("pure_pursuit_controller")

        # ---- PARAMETERS ----
        self.declare_parameter("lookahead_distance", 0.5)
        self.declare_parameter("linear_velocity", 0.3)
        self.declare_parameter("max_angular_velocity", 1.0)
        
        self.lookahead_distance = self.get_parameter("lookahead_distance").value
        self.linear_velocity = self.get_parameter("linear_velocity").value
        self.max_angular_velocity = self.get_parameter("max_angular_velocity").value

        # ---- STATE ----
        self.trajectory = None
        self.robot_pose = None
        self.target_index = 0

        # ---- SUBSCRIPTIONS ----
        self.trajectory_subscription = self.create_subscription(
            Path,
            "/trajectory",
            self.trajectory_callback,
            10
        )

        self.odom_subscription = self.create_subscription(
            Odometry,
            "/odom",
            self.odom_callback,
            10
        )

        # ---- PUBLISHER ----
        self.cmd_vel_publisher = self.create_publisher(
            TwistStamped,
            "/cmd_vel",
            10
        )

        # ---- CONTROL LOOP ----
        self.control_timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info(
            f"Pure Pursuit Controller Started "
            f"(lookahead_distance={self.lookahead_distance}m, "
            f"velocity={self.linear_velocity}m/s)"
        )


    def trajectory_callback(self, msg):
        """Store the trajectory for tracking"""
        self.trajectory = msg.poses
        self.target_index = 0
        self.get_logger().info(f"Received trajectory with {len(msg.poses)} points")


    def odom_callback(self, msg):
        """Update robot pose from odometry"""
        self.robot_pose = msg.pose.pose


    def control_loop(self):
        """Main control loop - compute velocity commands"""
        
        # Check if we have both trajectory and odometry
        if self.trajectory is None or self.robot_pose is None:
            return

        if len(self.trajectory) == 0:
            return

        # ---- GET CURRENT ROBOT POSE ----
        x_robot = self.robot_pose.position.x
        y_robot = self.robot_pose.position.y
        
        # Extract yaw from quaternion
        quat = self.robot_pose.orientation
        euler = euler_from_quaternion([quat.x, quat.y, quat.z, quat.w])
        theta_robot = euler[2]

        # ---- FIND TARGET POINT (lookahead) ----
        target_point = self.find_lookahead_point(x_robot, y_robot)

        if target_point is None:
            self.publish_cmd_vel(0.0, 0.0)
            self.get_logger().warn("Could not find lookahead point")
            return

        x_target, y_target = target_point

        # ---- PURE PURSUIT CONTROL LAW ----
        # Alpha: angle from robot heading to target point
        alpha = math.atan2(y_target - y_robot, x_target - x_robot) - theta_robot

        # Normalize alpha to [-pi, pi]
        alpha = math.atan2(math.sin(alpha), math.cos(alpha))

        # Angular velocity command
        # omega = (2 * v * sin(alpha)) / lookahead_distance
        if self.lookahead_distance > 0:
            omega = (2.0 * self.linear_velocity * math.sin(alpha)) / self.lookahead_distance
        else:
            omega = 0.0

        # Clamp angular velocity
        omega = np.clip(omega, -self.max_angular_velocity, self.max_angular_velocity)

        # ---- CHECK IF TRAJECTORY IS COMPLETE ----
        # If we're very close to the last point, stop
        last_point = self.trajectory[-1]
        dist_to_end = math.sqrt(
            (last_point.pose.position.x - x_robot)**2 +
            (last_point.pose.position.y - y_robot)**2
        )

        if dist_to_end < 0.2:  # Within 20cm of end
            self.get_logger().info("Trajectory complete!")
            self.publish_cmd_vel(0.0, 0.0)
            return

        # ---- PUBLISH COMMAND ----
        self.publish_cmd_vel(self.linear_velocity, omega)


    def find_lookahead_point(self, x_robot, y_robot):
        """
        Find the lookahead point on the trajectory.
        Returns the first trajectory point that is at least lookahead_distance away.
        """
        
        for i in range(self.target_index, len(self.trajectory)):
            x_traj = self.trajectory[i].pose.position.x
            y_traj = self.trajectory[i].pose.position.y

            distance = math.sqrt((x_traj - x_robot)**2 + (y_traj - y_robot)**2)

            if distance >= self.lookahead_distance:
                self.target_index = i
                return (x_traj, y_traj)

        # If no point found at lookahead distance, return the last point
        if len(self.trajectory) > 0:
            last = self.trajectory[-1]
            return (last.pose.position.x, last.pose.position.y)

        return None


    def publish_cmd_vel(self, linear_vel, angular_vel):
        """Publish velocity command"""
        cmd = TwistStamped()
        cmd.header.stamp.sec = 0
        cmd.header.stamp.nanosec = 0
        cmd.header.frame_id = "odom"
        cmd.twist.linear.x = float(linear_vel)
        cmd.twist.angular.z = float(angular_vel)
        self.cmd_vel_publisher.publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = PurePursuitController()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
