#!/bin/bash
# Quick Start Guide for Trajectory Navigation (ROS2 Jazzy)

echo "======================================"
echo "Trajectory Navigation - Quick Start"
echo "======================================"
echo ""

# Source ROS2 setup
echo "1. Setting up ROS2 environment..."
source /opt/ros/jazzy/setup.bash
source ~/Workspace/nav_assignment_ws/install/setup.bash

echo "✓ Environment ready"
echo ""

# Build
echo "2. Building package..."
cd ~/Workspace/nav_assignment_ws
colcon build --packages-select trajectory_nav
echo "✓ Build complete"
echo ""

# Show configuration info
echo "3. Configuration files (edit these to tune!):"
echo ""
echo "   📁 Location: ~/Workspace/nav_assignment_ws/src/trajectory_nav/config/"
echo ""
echo "   Key files:"
echo "   • trajectory_generator.yaml   - Sampling & velocity"
echo "   • spline_smoother.yaml        - Visualization options"
echo "   • pure_pursuit_controller.yaml - Tracking control (main tuning)"
echo ""
echo "   📖 Guide: See docs/CONFIG_SIMPLE.md for tuning instructions"
echo ""

# Show available commands
echo "4. Available commands:"
echo ""
echo "   ▶️  Launch full system:"
echo "   $ ros2 launch trajectory_nav trajectory_nav.launch.py"
echo ""
echo "   ▶️  Run individual nodes:"
echo "   $ ros2 run trajectory_nav waypoint_loader"
echo "   $ ros2 run trajectory_nav spline_smoother"
echo "   $ ros2 run trajectory_nav trajectory_generator"
echo "   $ ros2 run trajectory_nav pure_pursuit_controller"
echo "   $ ros2 run trajectory_nav trajectory_visualizer"
echo ""
echo "   ▶️  Monitor topics:"
echo "   $ ros2 topic list"
echo "   $ ros2 topic echo /cmd_vel"
echo "   $ ros2 topic echo /trajectory"
echo ""
echo "   ▶️  Check current parameters:"
echo "   $ ros2 param get /pure_pursuit_controller lookahead_distance"
echo ""
echo "5. Next steps:"
echo "   1. Read: docs/CONFIG_SIMPLE.md"
echo "   2. Edit: src/trajectory_nav/config/*.yaml"
echo "   3. Build: colcon build --packages-select trajectory_nav"
echo "   4. Run: ros2 launch trajectory_nav trajectory_nav.launch.py"
echo ""
echo "======================================"
echo "For detailed docs, see:"
echo "  • README.md - Overview"
echo "  • docs/QUICKSTART.md - Getting started"
echo "  • docs/CONFIG_SIMPLE.md - Configuration guide"
echo "======================================"
