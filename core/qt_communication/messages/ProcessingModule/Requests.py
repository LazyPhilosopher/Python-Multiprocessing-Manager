from core.qt_communication.messages.base import MessageBase


class CountToKRequest(MessageBase):
    def __init__(self, max_cnt: int):
        super().__init__()
        self.max_cnt = max_cnt


class LongTaskRequest(MessageBase):
    def __init__(self, seed: int):
        super().__init__()
        self.seed = seed


class SSHKeyGenerationRequest(MessageBase):
    def __init__(self, seed: int):
        super().__init__()
        self.seed = seed


class IntListGenerationRequest(MessageBase):
    def __init__(self, max_val: int):
        super().__init__()
        self.max_val = max_val
