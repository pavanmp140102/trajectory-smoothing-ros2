#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped


class SplineSmoother(Node):

    def __init__(self):
        super().__init__("spline_smoother")

        # ---- PARAMETER ----
        self.declare_parameter("enable_plot", False)
        self.enable_plot = self.get_parameter("enable_plot").value

        self.subscription = self.create_subscription(
            Path,
            "/raw_path",
            self.path_callback,
            10
        )

        self.publisher = self.create_publisher(
            Path,
            "/smoothed_path",
            10
        )

        self.plotted = False

        self.get_logger().info("Spline Smoother Node Started")


    def path_callback(self, msg):

        if len(msg.poses) < 3:
            self.get_logger().warn("Not enough waypoints for spline smoothing")
            return

        self.get_logger().info(f"Received {len(msg.poses)} waypoints")

        # ---- EXTRACT COORDINATES ----
        x = np.array([pose.pose.position.x for pose in msg.poses])
        y = np.array([pose.pose.position.y for pose in msg.poses])

        # ---- ARC LENGTH PARAMETERIZATION ----
        dx = np.diff(x)
        dy = np.diff(y)

        distances = np.sqrt(dx**2 + dy**2)

        s = np.concatenate(([0], np.cumsum(distances)))

        # ---- SPLINE FIT ----
        spline_x = CubicSpline(s, x, bc_type='natural')
        spline_y = CubicSpline(s, y, bc_type='natural')

        # ---- DENSE SAMPLING ----
        s_smooth = np.linspace(s.min(), s.max(), 100)

        x_smooth = spline_x(s_smooth)
        y_smooth = spline_y(s_smooth)

        # ---- PUBLISH SMOOTHED PATH ----
        smoothed_path = Path()
        smoothed_path.header.frame_id = "odom"

        for i in range(len(x_smooth)):

            pose = PoseStamped()
            pose.header.frame_id = "odom"

            pose.pose.position.x = float(x_smooth[i])
            pose.pose.position.y = float(y_smooth[i])
            pose.pose.position.z = 0.0

            smoothed_path.poses.append(pose)

        self.publisher.publish(smoothed_path)

        self.get_logger().info("Published smoothed path")

        # ---- OPTIONAL PLOT ----
        if self.enable_plot and not self.plotted:
            self.plot_paths(x, y, x_smooth, y_smooth)
            self.plotted = True


    def plot_paths(self, x, y, x_smooth, y_smooth):

        plt.figure()

        plt.plot(x, y, 'ro-', label="Original Waypoints")
        plt.plot(x_smooth, y_smooth, 'b-', label="Smoothed Path")

        plt.xlabel("X")
        plt.ylabel("Y")

        plt.title("Arc-Length Cubic Spline Path Smoothing")

        plt.legend()
        plt.grid(True)

        plt.show()


def main(args=None):

    rclpy.init(args=args)

    node = SplineSmoother()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()