# Parameter Configuration Guide

Complete guide to using node-specific YAML parameter files with the trajectory navigation system.

---

## Overview

The system now supports **3 methods** for setting parameters, with **node-specific YAML files** as the recommended approach:

### Method 1: Command Line (Best for quick testing)
```bash
ros2 run trajectory_nav trajectory_generator \
  --ros-args -p velocity:=0.5 -p sampling_distance:=0.1
```

### Method 2: YAML Config Files (✅ **RECOMMENDED** - Best for reproducibility)
Each node has its own configuration file:
```bash
# Default config
ros2 launch trajectory_nav trajectory_nav.launch.py

# With preset (each node loads matching preset automatically)
ros2 launch trajectory_nav trajectory_nav.launch.py preset:=turtlebot3
ros2 launch trajectory_nav trajectory_nav.launch.py preset:=aggressive
ros2 launch trajectory_nav trajectory_nav.launch.py preset:=smooth

# Mix and match individual node configs
ros2 launch trajectory_nav trajectory_nav.launch.py \
  traj_gen_config:=trajectory_generator_aggressive.yaml \
  controller_config:=pure_pursuit_controller_smooth.yaml
```

### Method 3: Launch File Inline (Best for automation)
Update `launch/trajectory_nav.launch.py` with parameters.

---

## Configuration File Organization

```
config/
├── Base Configs (Default parameters)
│   ├── spline_smoother.yaml
│   ├── trajectory_generator.yaml
│   └── pure_pursuit_controller.yaml
│
└── Presets (Alternative configurations)
    ├── trajectory_generator_turtlebot3.yaml
    ├── trajectory_generator_aggressive.yaml
    ├── trajectory_generator_smooth.yaml
    │
    ├── pure_pursuit_controller_turtlebot3.yaml
    ├── pure_pursuit_controller_aggressive.yaml
    └── pure_pursuit_controller_smooth.yaml
```

### Key Feature: **Each Node Has Its Own Config File**

- **Spline Smoother Config**: `spline_smoother.yaml`
  - Only parameters needed by this node
  - `enable_plot`

- **Trajectory Generator Config**: `trajectory_generator.yaml` (+ presets)
  - Only parameters needed by this node
  - `sampling_distance`, `velocity`

- **Pure Pursuit Controller Config**: `pure_pursuit_controller.yaml` (+ presets)
  - Only parameters needed by this node
  - `lookahead_distance`, `linear_velocity`, `max_angular_velocity`

---

## Default Base Configurations

### spline_smoother.yaml
```yaml
ros__parameters:
  enable_plot: false
```

### trajectory_generator.yaml
```yaml
ros__parameters:
  sampling_distance: 0.05       # 5cm spacing
  velocity: 0.3                 # 30cm/s
```

### pure_pursuit_controller.yaml
```yaml
ros__parameters:
  lookahead_distance: 0.5       # 50cm
  linear_velocity: 0.3          # 30cm/s
  max_angular_velocity: 1.0     # 1 rad/s
```

---

## Available Presets

### 1. Turtlebot3 Preset
**Command**: `preset:=turtlebot3`

**Files Used**:
- `trajectory_generator_turtlebot3.yaml`
- `pure_pursuit_controller_turtlebot3.yaml`
- `spline_smoother.yaml` (unchanged)

**Characteristics**: Conservative, stable, slower

---

### 2. Aggressive Preset
**Command**: `preset:=aggressive`

**Files Used**:
- `trajectory_generator_aggressive.yaml`
- `pure_pursuit_controller_aggressive.yaml`
- `spline_smoother.yaml` (unchanged)

**Characteristics**: Fast, tight tracking, high oscillation risk

---

### 3. Smooth Preset
**Command**: `preset:=smooth`

**Files Used**:
- `trajectory_generator_smooth.yaml`
- `pure_pursuit_controller_smooth.yaml`
- `spline_smoother.yaml` (unchanged)

**Characteristics**: Smooth, stable, production-ready

---

## How It Works

### Launch File Parameter Resolution

```python
# Declare preset argument
preset_arg = DeclareLaunchArgument('preset', default_value='')

# Build file names dynamically
preset = LaunchConfiguration('preset')
preset_suffix = ['_', preset]  # Creates _turtlebot3, _aggressive, etc.

# Declare individual config args for each node
traj_gen_config_arg = DeclareLaunchArgument(
    'traj_gen_config',
    default_value=['trajectory_generator', preset_suffix, '.yaml']
)
```

