# Quick Start Guide

## Prerequisites

### System Requirements
- Ubuntu 24.04 LTS
- ROS2 Jazzy
- Python 3.10+
- colcon build system

### Install ROS2 Jazzy
```bash
# If not already installed
curl -sSL https://repo.ros2.org/ros.key | sudo apt-key add -
sudo apt update && sudo apt install ros-jazzy-desktop
```

### Source ROS2
```bash
source /opt/ros/jazzy/setup.bash
```

---

## Installation

### 1. Clone/Prepare Workspace
```bash
cd ~/Workspace/nav_assignment_ws
cd src
```

### 2. Build Package
```bash
cd ..
colcon build --packages-select trajectory_nav
source install/setup.bash
```

### 3. Verify Build
```bash
ros2 pkg list | grep trajectory_nav
```

Should see: `trajectory_nav`

---

## Running the System

### Quick Start (All Nodes)

```bash
source ~/Workspace/nav_assignment_ws/install/setup.bash
ros2 launch trajectory_nav trajectory_nav.launch.py
```

This starts:
- Waypoint Loader
- Spline Smoother
- Trajectory Generator
- Pure Pursuit Controller
- (Optional) Trajectory Visualizer

### Monitoring Output

You should see logs like:
```
[waypoint_loader-1] Waypoint Loader Started
[waypoint_loader-1] Generated waypoints: [(0.0, 0.0), (1.2, 0.8), ...]
[spline_smoother-2] Spline Smoother Node Started
[spline_smoother-2] Received 6 waypoints
[trajectory_generator-3] Trajectory Generator Started
[trajectory_generator-3] Generating trajectory from 100 poses
[pure_pursuit_controller-4] Pure Pursuit Controller Started
```

---

## Visualizing Results

### With RViz

```bash
# Terminal 2
rviz2
```

**Add displays:**
1. Click "Add Display" → "Marker Array"
2. Set Topic: `/trajectory_markers`
3. Set Frame: `map`

**You'll see:**
- 🔴 Red spheres: Original waypoints
- 🔵 Blue line: Smoothed path
- 🟢 Green line: Trajectory points

### Monitor Topics

```bash
# Terminal 2: Watch trajectory
ros2 topic echo /trajectory

# Terminal 3: Watch velocity commands
ros2 topic echo /cmd_vel

# Terminal 4: List all topics
ros2 topic list
```

---

## Run Individual Nodes

If you want to start nodes separately:

```bash
# Terminal 1: Waypoint Loader
ros2 run trajectory_nav waypoint_loader

# Terminal 2: Spline Smoother
ros2 run trajectory_nav spline_smoother

# Terminal 3: Trajectory Generator
ros2 run trajectory_nav trajectory_generator

# Terminal 4: Pure Pursuit Controller
ros2 run trajectory_nav pure_pursuit_controller

# Terminal 5 (optional): Visualizer
ros2 run trajectory_nav trajectory_visualizer
```

---

## Test with Real Parameters

### Scenario 1: Slow Smooth Tracking
```bash
ros2 run trajectory_nav pure_pursuit_controller \
  --ros-args \
  -p lookahead_distance:=1.0 \
  -p linear_velocity:=0.2 \
  -p max_angular_velocity:=0.8
```

### Scenario 2: Aggressive Tracking
```bash
ros2 run trajectory_nav pure_pursuit_controller \
  --ros-args \
  -p lookahead_distance:=0.2 \
  -p linear_velocity:=0.5 \
  -p max_angular_velocity:=2.0
```

### Scenario 3: Dense Sampling
```bash
ros2 run trajectory_nav trajectory_generator \
  --ros-args \
  -p sampling_distance:=0.02 \
  -p velocity:=0.3
```

---

## Troubleshooting

### "Package not found"
```bash
# Make sure you sourced
source ~/Workspace/nav_assignment_ws/install/setup.bash

# Verify
ros2 pkg list | grep trajectory_nav
```

### "No module named rclpy"
```bash
# ROS2 not sourced
source /opt/ros/jazzy/setup.bash
```

### "No node named 'waypoint_loader'"
```bash
# Rebuild and source again
colcon build --packages-select trajectory_nav
source install/setup.bash
```

### "Topic /odom not found"
This is expected in standalone mode. Robot would normally provide `/odom`. For simulation, see [Turtlebot3 Integration](docs/TURTLEBOT3_INTEGRATION.md).

### Tests Failing
```bash
# Run unit tests
cd ~/Workspace/nav_assignment_ws/src/trajectory_nav
python3 test_components.py
```

Should see all tests pass ✓

---

## What's Happening

When you run the system:

1. **Waypoint Loader** generates 6 random waypoints
   - Publishes to `/raw_path`
   - Stops (one-time generation)

2. **Spline Smoother** receives waypoints
   - Smooths them with cubic spline
   - Publishes 100 smooth points to `/smoothed_path`

3. **Trajectory Generator** receives smooth path
   - Resamples at 0.05m intervals
   - Assigns timestamps (0.3 m/s)
   - Publishes to `/trajectory`

4. **Pure Pursuit Controller** runs loop
   - Every 0.1s: reads `/trajectory` and `/odom`
   - Computes velocity command
   - Publishes to `/cmd_vel`

5. **Trajectory Visualizer** shows everything
   - Displays messages on different topics
   - RViz-ready markers

---

## Key Files

| File | Purpose |
|------|---------|
| `src/trajectory_nav/` | Main package |
| `trajectory_nav/*.py` | Node implementations |
| `launch/trajectory_nav.launch.py` | Multi-node launcher |
| `test_components.py` | Unit tests |
| `docs/` | Detailed documentation |

---

## Next Steps

1. **Read Architecture**: [ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. **Understand Algorithms**: [ALGORITHMS.md](docs/ALGORITHMS.md)
3. **Tune Parameters**: [PARAMETERS.md](docs/PARAMETERS.md)
4. **Use with Turtlebot3**: [TURTLEBOT3_INTEGRATION.md](docs/TURTLEBOT3_INTEGRATION.md)

---

## Getting Help

### Check Logs
```bash
# Save logs to file
ros2 launch trajectory_nav trajectory_nav.launch.py > run.log 2>&1

# Review
cat run.log
```

### Debug Topics
```bash
# See what's available
ros2 topic list

# Check topic content
ros2 topic echo /trajectory

# Check message structure
ros2 interface show nav_msgs/msg/Path
```

### Run Tests
```bash
python3 ~/Workspace/nav_assignment_ws/src/trajectory_nav/test_components.py
```

---

## Common Modifications

### Change Waypoint Source
Edit `trajectory_nav/waypoint_loader.py`:
```python
def generate_waypoints(self):
    # Load from file, external API, etc.
    return [(0,0), (2,1), (4,0)]  # Your waypoints
```

### Adjust Smoothing
Edit `trajectory_nav/spline_smoother.py`:
```python
# Change number of output points
s_smooth = np.linspace(s.min(), s.max(), 200)  # More dense
```

### Use Different Control Law
Create new node, same `/odom` and `/trajectory` interface.

See documentation for more details!
