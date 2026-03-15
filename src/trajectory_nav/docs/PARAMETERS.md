# Parameters & Tuning

## All Tunable Parameters

### Trajectory Generator

Located in: `src/trajectory_nav/trajectory_nav/trajectory_generator.py`

#### `sampling_distance` (float)
- **Type**: Double
- **Default**: `0.05`
- **Unit**: meters
- **Range**: 0.01 - 0.5
- **Description**: Spatial distance between resampled trajectory points
- **Effect**:
  - Smaller → more dense points, finer trajectory, more computation
  - Larger → fewer points, coarser trajectory, less computation
- **Recommendation**: 
  - Simulation: 0.05 - 0.1 m
  - Real robot: 0.1 - 0.2 m

#### `velocity` (float)
- **Type**: Double
- **Default**: `0.3`
- **Unit**: m/s
- **Range**: 0.1 - 1.0
- **Description**: Constant velocity along trajectory
- **Effect**:
  - Affects timing only, not spatial shape
  - Higher velocity → shorter trajectory duration
  - Lower velocity → longer trajectory duration, smoother acceleration
- **Recommendation**: 
  - Test: 0.2 - 0.5 m/s
  - Real: Depends on robot capabilities

---

### Pure Pursuit Controller

Located in: `src/trajectory_nav/trajectory_nav/pure_pursuit_controller.py`

#### `lookahead_distance` (float) ⭐ MOST IMPORTANT
- **Type**: Double
- **Default**: `0.5`
- **Unit**: meters
- **Range**: 0.2 - 2.0
- **Description**: Distance ahead on trajectory to aim for
- **Effects**:
  - **Small (0.2m)**: Aggressive tracking, oscillates, follows closely
  - **Medium (0.5m)**: Balanced, recommended
  - **Large (1.0m)**: Smooth but sluggish, may miss sharp turns
- **How to tune**:
  1. Start with 0.5 m
  2. If robot oscillates: **increase** to 0.7 m
  3. If robot misses turns: **decrease** to 0.3 m
  4. Find sweet spot where tracking is smooth and accurate
- **Recommendation**:
  - Simulation: 0.3 - 0.7 m
  - Real robot: 0.5 - 1.5 m (larger for high-speed robots)

#### `linear_velocity` (float)
- **Type**: Double
- **Default**: `0.3`
- **Unit**: m/s
- **Range**: 0.1 - 1.0
- **Description**: Forward velocity of robot
- **Effect**:
  - Higher speed requires larger lookahead distance
  - Lower speed allows tighter tracking
- **Recommendation**:
  - Simulation: 0.2 - 0.5 m/s
  - Real robot: Device-dependent, typically 0.3 - 0.8 m/s

#### `max_angular_velocity` (float)
- **Type**: Double
- **Default**: `1.0`
- **Unit**: rad/s
- **Range**: 0.5 - 2.0
- **Description**: Maximum rotational velocity
- **Effect**:
  - Limits maximum turn rate
  - Prevents hardware saturation
  - Caps control law output
- **Recommendation**:
  - Simulation: 1.0 - 2.0 rad/s (no physical limits)
  - Real robot: Check device specifications
  - For Turtlebot3: ~1.0 - 1.5 rad/s

---

### Spline Smoother

Located in: `src/trajectory_nav/trajectory_nav/spline_smoother.py`

#### `enable_plot` (bool)
- **Type**: Boolean
- **Default**: `false`
- **Description**: Enable matplotlib visualization of smoothing
- **Effect**: Shows original waypoints vs. smoothed path
- **Usage**:
  ```bash
  ros2 run trajectory_nav spline_smoother --ros-args -p enable_plot:=true
  ```
- **Note**: Matplotlib may block ROS if used in production

---

## Parameter Presets

### Preset 1: Simulation (Conservative)
Best for initial testing in Gazebo
```python
# trajectory_generator
sampling_distance: 0.05
velocity: 0.3

# pure_pursuit_controller
lookahead_distance: 0.5
linear_velocity: 0.3
max_angular_velocity: 1.0
```

### Preset 2: Turtlebot3 (Reduced)
Tuned for Turtlebot3 in Gazebo
```python
# trajectory_generator
sampling_distance: 0.1
velocity: 0.2

# pure_pursuit_controller
lookahead_distance: 0.3
linear_velocity: 0.2
max_angular_velocity: 1.0
```

### Preset 3: Fast Tracking
For aggressive tracking with tight curves
```python
# trajectory_generator
sampling_distance: 0.02
velocity: 0.5

# pure_pursuit_controller
lookahead_distance: 0.2
linear_velocity: 0.5
max_angular_velocity: 2.0
```

