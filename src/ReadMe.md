# Trajectory Tracking – Path Smoothing (ROS 2)

## Overview

This project implements a **trajectory preprocessing pipeline** in **ROS 2** for generating smooth paths from sparse waypoints.

The system currently performs:

1. **Waypoint generation**
2. **Path smoothing using Cubic Spline interpolation**
3. **Visualization using RViz or optional Matplotlib**

This forms the first stage of a trajectory tracking pipeline that will later generate time-parameterized trajectories.

---

# System Architecture

The pipeline follows a modular ROS design:

```
waypoint_loader
      │
      ▼
   /raw_path  (nav_msgs/Path)
      │
      ▼
spline_smoother
      │
      ▼
/smoothed_path (nav_msgs/Path)
```

Each node performs a single responsibility, making the system easy to extend.

---

# Nodes

## 1. waypoint_loader

Generates waypoints and publishes them as a ROS `nav_msgs/Path`.

### Output Topic

```
/raw_path
```

### Message Type

```
nav_msgs/Path
```

### Features

* Generates random forward-progressing waypoints
* Publishes them in the `map` frame
* Serves as input for the smoothing node

---

## 2. spline_smoother

Subscribes to the raw path and produces a smooth trajectory using **Cubic Spline interpolation**.

### Input Topic

```
/raw_path
```

### Output Topic

```
/smoothed_path
```

### Message Type

```
nav_msgs/Path
```

### Algorithm

1. Extract `(x, y)` waypoint coordinates
2. Compute **arc-length parameterization**
3. Fit **CubicSpline interpolation**
4. Sample dense points along the path
5. Publish the smoothed path

Arc-length parameterization ensures interpolation accuracy when waypoint spacing is uneven.

---

# Optional Visualization

The node supports optional Matplotlib visualization.

### Enable Plotting

```
ros2 run trajectory_tracking spline_smoother \
--ros-args -p enable_plot:=true
```

By default plotting is disabled and visualization is performed using **RViz**.

---

# Running the System

## Build Workspace

```
colcon build
source install/setup.bash
```

---

## Run Waypoint Generator

```
ros2 run trajectory_tracking waypoint_loader
```

---

## Run Path Smoother

```
ros2 run trajectory_tracking spline_smoother
```

---

# Visualization with RViz

Launch RViz:

```
rviz2
```

Add two **Path displays**:

| Topic            | Description          |
| ---------------- | -------------------- |
| `/raw_path`      | original waypoints   |
| `/smoothed_path` | spline smoothed path |

You should observe:

* jagged raw path
* smooth spline trajectory

---

# Dependencies

Python libraries required:

```
numpy
scipy
matplotlib (optional)
```

Install if needed:

```
pip install numpy scipy matplotlib
```

---

# Future Work

Next stage of the project will implement **trajectory generation**.

The smoothed path will be converted into a time-parameterized trajectory:

```
(x, y) → (x, y, t)
```

Steps:

1. Resample path every **0.05 m**
2. Assign velocity **v = 0.3 m/s**
3. Compute timestamps

```
t += distance / velocity
```

Output trajectory format:

```
[(x1, y1, t1),
 (x2, y2, t2),
 ...]
```

This trajectory will later be used by a **trajectory tracking controller**.

---

# Author

Pavan Patil
Robotics / Autonomous Systems Development
