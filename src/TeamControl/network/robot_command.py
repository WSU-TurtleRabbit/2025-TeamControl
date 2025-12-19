import time


class RobotCommand:
    def __init__(
        self,
        robot_id: int,
        vx: float = 0.0,
        vy: float = 0.0,
        w: float = 0.0,
        kick: int = 0,
        dribble: int = 0,
        time_origin: float = 0.0,
    ):
        self.time_set: float = time.time()
        self.robot_id: int = int(robot_id)
        self.vx: float = float(vx)
        self.vy: float = float(vy)
        self.w: float = float(w)
        self.kick: int = int(kick)
        self.dribble: int = int(dribble)
        self.time_origin: float = float(time_origin)

    def __str__(self) -> str:
        return f"{self.robot_id} {self.vx} {self.vy} {self.w} {self.kick} {self.dribble} {self.time_set}"

    def encode(self) -> bytes:
        return bytes(str(self).encode("utf-8"))

    @classmethod
    def decode(cls, command_msg: str | bytes):
        if isinstance(command_msg, bytes):
            command_msg = command_msg.decode()

        robot_id, vx, vy, w, kick, dribble, time_origin = command_msg.split(" ")
        return RobotCommand(
            int(robot_id),
            float(vx),
            float(vy),
            float(w),
            int(kick),
            int(dribble),
            float(time_origin),
        )
