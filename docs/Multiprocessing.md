# Multiprocessing 

![27May2025](27May2025_Multiprcessing.png)

World Model as a Multiprocessing Manager . which means : 

- gets shared across processes and keeps itself up-to-date
- you don't need to make a copy of the model, just parse in when creating the Multiprocess (for class / object)
- You will have to create handling function in World Model to handle access of vairable data

```python
e.g. use wm.get_latest_frame() instead of wm.frame_list.latest 
```

## How does the World Model stay up to date and prevents race Conditions ? 
In this case, we use an Integer (Manager.INT) to keep track of the version number in the World Model.
This means that :
- The world model will utilise the `Interval` variable to identify how often this version will be incremented (increased)
- The inteval is set to 5 frames for now, meaning that for every 5 new frames, the version value will be increased. 
- If your process is on version 3 and world model on version 4. we utilise this `Version Number` to call the `wm.get_latest_frame()` to get / update for set of frames
- Then we can keep using this set of frames to run our loop of process -> meaning that we get overflow in data. 
- Therefore, this might introduce a delay if your process is tiny, since we are receiving 60 frames per second (fps). 
- However, if your process is TOO LONG, it can also be that you might missed out on some versions. (but you can technically still get it via retriving a `list_of_frames()`, etc.)


**ALWAYS Remember that you cannot make a copy of World Model as it is not intended to be use this way ** You will break the auto update and everything to that process if you do so !!**

# Here are some common errors that you might bump into 

## ERROR : robot = 0 instead of a Robot Object
If you see the robot object being not an object but an INT, this means that the robot does not receive. 
This can happen due to one of the following reasons:
- There are 4 cameras and you are not utilising all of them
- There is no such robot on the game field
- There might be a frame drop on the vision that it cannot detect this robot. 

Therefore, if you would like, you can look on how you'd like to solve this using the FrameList class (this handles the frame storage, access, and retrieval).

## ERROR : Real life robots + SSL Vision, robot is running weird velocity
IF your robot is aiming at some where else on the field e.g. at the bottom right of the field, this might be caused by the ssl-vision thinking that there's a ball there. 
What it will do then is to output new fake ball positions, resulting in the proess in `remote_control_process.py` using the wrong ball value -> incorrect movement. 

This means that you will have to manually update your color calibration on the SSL vision software, check the masking area.

If you have a human on field (that is orange) make sure to cover your skin to make it invisible to the camera view. (otherwise, you're a ball)

# Status Update : 

As of 27 May. 2025, the Multiprocessing has been tested on robot chasing ball on field (using remote_control_process.py). 

