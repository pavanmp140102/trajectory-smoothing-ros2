#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

import random
import numpy as np

from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import PoseStamped


class WaypointLoader(Node):

    def __init__(self):
        super().__init__("waypoint_loader")

        self.publisher = self.create_publisher(
            Path,
            "/raw_path",
            10
        )

        # Subscribe to odometry to track robot position
        self.odom_subscription = self.create_subscription(
            Odometry,
            "/odom",
            self.odom_callback,
            10
        )

        # Track state
        self.current_waypoints = None
        self.robot_position = None
        self.goal_reached_distance = 0.3  # Distance to consider goal reached (m)

        self.get_logger().info("Waypoint Loader Started")

        # Generate first waypoints immediately
        self.generate_and_publish_waypoints()

        # Then check periodically (10 Hz) if goal is reached
        self.timer = self.create_timer(0.1, self.check_and_publish)


    def odom_callback(self, msg):
        """Track robot position from odometry"""
        self.robot_position = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y
        ])


    def generate_random_waypoints(self):
        """Generate new random waypoints starting from origin"""
        waypoints = []
        x = 0.0
        for i in range(6):
            y = random.uniform(-2.0, 2.0)
            waypoints.append((x, y))
            x += random.uniform(1.0, 2.0)
        return waypoints


    def generate_and_publish_waypoints(self):
        """Generate new waypoints and publish them"""
        self.current_waypoints = self.generate_random_waypoints()
        self.get_logger().info(f"Generated NEW waypoints: {self.current_waypoints}")
        
        path_msg = Path()
        path_msg.header.frame_id = "odom"

        for x, y in self.current_waypoints:
            pose = PoseStamped()
            pose.header.frame_id = "odom"
            pose.pose.position.x = float(x)
            pose.pose.position.y = float(y)
            pose.pose.position.z = 0.0
            path_msg.poses.append(pose)

        self.publisher.publish(path_msg)
        self.get_logger().info(f"Published waypoint path ({len(self.current_waypoints)} points)")


    def check_and_publish(self):
        """Check if robot reached goal, generate new waypoints if so"""
        
        # Don't check until we have both waypoints and robot position
        if self.current_waypoints is None or self.robot_position is None:
            return
        
        # Get the final goal (last waypoint)
        goal_x, goal_y = self.current_waypoints[-1]
        goal_position = np.array([goal_x, goal_y])
        
        # Calculate distance to goal
        distance_to_goal = np.linalg.norm(self.robot_position - goal_position)
        
        # If close enough to goal, generate new waypoints
        if distance_to_goal < self.goal_reached_distance:
            self.get_logger().info(
                f"Goal REACHED! (distance: {distance_to_goal:.3f}m). "
                f"Robot at ({self.robot_position[0]:.2f}, {self.robot_position[1]:.2f})"
            )
            self.generate_and_publish_waypoints()
        else:
            # Keep republishing current waypoints (for latecomer subscribers)
            if self.current_waypoints is not None:
                path_msg = Path()
                path_msg.header.frame_id = "odom"

                for x, y in self.current_waypoints:
                    pose = PoseStamped()
                    pose.header.frame_id = "odom"
                    pose.pose.position.x = float(x)
                    pose.pose.position.y = float(y)
                    pose.pose.position.z = 0.0
                    path_msg.poses.append(pose)

                self.publisher.publish(path_msg)


def main(args=None):

    rclpy.init(args=args)

    node = WaypointLoader()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()