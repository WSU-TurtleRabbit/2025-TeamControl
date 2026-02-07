"""cmd_manager.py

This is used to keep track of the values within robot command
and pack and send command forward
"""

from TeamControl.network.robot_command import RobotCommand


class CommandManager:
    def __init__(self, isYellow, robot_id, dispatcher_q, run_time=1):
        self.isYellow = isYellow
        self.robot_id = robot_id
        self.output_queue = dispatcher_q
        self.vx = 0.0
        self.vy = 0.0
        self.w = 0.0
        self.dribble = False
        self.kick = False
        self.run_time = run_time  # second

    def __repr__(self):
        return str(self._to_command())

    def _to_command(self) -> RobotCommand:
        return RobotCommand(
            self.robot_id,
            self.vx,
            self.vy,
            self.w,
            self.kick,
            self.dribble,
            self.isYellow,
        )

    def update_command(self, **kwargs) -> None:
        self.vx = kwargs.get("vx", self.vx)
        self.vy = kwargs.get("vy", self.vy)
        self.w = kwargs.get("w", self.w)
        self.dribble = kwargs.get("dribble", self.dribble)
        self.kick = kwargs.get("kick", self.kick)
        self.run_time = kwargs.get("runtime", self.run_time)
        print("updated : ", kwargs)

    def pack_and_send(self) -> bool:
        """
        Pack and send the command to the dispatcher queue.
        return: True if the command is sent successfully, False otherwise.
        """
        command = self._to_command()
        if not self.output_queue.full():
            self.output_queue.put([command, self.run_time])
            # print("command sent", command)
            return True
        else:
            print("output queue is full")

        return False

    def clear(self):
        self.vx = 0
        self.vy = 0
        self.w = 0
        self.dribble = 0
        self.kick = 0 
        self.run_time = 1 
if __name__ == "__main__":
    from queue import Queue

    dispatcher_q = Queue()
    cmd_mgr = CommandManager(isYellow=True, robot_id=1, dispatcher_q=dispatcher_q)
    cmd_mgr.update_command(vx=0.0, vy=0.0, w=0.0, dribble=False, kick=False)
    cmd_mgr.update_command(dribble=True, kick=False)
    is_sent = cmd_mgr.pack_and_send()
    if is_sent:
        print("Command sent : ", cmd_mgr)
