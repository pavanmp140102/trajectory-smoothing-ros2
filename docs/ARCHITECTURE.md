# System Architecture

## Overview

The trajectory navigation system is designed as a modular ROS2 pipeline where each node performs a single responsibility. This architecture allows easy extension and debugging.

## Data Flow Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRAJECTORY NAVIGATION PIPELINE                │
└─────────────────────────────────────────────────────────────────┘

        Stage 1                Stage 2               Stage 3
        (Input)            (Processing)          (Execution)

┌──────────────────┐     ┌──────────────────┐   ┌──────────────────┐
│ Waypoint Loader  │────▶│ Spline Smoother  │──▶│ Trajectory Gen.  │
│                  │     │                  │   │                  │
│ • Random points  │     │ • Arc-length     │   │ • Resample @     │
│ • Publishes      │     │   parameterization   │   0.05m intervals│
│   /raw_path      │     │ • Cubic spline   │   │ • Add timestamps │
│                  │     │   interpolation  │   │   (v=0.3 m/s)   │
└──────────────────┘     │ • Smooth curve   │   │ • Publishes      │
                         │ • Publishes      │   │   /trajectory    │
                         │   /smoothed_path │   │                  │
                         └──────────────────┘   └──────────────────┘
                                                        │
                                                        ▼
                                        ┌───────────────────────────┐
                                        │  Pure Pursuit Controller  │
                                        │                           │
                                        │ • Reads /trajectory       │
                                        │ • Reads /odom             │
                                        │ • Implements tracking     │
                                        │ • Publishes /cmd_vel      │
                                        │                           │
                                        └───────────────────────────┘
                                                        │
                                                        ▼
                                        ┌───────────────────────────┐
                                        │  Robot (Differential)     │
                                        │                           │
                                        │ • Differential drive      │
                                        │ • Publishes /odom (loop)  │
                                        │                           │
                                        └───────────────────────────┘
```

## Topics & Message Types

### Published Topics

| Topic | Node | Message Type | Description |
|-------|------|--------------|-------------|
| `/raw_path` | waypoint_loader | `nav_msgs/Path` | Original discrete waypoints |
| `/smoothed_path` | spline_smoother | `nav_msgs/Path` | Smoothed continuous path |
| `/trajectory` | trajectory_generator | `nav_msgs/Path` | Time-parameterized trajectory (time in z) |
| `/cmd_vel` | pure_pursuit_controller | `geometry_msgs/Twist` | Linear (x) and angular (z) velocities |
| `/trajectory_markers` | trajectory_visualizer | `visualization_msgs/MarkerArray` | RViz visualization markers |

### Subscribed Topics

| Topic | Node | Message Type | Purpose |
|-------|------|--------------|---------|
| `/raw_path` | spline_smoother | `nav_msgs/Path` | Raw waypoints to smooth |
| `/smoothed_path` | trajectory_generator | `nav_msgs/Path` | Smoothed path to resample |
| `/trajectory` | pure_pursuit_controller | `nav_msgs/Path` | Trajectory to track |
| `/odom` | pure_pursuit_controller | `nav_msgs/Odometry` | Robot pose feedback |
| `/raw_path` | trajectory_visualizer | `nav_msgs/Path` | For visualization |
| `/smoothed_path` | trajectory_visualizer | `nav_msgs/Path` | For visualization |
| `/trajectory` | trajectory_visualizer | `nav_msgs/Path` | For visualization |

## Node Details

### 1. Waypoint Loader
- **Role**: Input generation
- **Dependencies**: None
- **Output**: Random forward-progressing waypoints
- **Frame**: `map`

### 2. Spline Smoother
- **Role**: Path interpolation
- **Algorithm**: Cubic spline with arc-length parameterization
- **Input**: Discrete waypoints
- **Output**: Dense smooth path (100 points default)
- **Features**: Optional matplotlib visualization

### 3. Trajectory Generator
- **Role**: Time parameterization
- **Algorithm**: Fixed spatial resampling + constant velocity timing
- **Input**: Smooth path
- **Output**: (x, y, t) trajectory
- **Sampling**: 0.05m intervals at 0.3 m/s

### 4. Pure Pursuit Controller
- **Role**: Trajectory tracking
- **Algorithm**: Pure pursuit control law
- **Input**: Trajectory + odometry feedback
- **Output**: Velocity commands
- **Loop Rate**: 10 Hz (0.1s timer)

### 5. Trajectory Visualizer
- **Role**: Debugging/visualization
- **Output**: RViz markers
- **Color Coding**:
  - 🔴 Red: Raw waypoints
  - 🔵 Blue: Smoothed path
  - 🟢 Green: Trajectory points

## Coordinate Frames

All nodes use the `map` frame for consistency:
- **Frame ID**: `map` (global coordinate system)
- **Robot Position**: (x, y, θ) in map frame
- **Path Representation**: (x_path, y_path) in map frame

## Timing & Synchronization

- **Waypoint Generation**: One-time at startup
- **Spline Smoothing**: Triggered on `/raw_path` subscription
- **Trajectory Generation**: Triggered on `/smoothed_path` subscription
- **Control Loop**: Fixed 10 Hz timer (0.1s)
- **Visualization**: Event-triggered on topic updates

## Closed-Loop Feedback

```
Pure Pursuit Controller
    ┌─────────────────────┐
    │  Trajectory Tracking │
    └──────────┬──────────┘
               │ publishes
               ▼
          /cmd_vel
               │
               ▼
          Robot Motors
               │
               │ executes
               ▼
          Robot Motion
               │
               │ generates
               ▼
          /odom (feedback)
               │
               └─────────▶ Pure Pursuit Controller (reads odom)
                          Adjusts next /cmd_vel command
```

The controller operates in a **closed loop**:
1. Read current pose from `/odom`
2. Find lookahead point on trajectory
3. Compute velocity command via pure pursuit law
4. Publish to `/cmd_vel`
5. Robot executes command
6. Odometry is published
7. Loop repeats at 10 Hz

## Extension Points

### Easy to Extend

1. **Waypoint source**: Replace random generation with file I/O
2. **Smoothing algorithm**: Swap cubic spline for different interpolation
3. **Trajectory generation**: Add obstacle avoidance or time optimization
4. **Controller**: Implement different control laws (PID, MPC, etc.)
5. **Visualization**: Add custom markers or data logging

### Information Flow

Each node is **loosely coupled** via ROS topics:
- Nodes don't need to know about each other
- Can add/remove nodes without breaking system
- Easy to replace implementation while keeping interface