**Example**: When `preset:=turtlebot3`:
- `trajectory_generator` + `_turtlebot3` + `.yaml` → `trajectory_generator_turtlebot3.yaml`
- `pure_pursuit_controller` + `_turtlebot3` + `.yaml` → `pure_pursuit_controller_turtlebot3.yaml`

### Node Configuration Loading

Each node loads its specific config file:

```python
trajectory_generator = Node(
    package='trajectory_nav',
    executable='trajectory_generator',
    parameters=[traj_gen_params],  # ← Loads trajectory_generator.yaml
)

pure_pursuit_controller = Node(
    package='trajectory_nav',
    executable='pure_pursuit_controller',
    parameters=[controller_params],  # ← Loads pure_pursuit_controller.yaml
)
```

---

## Usage Examples

### Example 1: Default Configuration
```bash
ros2 launch trajectory_nav trajectory_nav.launch.py
```
**Result**:
- Trajectory Generator loads `trajectory_generator.yaml`
- Pure Pursuit Controller loads `pure_pursuit_controller.yaml`
- Spline Smoother loads `spline_smoother.yaml`

### Example 2: Turtlebot3 Preset
```bash
ros2 launch trajectory_nav trajectory_nav.launch.py preset:=turtlebot3
```
**Result**:
- Trajectory Generator loads `trajectory_generator_turtlebot3.yaml`
- Pure Pursuit Controller loads `pure_pursuit_controller_turtlebot3.yaml`
- Spline Smoother loads `spline_smoother.yaml` (no turtlebot3 version)

### Example 3: Mix and Match Configs
```bash
ros2 launch trajectory_nav trajectory_nav.launch.py \
  traj_gen_config:=trajectory_generator_aggressive.yaml \
  controller_config:=pure_pursuit_controller_smooth.yaml
```
**Result**:
- Trajectory Generator loads `trajectory_generator_aggressive.yaml`
- Pure Pursuit Controller loads `pure_pursuit_controller_smooth.yaml`
- Spline Smoother loads `spline_smoother.yaml`

### Example 4: Override Individual Node
```bash
# Use smooth preset, but override trajectory generator
ros2 launch trajectory_nav trajectory_nav.launch.py \
  preset:=smooth \
  traj_gen_config:=trajectory_generator_aggressive.yaml
```

---

## Creating Custom Node Configs

### Step 1: Create New Config File

Create `config/trajectory_generator_my_robot.yaml`:

```yaml
# Trajectory Generator - My Robot Preset

ros__parameters:
  sampling_distance: 0.08
  velocity: 0.35

```

### Step 2: Update setup.py

Add your config to the data_files:

```python
('share/' + package_name + '/config', [
    'config/trajectory_generator.yaml',
    'config/pure_pursuit_controller.yaml',
    'config/trajectory_generator_my_robot.yaml',  # ← Add this line
    'config/pure_pursuit_controller_my_robot.yaml',
    # ... other configs
]),
```

### Step 3: Use Your Custom Config

```bash
colcon build --packages-select trajectory_nav
source install/setup.bash

# Create preset group
ros2 launch trajectory_nav trajectory_nav.launch.py \
  traj_gen_config:=trajectory_generator_my_robot.yaml \
  controller_config:=pure_pursuit_controller_my_robot.yaml
```

---

## YAML File Structure

### Per-Node Configuration

Each node's YAML file contains **only that node's parameters**:

```yaml
# trajectory_generator.yaml
ros__parameters:
  sampling_distance: 0.05
  velocity: 0.3
```

```yaml
# pure_pursuit_controller.yaml  
ros__parameters:
  lookahead_distance: 0.5
  linear_velocity: 0.3
  max_angular_velocity: 1.0
```

```yaml
# spline_smoother.yaml
ros__parameters:
  enable_plot: false
```

### Parameter Types

```yaml
# Float
velocity: 0.3
lookahead_distance: 0.5

# Integer
max_iterations: 100

# Boolean
enable_plot: false

# String
frame_id: "map"

# List
waypoints: [0.0, 1.0, 2.0]
```

---

## Comparison: Which Method to Use?

| Method | Best For | Complexity | Flexibility |
|--------|----------|-----------|------------|
| **YAML Config** | Production, reproducibility | Low | High |
| **Command Line** | Quick testing | Very Low | Medium |
| **Launch File** | Integration, automation | Medium | Low |

### Quick Decision Guide

- **Just testing?** → Use command line
  ```bash
  ros2 run trajectory_nav pure_pursuit_controller --ros-args -p velocity:=0.5
  ```

