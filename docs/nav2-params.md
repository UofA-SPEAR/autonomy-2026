# **Overview - Config**
explaination on parameters in [nav2_params.yaml](build/rc_car_navigation/config/nav2_params.yaml)  
Note: variables will be **bolded** and func will be *italicize* for convence of reference  
# Core Servers *using all*  
behaviour tree

# Planners Plugin:  
[Smac Hybrid-A* Planner](https://docs.nav2.org/configuration/packages/smac/configuring-smac-hybrid.html)  

# Controller Plugin:  
[MPPI Controller](https://docs.nav2.org/configuration/packages/configuring-mppic.html)  

## Main idea:  
- sim thousands of possible trajectories into future
- pick on that best follows the path while avoiding obstacles
- accounts for physics of rover ie. cannot turn in place without some momentum

Note: we are trying to minimize the cost of choosing a best path out of a bunch of more costly paths, by pred the future (simulating with algo)

## Core Algorithm
1. Generate N random trajectories (N = **batch_size**)
2. Simulate each trajectory T seconds into the future (T = **time_steps** × **model_dt**)
3. Score each trajectory (lower cost = better)
4. Pick the best trajectory (weighted by temperature)
5. Execute ONLY the first Δt step (Δt = **model_dt**)
6. Throw away the rest and repeat from step 1

Only the FIRST tiny step (Δt) is executed. Then MPPI re-plans with updated rover position.

## Cost minimization  
Total Cost = path_distance² + 1/obstacle_distance + goal_distance² + acceleration² + jerk²  
ex.  
Trajectory A: Total cost = 12.5 (bad)  
Trajectory B: Total cost = 3.2  (best!) ✓  
Trajectory C: Total cost = 7.8  (okay)  

MPPI picks B (minimum cost)

## DEBUGGING with RViz  
helpful to mess around with *TrajectoryVisualizer*  
ex. change in path pts, when time_step changes  

time_step = 1:  Rover → ●●●●●●●●●●●●●●● → Future  (all points)  
time_step = 3:  Rover → ●   ●   ●   ●   ● → Future  (every 3rd)  
time_step = 10: Rover → ●       ●       ● → Future  (every 10th)  

## Critics  
*ConstraintCritic*: Filter out impossible trajectories  
Rejects trajectories that:  
- Exceed velocity limits (v > v_max)
- Exceed acceleration limits (a > a_max)
- Turn radius too tight (R < min_turning_r)
- Collide with obstacles

Cost: ∞ (reject) if violated, 0 if valid  

*GoalCritic*: Ensure correct final orientation  
Cost = distance_to_goal²  

Example:  
  End 0.5m from goal → cost = 0.25  
  End 2.0m from goal → cost = 4.0  

*GoalAngleCritic*: Ensure correct final orientation  
Cost = (θ_final - θ_goal)²  

Example:  
  Final heading: 88°, Goal: 90° → cost = 2² = 4  
  Final heading: 45°, Goal: 90° → cost = 45² = 2025  

*CostCritic*: General quality assessment  
Evaluates:  
- Distance to obstacles
- Smoothness of motion
- Energy efficiency

Cost: Higher for dangerous/inefficient paths

*PathAlignCritic*: Stay aligned with planned path direction  
Measures angle between:  
- Trajectory heading at each point
- Path heading at nearest path point

Cost = Σ (angle_difference²)  

*PathFollowCritic*: How close does trajectory stay to the path?  
Cost = Σ distance_to_path²  

Example:  
  Stay 0.1m from path → cost = 0.01  
  Drift 0.5m from path → cost = 0.25  

*PathAngleCritic*: Face the right direction while following path  
At each point:  
  Cost += (robot_heading - path_tangent_angle)²  

Example:  
  Path goes east (0°), robot heading 5° → small cost  
  Path goes east (0°), robot heading 45° → large cost  

*PreferForwardCritic*: Bias toward forward motion (backward only when necessary)  
Cost = 0 if velocity > 0 (forward)  
Cost = penalty if velocity < 0 (backward)  

Example:  
  v = 1.0 m/s → cost = 0 (good)  
  v = -0.3 m/s → cost = penalty (discouraged)  

# Smoother Plugin:  
[Savitzky-Golay Smoother](https://docs.nav2.org/configuration/packages/configuring-savitzky-golay-smoother.html)
