from uuid import uuid4

from core.qt_communication.Task import Task

# ANSI escape codes for coloring
COLOR_GREEN = "\033[92m"
COLOR_BLUE = "\033[94m"
COLOR_RESET = "\033[0m"

class Worker:
    def __init__(self, task: Task):
        self.func = task.func
        self.arg_dict = task.arg_dict
        self.pipe_dict = task.pipe_dict
        self.uuid = uuid4()

    def run(self):
        self.func(self.uuid, self.arg_dict, self.pipe_dict)
