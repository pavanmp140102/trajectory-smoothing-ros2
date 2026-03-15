#!/usr/bin/env python3

import os

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """
    Launch all trajectory navigation nodes.
    
    Each node loads its own configuration from the config/ directory:
    - trajectory_generator.yaml
    - spline_smoother.yaml
    - pure_pursuit_controller.yaml
    
    To customize behavior, edit the YAML files directly.
    
    Usage:
    $ ros2 launch trajectory_nav trajectory_nav.launch.py
    """
    
    package_dir = get_package_share_directory('trajectory_nav')
    config_dir = os.path.join(package_dir, 'config')
    
    # Individual config files for each node
    trajectory_gen_params = os.path.join(config_dir, 'trajectory_generator.yaml')
    spline_smoother_params = os.path.join(config_dir, 'spline_smoother.yaml')
    pure_pursuit_params = os.path.join(config_dir, 'pure_pursuit_controller.yaml')

    # Waypoint Loader Node (no parameters)
    waypoint_loader = Node(
        package='trajectory_nav',
        executable='waypoint_loader',
        name='waypoint_loader',
        output='screen',
    )

    # Spline Smoother Node
    spline_smoother = Node(
        package='trajectory_nav',
        executable='spline_smoother',
        name='spline_smoother',
        output='screen',
        parameters=[spline_smoother_params],
    )

    # Trajectory Generator Node
    trajectory_generator = Node(
        package='trajectory_nav',
        executable='trajectory_generator',
        name='trajectory_generator',
        output='screen',
        parameters=[trajectory_gen_params],
    )

    # Pure Pursuit Controller Node
    pure_pursuit_controller = Node(
        package='trajectory_nav',
        executable='pure_pursuit_controller',
        name='pure_pursuit_controller',
        output='screen',
        parameters=[pure_pursuit_params],
    )

    # Trajectory Visualizer Node (optional, no parameters)
    trajectory_visualizer = Node(
        package='trajectory_nav',
        executable='trajectory_visualizer',
        name='trajectory_visualizer',
        output='screen',
    )

    # Create launch description
    ld = LaunchDescription([
        waypoint_loader,
        spline_smoother,
        trajectory_generator,
        pure_pursuit_controller,
        trajectory_visualizer,
    ])

    return ld
