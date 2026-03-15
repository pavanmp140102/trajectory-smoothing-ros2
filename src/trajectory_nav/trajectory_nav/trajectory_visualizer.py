#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

import numpy as np
import math
from nav_msgs.msg import Path
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point


class TrajectoryVisualizer(Node):

    def __init__(self):
        super().__init__("trajectory_visualizer")

        # ---- SUBSCRIPTIONS ----
        self.raw_path_subscription = self.create_subscription(
            Path,
            "/raw_path",
            self.raw_path_callback,
            10
        )

        self.smoothed_path_subscription = self.create_subscription(
            Path,
            "/smoothed_path",
            self.smoothed_path_callback,
            10
        )

        self.trajectory_subscription = self.create_subscription(
            Path,
            "/trajectory",
            self.trajectory_callback,
            10
        )

        # ---- PUBLISHERS ----
        self.marker_publisher = self.create_publisher(
            MarkerArray,
            "/trajectory_markers",
            10
        )

        self.get_logger().info("Trajectory Visualizer Started")


    def raw_path_callback(self, msg):
        """Publish raw waypoints as red spheres"""
        markers = MarkerArray()

        # Clear previous markers
        clear_marker = Marker()
        clear_marker.action = Marker.DELETEALL

        for i, pose in enumerate(msg.poses):
            marker = Marker()
            marker.header.frame_id = "odom"
            marker.header.stamp.sec = 0
            marker.header.stamp.nanosec = 0
            marker.ns = "raw_waypoints"
            marker.id = i
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD

            marker.pose.position = pose.pose.position
            marker.scale.x = 0.1
            marker.scale.y = 0.1
            marker.scale.z = 0.1

            marker.color.r = 1.0  # Red
            marker.color.g = 0.0
            marker.color.b = 0.0
            marker.color.a = 1.0

            markers.markers.append(marker)

        # Line connecting waypoints
        line_marker = Marker()
        line_marker.header.frame_id = "odom"
        line_marker.header.stamp.sec = 0
        line_marker.header.stamp.nanosec = 0
        line_marker.ns = "raw_path_line"
        line_marker.id = 0
        line_marker.type = Marker.LINE_STRIP
        line_marker.action = Marker.ADD

        for pose in msg.poses:
            point = Point()
            point.x = pose.pose.position.x
            point.y = pose.pose.position.y
            point.z = pose.pose.position.z
            line_marker.points.append(point)

        line_marker.scale.x = 0.05
        line_marker.color.r = 1.0
        line_marker.color.g = 0.0
        line_marker.color.b = 0.0
        line_marker.color.a = 0.5

        markers.markers.append(line_marker)

        self.marker_publisher.publish(markers)


    def smoothed_path_callback(self, msg):
        """Publish smoothed path as blue line"""
        markers = MarkerArray()

        line_marker = Marker()
        line_marker.header.frame_id = "odom"
        line_marker.header.stamp.sec = 0
        line_marker.header.stamp.nanosec = 0
        line_marker.ns = "smoothed_path"
        line_marker.id = 0
        line_marker.type = Marker.LINE_STRIP
        line_marker.action = Marker.ADD

        for pose in msg.poses:
            point = Point()
            point.x = pose.pose.position.x
            point.y = pose.pose.position.y
            point.z = pose.pose.position.z
            line_marker.points.append(point)

        line_marker.scale.x = 0.03
        line_marker.color.r = 0.0
        line_marker.color.g = 0.0
        line_marker.color.b = 1.0  # Blue
        line_marker.color.a = 0.8

        markers.markers.append(line_marker)

        self.marker_publisher.publish(markers)


    def trajectory_callback(self, msg):
        """Publish trajectory as green spheres (sampled points)"""
        markers = MarkerArray()

        # Sample every 5th point to avoid too many markers
        sample_rate = max(1, len(msg.poses) // 20)

        for idx, pose in enumerate(msg.poses):
            if idx % sample_rate != 0:
                continue

            marker = Marker()
            marker.header.frame_id = "odom"
            marker.header.stamp.sec = 0
            marker.header.stamp.nanosec = 0
            marker.ns = "trajectory_points"
            marker.id = idx
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD

            marker.pose.position = pose.pose.position
            marker.scale.x = 0.08
            marker.scale.y = 0.08
            marker.scale.z = 0.08

            marker.color.r = 0.0
            marker.color.g = 1.0  # Green
            marker.color.b = 0.0
            marker.color.a = 0.7

            markers.markers.append(marker)

        # Line connecting trajectory points
        line_marker = Marker()
        line_marker.header.frame_id = "odom"
        line_marker.header.stamp.sec = 0
        line_marker.header.stamp.nanosec = 0
        line_marker.ns = "trajectory_line"
        line_marker.id = 0
        line_marker.type = Marker.LINE_STRIP
        line_marker.action = Marker.ADD

        for pose in msg.poses:
            point = Point()
            point.x = pose.pose.position.x
            point.y = pose.pose.position.y
            point.z = pose.pose.position.z
            line_marker.points.append(point)

        line_marker.scale.x = 0.02
        line_marker.color.r = 0.0
        line_marker.color.g = 1.0
        line_marker.color.b = 0.0
        line_marker.color.a = 0.6

        markers.markers.append(line_marker)

        self.marker_publisher.publish(markers)


def main(args=None):

    rclpy.init(args=args)

    node = TrajectoryVisualizer()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
