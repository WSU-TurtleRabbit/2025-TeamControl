# Manual for the Live Demonstration of A1

## General Settings
Before starting your demo, make sure the following conditions are met:

- Division setting: Set the division to Division B.
- Agents on the field: Remove all agents except the moving one from the field.

## goToPoint Improvements
To demonstrate your improved `goToPoint` function, please use `sandbox_process.py`.

Steps:
1. Place your agent inside one of the goals before starting the first run.
2. Run `sandbox_process.py` three times, each with a different target point.

Target Points:
- `target_position = (0, 0)`
- `target_position = (x1, y1)` ← replace with your chosen coordinates
- `target_position = (x2, y2)` ← replace with your chosen coordinates

## goalie
For the goalie demonstration, please configure your ball spawner with the following parameters:

```python
spawner = BallSpawner(
        division=’B’,
        ball_speed=5.0,
        goal_probability=0.75,
        seed=...,
    )
```    

During the Demo:
- The demonstration will be timed, and all teams will have equal time to present.
- Show how your goalie responds to the incoming balls.
- At the end of your run, please display the score counter. The objective is that the score is as small as possible meaning your goalie is very efficient at blocking incoming shots.

Good luck!