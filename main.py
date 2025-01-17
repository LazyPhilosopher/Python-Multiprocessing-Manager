import random
import sys

from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication

from core.gui.MainWindow import MainWindow
from core.modules.ProcessingModule.ProcessingModule import ProcessingModule
from core.qt_communication.common_signals import CommonSignals
from core.qt_communication.messages.ProcessingModule.Requests import CountToKRequest, LongTaskRequest

if __name__ == "__main__":
    app = QApplication(sys.argv)

    qt_signals = CommonSignals()
    log_window = MainWindow()
    log_window.show()

    processing_thread = QThread()
    processing_module = ProcessingModule(process_count=16)  # Allow N parallel processes
    processing_module.moveToThread(processing_thread)

    processing_thread.start()

    requests = [*[CountToKRequest(max_cnt=cnt)
                  for cnt in random.choices(range(1, 10), k=50)],
                *[LongTaskRequest(seed=seed)
                  for seed in random.choices(range(1, 100), k=50)]]

    random.shuffle(requests)

    qt_signals.processing_module_request.emit(requests)

    sys.exit(app.exec())
