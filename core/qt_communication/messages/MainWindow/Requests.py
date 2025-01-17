from core.qt_communication.messages.base import MessageBase


class SimplePrintRequest(MessageBase):
    def __init__(self, message: str):
        super().__init__()
        self.message = message


class UppercasePrintRequest(MessageBase):
    def __init__(self, message: str):
        super().__init__()
        self.message = message


class StarredPrintRequest(MessageBase):
    def __init__(self, message: str):
        super().__init__()
        self.message = message
