# Parameter Configuration Guide

Simple guide to configuring individual nodes using YAML files.

---

## Overview

Each node has its own configuration file in the `config/` directory:

```
config/
├── trajectory_generator.yaml       ← Sampling & velocity parameters
├── spline_smoother.yaml            ← Smoothing parameters
└── pure_pursuit_controller.yaml    ← Tracking control parameters
```

When you run the system, each node automatically loads its configuration file.

---

## Configuration Files

### 1. trajectory_generator.yaml

Controls how the smooth path is converted to a time-parameterized trajectory.

```yaml
ros__parameters:
  sampling_distance: 0.05   # Distance between trajectory points (m)
  velocity: 0.3             # Constant velocity along trajectory (m/s)
```

**How to Tune:**

| If you want... | Change this | Example |
|---|---|---|
| Smoother motion | Decrease `sampling_distance` | `0.02` instead of `0.05` |
| More computation | Decrease `sampling_distance` | `0.02` |
| Faster computation | Increase `sampling_distance` | `0.1` |
| Faster robot | Increase `velocity` | `0.5` instead of `0.3` |
| Slower robot | Decrease `velocity` | `0.2` |

---

### 2. spline_smoother.yaml

Controls the path smoothing visualization.

```yaml
ros__parameters:
  enable_plot: false        # Set to true to visualize smoothing
```

**Options:**
- `false` - Don't show matplotlib (default)
- `true` - Show matplotlib plot of original vs. smoothed path

---

### 3. pure_pursuit_controller.yaml

Controls how the robot tracks the trajectory (most important for tuning!).

```yaml
ros__parameters:
  lookahead_distance: 0.5        # ⭐ Main tuning parameter (m)
  linear_velocity: 0.3           # Forward velocity (m/s)
  max_angular_velocity: 1.0      # Maximum rotation rate (rad/s)
```

**How to Tune:**

| Problem | Solution | Change |
|---------|----------|--------|
| Robot oscillates/weaves | Increase lookahead | `0.7` instead of `0.5` |
| Robot misses sharp turns | Decrease lookahead | `0.3` instead of `0.5` |
| Too slow | Increase velocity | `0.5` instead of `0.3` |
| Too fast | Decrease velocity | `0.2` instead of `0.3` |
| Jerky turns | Increase lookahead | `0.8` |
| Can't make sharp turns | Decrease lookahead | `0.25` |

**The Main Parameter: `lookahead_distance`**

This is the most important parameter to tune:

- **Small (0.2m)**: Tight, responsive tracking but may oscillate
- **Medium (0.5m)**: Balanced (good starting point)
- **Large (1.0m)**: Smooth, stable but slow to respond to curves

---

## How to Configure

### Method 1: Edit YAML Files Directly

```bash
# Edit trajectory generator settings
nano config/trajectory_generator.yaml

# Edit pure pursuit controller (main tuning)
nano config/pure_pursuit_controller.yaml

# Edit spline smoother (rarely needed)
nano config/spline_smoother.yaml
```

### Method 2: After Editing

After editing any YAML file:

```bash
# Rebuild and reinstall
colcon build --packages-select trajectory_nav
source install/setup.bash

# Run with new configuration
ros2 launch trajectory_nav trajectory_nav.launch.py
```

### Method 3: Command Line (For Quick Testing)

Don't rebuild, just override on command line:

```bash
# Only for testing individual nodes
ros2 run trajectory_nav pure_pursuit_controller \
  --ros-args -p lookahead_distance:=0.7 -p linear_velocity:=0.4
```

---

## Typical Configurations

### For Development/Testing
```yaml
# trajectory_generator.yaml
ros__parameters:
  sampling_distance: 0.05
  velocity: 0.3

# pure_pursuit_controller.yaml
ros__parameters:
  lookahead_distance: 0.5
  linear_velocity: 0.3
  max_angular_velocity: 1.0
```

