# Manual for the Live Demonstration of A2

## General Settings
Before starting your demo, make sure the following conditions are met:

- Division setting: Set the division to Division B.
- Agents on the field: Remove all agents except the moving ones from the field.

## Shooting
To demonstrate your improved shooting behavior, please use `striker_process.py`.

Please configure your idle ball spawner with the following parameters:
---
In `ball_idle_spawner.py` replace
```python
class BallIdleSpawner:
    test_scenarios = []
```

with 
```python
class BallIdleSpawner:
    test_scenarios = [(2, -0.5), (3.5, -1.5), (3.9, 1.8), (1, 0), (0.5, 0), (0.1, 0.2)]
```
---
In `striker_process.py` make sure you have the following settings:

```python
DIVISION = 'B'
...
spawner = BallIdleSpawner(
        division=DIVISION
    )
```
---
Please set the time limit in `striker_process.py` to 90s.
```python
while time.time() - start_time < 90:
    ...
```
---

During the Demo:
- The demonstration will be timed, and all teams will have equal time to present. This is implemented by the timer directly in `striker_process.py`
- Show how your striker can score goals.
- At the end of your run, please display the score counter. The objective is that the score is as high as possible.

Good luck!
