#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

import numpy as np
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from rosgraph_msgs.msg import Clock

import math


class TrajectoryGenerator(Node):

    def __init__(self):
        super().__init__("trajectory_generator")

        # ---- PARAMETERS ----
        self.declare_parameter("sampling_distance", 0.05)
        self.declare_parameter("velocity", 0.3)
        
        self.sampling_distance = self.get_parameter("sampling_distance").value
        self.velocity = self.get_parameter("velocity").value
        
        # ---- SUBSCRIPTION ----
        self.subscription = self.create_subscription(
            Path,
            "/smoothed_path",
            self.smoothed_path_callback,
            10
        )

        # ---- PUBLISHER ----
        self.trajectory_publisher = self.create_publisher(
            Path,
            "/trajectory",
            10
        )

        self.get_logger().info(
            f"Trajectory Generator Started "
            f"(sampling_distance={self.sampling_distance}m, velocity={self.velocity}m/s)"
        )


    def smoothed_path_callback(self, msg):
        """
        Convert smoothed path (x, y) into time-parameterized trajectory (x, y, t)
        """
        if len(msg.poses) < 2:
            self.get_logger().warn("Not enough poses for trajectory generation")
            return

        self.get_logger().info(f"Generating trajectory from {len(msg.poses)} poses")

        # ---- EXTRACT COORDINATES ----
        poses = msg.poses
        x_coords = np.array([pose.pose.position.x for pose in poses])
        y_coords = np.array([pose.pose.position.y for pose in poses])

        # ---- RESAMPLE PATH AT FIXED DISTANCES ----
        trajectory_points = self.resample_path(x_coords, y_coords)

        if len(trajectory_points) == 0:
            self.get_logger().warn("Failed to generate trajectory points")
            return

        # ---- ASSIGN TIMESTAMPS ----
        trajectory_with_time = self.assign_timestamps(trajectory_points)

        # ---- PUBLISH AS PATH MESSAGE ----
        self.publish_trajectory(trajectory_with_time)

        self.get_logger().info(f"Published trajectory with {len(trajectory_with_time)} points")


    def resample_path(self, x, y):
        """
        Resample path at fixed spatial intervals (sampling_distance)
        Returns: list of (x, y) tuples
        """
        trajectory = [(x[0], y[0])]  # Start point

        for i in range(len(x) - 1):
            dx = x[i+1] - x[i]
            dy = y[i+1] - y[i]
            segment_length = np.sqrt(dx**2 + dy**2)

            if segment_length < 1e-6:
                continue

            # Number of samples in this segment
            num_samples = max(1, int(np.ceil(segment_length / self.sampling_distance)))

            for j in range(1, num_samples + 1):
                t = j / num_samples
                x_sample = x[i] + t * dx
                y_sample = y[i] + t * dy
                
                # Only add if distance from last point is >= sampling_distance
                if len(trajectory) > 0:
                    last_x, last_y = trajectory[-1]
                    dist = np.sqrt((x_sample - last_x)**2 + (y_sample - last_y)**2)
                    if dist >= self.sampling_distance * 0.9:  # Allow slight tolerance
                        trajectory.append((x_sample, y_sample))

        return trajectory


    def assign_timestamps(self, trajectory_points):
        """
        Assign timestamps to trajectory points based on constant velocity
        Returns: list of (x, y, t) tuples
        """
        trajectory_with_time = []
        current_time = 0.0

        for i, (x, y) in enumerate(trajectory_points):
            trajectory_with_time.append((x, y, current_time))

            # Calculate distance to next point
            if i < len(trajectory_points) - 1:
                next_x, next_y = trajectory_points[i + 1]
                distance = np.sqrt((next_x - x)**2 + (next_y - y)**2)
                current_time += distance / self.velocity

        return trajectory_with_time


    def publish_trajectory(self, trajectory_with_time):
        """
        Publish trajectory as a Path message with timestamps in header
        """
        trajectory_msg = Path()
        trajectory_msg.header.frame_id = "odom"
        trajectory_msg.header.stamp.sec = 0
        trajectory_msg.header.stamp.nanosec = 0

        for x, y, t in trajectory_with_time:
            pose = PoseStamped()
            pose.header.frame_id = "odom"
            pose.header.stamp.sec = int(t)
            pose.header.stamp.nanosec = int((t - int(t)) * 1e9)
            
            pose.pose.position.x = float(x)
            pose.pose.position.y = float(y)
            pose.pose.position.z = float(t)  # Store time in z component

            trajectory_msg.poses.append(pose)

        self.trajectory_publisher.publish(trajectory_msg)


def main(args=None):

    rclpy.init(args=args)

    node = TrajectoryGenerator()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
