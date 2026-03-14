#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

import random

from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped


class WaypointLoader(Node):

    def __init__(self):
        super().__init__("waypoint_loader")

        self.publisher = self.create_publisher(
            Path,
            "/raw_path",
            10
        )

        self.get_logger().info("Waypoint Loader Started")

        # publish once after startup
        self.timer = self.create_timer(1.0, self.publish_waypoints)


    def generate_random_waypoints(self):

        waypoints = []

        x = 0.0

        for i in range(6):
            y = random.uniform(-2.0, 2.0)
            waypoints.append((x, y))
            x += random.uniform(1.0, 2.0)
        return waypoints


    def publish_waypoints(self):
        waypoints = self.generate_random_waypoints()
        self.get_logger().info(f"Generated waypoints: {waypoints}")

        path_msg = Path()
        path_msg.header.frame_id = "map"

        for x, y in waypoints:

            pose = PoseStamped()

            pose.header.frame_id = "map"

            pose.pose.position.x = float(x)
            pose.pose.position.y = float(y)
            pose.pose.position.z = 0.0

            path_msg.poses.append(pose)

        self.publisher.publish(path_msg)

        self.get_logger().info("Published raw waypoint path")

        # stop timer after first publish (optional)
        self.timer.cancel()


def main(args=None):

    rclpy.init(args=args)

    node = WaypointLoader()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()