### Preset 4: Smooth Tracking
For smooth, stable tracking
```python
# trajectory_generator
sampling_distance: 0.1
velocity: 0.2

# pure_pursuit_controller
lookahead_distance: 1.0
linear_velocity: 0.2
max_angular_velocity: 0.8
```

---

## Setting Parameters

### Method 1: Command Line
```bash
# Set individual parameter
ros2 run trajectory_nav trajectory_generator \
  --ros-args -p velocity:=0.5 -p sampling_distance:=0.1
```

### Method 2: Launch File
Edit `launch/trajectory_nav.launch.py`:
```python
trajectory_generator = Node(
    package='trajectory_nav',
    executable='trajectory_generator',
    parameters=[{
        'sampling_distance': 0.1,
        'velocity': 0.5,
    }],
)
```

### Method 3: ROS Parameter File
Create `params.yaml`:
```yaml
/**:
  ros__parameters:
    trajectory_generator:
      sampling_distance: 0.1
      velocity: 0.5
    pure_pursuit_controller:
      lookahead_distance: 0.4
      linear_velocity: 0.3
      max_angular_velocity: 1.0
```

Then launch with:
```bash
ros2 launch trajectory_nav trajectory_nav.launch.py params_file:=params.yaml
```

---

## Typical Tuning Workflow

### 1. Identify Problem
```
Robot behavior          Likely cause           Adjustment
────────────────────────────────────────────────────────
Oscillates side-to-side Too aggressive         ↑ lookahead_distance
Misses sharp turns      Too conservative       ↓ lookahead_distance
Too slow                Need more speed        ↑ linear_velocity
Too jerky/choppy        Sampling too coarse    ↓ sampling_distance
```

### 2. Make One Change
Change only ONE parameter at a time.

### 3. Test & Observe
Watch robot behavior for 1-2 cycles.

### 4. Evaluate
- Tracking error acceptable?
- Motion smooth?
- Any oscillations?

### 5. Repeat
Iterate until satisfied.

---

## Performance Monitoring

### Topics to Monitor

```bash
# Watch actual velocity commands
ros2 topic echo /cmd_vel

# Watch target trajectory
ros2 topic echo /trajectory

# Watch odometry feedback
ros2 topic echo /odom
```

### Metrics to Check

1. **Tracking Error**: Distance from path to robot
   - Acceptable: < 0.5 m
   - Good: < 0.2 m
   - Excellent: < 0.1 m

2. **Oscillation**: Robot weaving side-to-side
   - Smooth: No visible weaving
   - Acceptable: Small weaving (±0.1 m)
   - Poor: Large weaving (±0.5 m)

3. **Speed Consistency**: Linear velocity variation
   - Steady: ±5% variation
   - Acceptable: ±10% variation
   - Poor: >±20% variation

4. **Turn Sharpness**: Angular velocity at waypoints
   - Smooth: Gradual increases/decreases
   - Jerky: Sudden spikes

---

## Advanced Tuning

### For Different Robot Types

#### Differential Drive (Turtlebot3)
```
lookahead_distance: 0.3-0.5   # Responsive
max_angular_velocity: 1.0      # Standard
```

#### Skid Steer (Clearpath Jackal)
```
lookahead_distance: 0.4-0.6   # More stable
max_angular_velocity: 1.5      # Higher capability
```

#### Ackermann Steering (Car-like)
```
lookahead_distance: 0.8-1.2   # Longer wheelbase
max_angular_velocity: 0.5      # Limited turn rate
```

### For Different Speeds

#### Slow (v = 0.1 m/s)
```
lookahead_distance: 0.2-0.3   # Close tracking
sampling_distance: 0.05        # Fine resolution
```

#### Medium (v = 0.3 m/s)
```
lookahead_distance: 0.4-0.6   # Balanced
sampling_distance: 0.1         # Standard
```

#### Fast (v = 1.0 m/s)
```
lookahead_distance: 0.8-1.2   # Far horizon
sampling_distance: 0.2         # Coarser is OK
```

---

## Debugging Parameter Issues

### Problem: Robot Goes in Circles
- **Cause**: Controller not converging
- **Fix**: 
  - Increase `lookahead_distance` (try 1.0m)
  - Decrease `linear_velocity`
  - Check `/odom` is publishing correctly

### Problem: Robot Oscillates Wildly
- **Cause**: Lookahead too short
- **Fix**: Increase `lookahead_distance` by 50%

### Problem: Robot Misses Waypoints
- **Cause**: Lookahead too long
- **Fix**: Decrease `lookahead_distance` by 50%

### Problem: Robot Stops Before End
- **Cause**: Incomplete trajectory
- **Fix**: Check `/trajectory` topic has enough points

### Problem: Jerky Motion
- **Cause**: Sampling too coarse
- **Fix**: Decrease `sampling_distance` to 0.05m