### For Production (Smooth/Stable)
```yaml
# pure_pursuit_controller.yaml
ros__parameters:
  lookahead_distance: 0.8      # More stable
  linear_velocity: 0.2         # Slower
  max_angular_velocity: 0.8    # Limited turns
```

### For Research (Dense Sampling)
```yaml
# trajectory_generator.yaml
ros__parameters:
  sampling_distance: 0.01      # Ultra-dense
  velocity: 0.25

# spline_smoother.yaml
ros__parameters:
  enable_plot: true            # Visualize
```

---

## Manual Tuning Workflow

### Step 1: Start with Defaults

Run the system as-is:
```bash
ros2 launch trajectory_nav trajectory_nav.launch.py
```

Observe the behavior. Note any issues (oscillation, missing turns, etc.)

### Step 2: Identify the Problem

- **Oscillating**: Robot weaves side-to-side
- **Jerky**: Motion is choppy, not smooth
- **Slow response**: Robot doesn't react quickly to turns
- **Overshooting**: Follows curves too wide

### Step 3: Make ONE Change

Edit ONE parameter only:

```yaml
# pure_pursuit_controller.yaml
# BEFORE:
lookahead_distance: 0.5

# AFTER (trying 0.7 to reduce oscillation):
lookahead_distance: 0.7
```

### Step 4: Rebuild & Test

```bash
colcon build --packages-select trajectory_nav
source install/setup.bash
ros2 launch trajectory_nav trajectory_nav.launch.py
```

### Step 5: Evaluate

Did it improve? If yes → keep it. If no → revert and try different value.

### Step 6: Repeat

Go back to Step 3 and try next parameter.

---

## Monitoring Current Parameters

```bash
# See what parameters are currently loaded
ros2 param get /trajectory_generator sampling_distance
ros2 param get /pure_pursuit_controller lookahead_distance

# List all parameters
ros2 param list

# Watch a parameter in real-time
ros2 param get /pure_pursuit_controller lookahead_distance --watch
```

---

## YAML File Format

**Important Rules:**
- Use 2 spaces for indentation (NOT tabs)
- Colon must be followed by space: `key: value`  (not `key:value`)
- Comments start with `#`
- Don't quote numbers

**Valid:**
```yaml
ros__parameters:
  lookahead_distance: 0.5
  enable_plot: false
```

**Invalid:**
```yaml
ros__parameters:
  lookahead_distance:0.5           # ✗ No space
  enable_plot: "false"             # ✗ Don't quote
  lookahead_distance:	0.5         # ✗ Tab instead of spaces
```

---

## Troubleshooting

### "Config file not found" Error
```
Error: Could not open parameter file
```
**Solution:**
1. Check files exist: `ls config/`
2. Rebuild: `colcon build --packages-select trajectory_nav`
3. Source: `source install/setup.bash`

### Changes Don't Take Effect
**Solution:**
1. Rebuild: `colcon build --packages-select trajectory_nav`
2. Source: `source install/setup.bash`
3. Restart: `ros2 launch trajectory_nav trajectory_nav.launch.py`

### YAML Syntax Error
```
Error: YAML parsing failed
```
**Solution:**
- Check indentation (2 spaces)
- Check colons have space after
- Use online YAML validator

---

## Quick Reference

### Trajectory Generator
```yaml
ros__parameters:
  sampling_distance: 0.05   # Try 0.02-0.1
  velocity: 0.3             # Try 0.2-0.5
```

### Spline Smoother
```yaml
ros__parameters:
  enable_plot: false        # true or false
```

### Pure Pursuit Controller (Main Tuning)
```yaml
ros__parameters:
  lookahead_distance: 0.5   # ← Change to tune behavior
  linear_velocity: 0.3      # ← Change speed
  max_angular_velocity: 1.0 # ← Limit turn rate
```

---

## Summary

✅ Each node has individual YAML configuration  
✅ Edit files to customize behavior  
✅ Rebuild after changes  
✅ Tune `lookahead_distance` for most effects  
✅ Simple and straightforward  

**Next Step**: Edit `config/pure_pursuit_controller.yaml` and change `lookahead_distance` to see the difference!