- **Want reproducible setup?** → Use YAML + preset
  ```bash
  ros2 launch trajectory_nav trajectory_nav.launch.py preset:=smooth
  ```

- **Need different node configs?** → Use YAML + specific files
  ```bash
  ros2 launch trajectory_nav trajectory_nav.launch.py \
    traj_gen_config:=trajectory_generator_aggressive.yaml \
    controller_config:=pure_pursuit_controller_smooth.yaml
  ```

- **Deploying to production?** → Use YAML + launch file
  ```bash
  ros2 launch trajectory_nav trajectory_nav.launch.py preset:=turtlebot3
  ```

---

## Monitoring Parameter Values

### Check Current Parameters

```bash
# List all parameters
ros2 param list

# Get specific parameter
ros2 param get /trajectory_generator sampling_distance

# Get controller parameter
ros2 param get /pure_pursuit_controller lookahead_distance
```

### Verify Config Loaded

```bash
# Start with turtlebot3 preset
ros2 launch trajectory_nav trajectory_nav.launch.py preset:=turtlebot3

# In another terminal, verify configs loaded
ros2 param get /trajectory_generator sampling_distance
   # Expected: 0.1 (from turtlebot3 preset)

ros2 param get /pure_pursuit_controller lookahead_distance
   # Expected: 0.3 (from turtlebot3 preset)

ros2 param get /spline_smoother enable_plot
   # Expected: false (base config unchanged)
```

---

## Troubleshooting Configuration Issues

### "Config file not found"
```
Error: Cannot find configuration file: trajectory_generator_turtlebot3.yaml
```
**Solution**:
1. Verify file exists: `ls config/*.yaml`
2. Rebuild package: `colcon build --packages-select trajectory_nav`
3. Source setup: `source install/setup.bash`
4. Check file name spelling

### Parameters not loading

```bash
# Debug: Check which files are being loaded
ros2 launch trajectory_nav trajectory_nav.launch.py preset:=turtlebot3 --debug
```

Look for lines like:
```
parameters=['/path/to/trajectory_generator_turtlebot3.yaml']
```

If file not found, it falls back to base config.

### YAML syntax error
```
Error: YAML syntax error in parameter file
```
**Solution**:
- Check indentation (use 2 spaces, not tabs)
- Verify colons: `key: value` (space after colon)
- No quotes needed for numbers: `velocity: 0.3` not `velocity: "0.3"`

Valid format:
```yaml
ros__parameters:
  sampling_distance: 0.05
  velocity: 0.3
  enable_plot: false
```

Invalid format:
```yaml
ros__parameters:
    sampling_distance: 0.05  # ← Wrong indentation (4 spaces)
  velocity: 0.3              # ← Inconsistent indentation
  enable_plot:false          # ← Missing space after colon
```

---

## Advanced: Individual Node Configuration

Instead of presets, configure each node independently:

```bash
# Custom trajectory generator
ros2 launch trajectory_nav trajectory_nav.launch.py \
  traj_gen_config:=trajectory_generator_aggressive.yaml

# Result:
# - trajectory_generator loads aggressive config
# - pure_pursuit_controller loads default config
# - spline_smoother loads default config
```

This is great for fine-tuning specific nodes without affecting others!

---

## Summary

✅ **3 parameter setting methods**:
1. **Command line** - Quick testing
2. **YAML files (per-node)** - Reproducibility ⭐ RECOMMENDED
3. **Launch file** - Automation

✅ **Node-specific configuration**:
- Each node has its own YAML file
- Independent, modular design
- Easy to mix and match

✅ **Preset system**:
- `preset:=turtlebot3` - Conservative
- `preset:=aggressive` - Fast tracking
- `preset:=smooth` - Production-ready

✅ **Flexibility**:
- Use presets for quick setup
- Override individual nodes
- Create custom configs

---

## Next Steps

1. **Try presets**:
   ```bash
   ros2 launch trajectory_nav trajectory_nav.launch.py preset:=turtlebot3
   ros2 launch trajectory_nav trajectory_nav.launch.py preset:=smooth
   ```

2. **Mix and match nodes**:
   ```bash
   ros2 launch trajectory_nav trajectory_nav.launch.py \
     traj_gen_config:=trajectory_generator_aggressive.yaml \
     controller_config:=pure_pursuit_controller_smooth.yaml
   ```

3. **Create custom config** for your robot

4. **Monitor parameters**:
   ```bash
   ros2 param get /trajectory_generator sampling_distance
   ros2 param get /pure_pursuit_controller lookahead_distance
   ```

See [PARAMETERS.md](PARAMETERS.md) for detailed tuning guide!
