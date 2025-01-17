from PySide6.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QWidget

from core.qt_communication.common_signals import CommonSignals
from core.qt_communication.messages.MainWindow.Requests import SimplePrintRequest, UppercasePrintRequest
from core.qt_communication.messages.base import MessageBase


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.qt_signals = CommonSignals()

        # Set up the main window
        self.setWindowTitle("PySide6 Multiprocessing Playground")
        self.resize(400, 300)

        # Create the text output widget
        self.text_output = QTextEdit(self)
        self.text_output.setReadOnly(True)  # Make it read-only

        # Set up layout and central widget
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.text_output)
        self.setCentralWidget(central_widget)

        # Connect the signal to the output function
        self.qt_signals.main_window_request.connect(self.handle_request)
        # self.qt_signals.main_window_request.

    def handle_request(self, request: MessageBase):
        request_handlers = {
            SimplePrintRequest: self.output_text,
            UppercasePrintRequest: self.output_uppercase_text,
        }

        handler = request_handlers.get(type(request), None)
        if handler:
            handler(request)
        else:
            raise Exception

    def output_text(self, request: SimplePrintRequest):
        """Append received text to the QTextEdit."""
        self.text_output.append(request.message)

    def output_uppercase_text(self, request: UppercasePrintRequest):
        self.text_output.append(request.message.upper())
