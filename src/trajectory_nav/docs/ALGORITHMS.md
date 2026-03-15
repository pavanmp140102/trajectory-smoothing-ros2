# Algorithms & Control Law

## Cubic Spline Interpolation (Spline Smoother)

### Problem
Given discrete waypoints, create a smooth continuous path without sharp kinks.

### Solution: Cubic Spline with Arc-Length Parameterization

#### Step 1: Arc-Length Parameterization
Convert waypoints to arc-length parameter space:

```
Waypoints: [(x₀, y₀), (x₁, y₁), (x₂, y₂), ...]

Arc-length: s = 0 → s₁ → s₂ → ...
where sᵢ = cumsum(distance between consecutive points)
```

**Why?** Arc-length parameterization ensures consistent interpolation even when waypoints are unevenly spaced.

#### Step 2: Fit Cubic Splines

For x-coordinates:
```
xₛ(s) = CubicSpline(s, x_values, bc_type='natural')
```

For y-coordinates:
```
yₛ(s) = CubicSpline(s, y_values, bc_type='natural')
```

**Properties:**
- C² continuous (smooth position and curvature)
- Natural boundary conditions (zero second derivative at ends)
- Numerically stable

#### Step 3: Dense Sampling

Sample at high density (100 points default):
```
s_dense = linspace(s_min, s_max, 100)
x_smooth = xₛ(s_dense)
y_smooth = yₛ(s_dense)
```

**Result**: Smooth path with no sharp turns.

### Code Example

```python
from scipy.interpolate import CubicSpline
import numpy as np

# Waypoints
x = np.array([0.0, 2.0, 4.0, 6.0])
y = np.array([0.0, 2.0, 0.0, 2.0])

# Arc-length parameterization
distances = np.sqrt(np.diff(x)**2 + np.diff(y)**2)
s = np.concatenate(([0], np.cumsum(distances)))

# Spline fit
spline_x = CubicSpline(s, x, bc_type='natural')
spline_y = CubicSpline(s, y, bc_type='natural')

# Dense sampling
s_smooth = np.linspace(s.min(), s.max(), 100)
x_smooth = spline_x(s_smooth)
y_smooth = spline_y(s_smooth)
```

---

## Trajectory Generation: Time Parameterization

### Problem
Convert smooth path (x, y) into a trajectory with timing information.

### Solution

#### Step 1: Resample at Fixed Spatial Intervals

Sample every `Δs = 0.05m`:

```
trajectory = []
for i in range(len(path) - 1):
    distance = ||path[i+1] - path[i]||
    samples = ceil(distance / Δs)
    for j in range(1, samples + 1):
        t = j / samples
        p_sample = path[i] + t * (path[i+1] - path[i])
        trajectory.append(p_sample)
```

**Why?** Fixed spatial sampling ensures consistent control update rates.

#### Step 2: Assign Timestamps

Use constant velocity `v = 0.3 m/s`:

```
t = 0
for i in range(len(trajectory)):
    if i > 0:
        d = ||trajectory[i] - trajectory[i-1]||
        t += d / v
    trajectory[i].time = t
```

**Result**: Trajectory with timing `(x, y, t)` at each point.

### Code Example

```python
import numpy as np

def generate_trajectory(path, sampling_distance=0.05, velocity=0.3):
    trajectory = []
    current_time = 0.0
    
    # Spatial resampling
    for i in range(len(path) - 1):
        segment = path[i+1] - path[i]
        length = np.linalg.norm(segment)
        samples = max(1, int(np.ceil(length / sampling_distance)))
        
        for j in range(samples):
            t = j / samples
            point = path[i] + t * segment
            trajectory.append((point, current_time))
            
            # Update time for next point
            if j < samples - 1:
                current_time += sampling_distance / velocity
    
    return trajectory
```

---

## Pure Pursuit Control Law

### Problem
How to steer a differential drive robot to follow a trajectory?

### Solution: Pure Pursuit Algorithm

#### Principle

1. **Lookahead**: Select a point at distance `L` ahead on the trajectory
2. **Compute angle**: Find angle from robot heading to lookahead point
3. **Steer**: Proportional angular velocity based on angle error

#### Control Law

```
α = atan2(y_target - y_robot, x_target - x_robot) - θ_robot

ω = (2v sin(α)) / L
```

Where:
- `α`: angle error to target
- `v`: linear velocity (0.3 m/s)
- `L`: lookahead distance (0.5 m)
- `ω`: angular velocity command

#### Geometry

```
Robot Frame (θ = 0):

          Target (L away)
                *
               /|
              / |
             /  | α (angle to target)
            /   |
           /___ |
          Robot heading (θ)

α = atan2(Δy, Δx) - θ
```

#### Behavior

| Condition | Behavior |
|-----------|----------|
| α ≈ 0° | Straight ahead → ω ≈ 0 |
| α = 45° | Turn right | Large positive ω |
| α = -45° | Turn left | Large negative ω |
| α = 90° | Sharp turn | Maximum ω |

#### Tuning Parameters

- **Lookahead Distance `L`**:
  - Small L (0.2m): Tighter tracking, more oscillation
  - Large L (1.0m): Smoother path, slower convergence
  - Default: 0.5m (good balance)

- **Linear Velocity `v`**:
  - Higher v: Faster but less precise
  - Lower v: Slower but better tracking
  - Default: 0.3 m/s

- **Max Angular Velocity `ω_max`**:
  - Limits sharp turns
  - Default: 1.0 rad/s

### Code Example

```python
import math

def pure_pursuit_control(robot_x, robot_y, robot_theta, 
                        target_x, target_y, 
                        v=0.3, L=0.5, max_omega=1.0):
    
    # Compute angle to target
    angle_to_target = math.atan2(target_y - robot_y, 
                                 target_x - robot_x)
    
    # Angle error (normalized to [-π, π])
    alpha = angle_to_target - robot_theta
    alpha = math.atan2(math.sin(alpha), math.cos(alpha))
    
    # Pure pursuit control law
    omega = (2 * v * math.sin(alpha)) / L
    
    # Clamp angular velocity
    omega = max(-max_omega, min(max_omega, omega))
    
    return v, omega
```

---

## Comparison of Approaches

| Aspect | Our Approach | Alternatives |
|--------|--------------|--------------|
| **Smoothing** | Arc-length cubic spline | Bezier, polynomial fit, RBF |
| **Trajectory** | Fixed spatial sampling | Time-optimal, velocity profiles |
| **Control** | Pure pursuit | Stanley, MPC, PID, LQR |
| **Complexity** | Low-Medium | Medium-High |
| **Robustness** | Good for simulation | Better for real robots |
| **Tuning** | 3 parameters | 5-20+ parameters |

---

## Mathematical Notation

| Symbol | Meaning | Unit |
|--------|---------|------|
| `(x, y)` | 2D Cartesian position | meters |
| `θ` | Robot heading (yaw angle) | radians |
| `v` | Linear velocity | m/s |
| `ω` | Angular velocity | rad/s |
| `L` | Lookahead distance | meters |
| `s` | Arc-length parameter | meters |
| `t` | Time | seconds |
| `α` | Angle error | radians |
