import sys
import time
import logging
import random

from PySide6.QtCore import QObject, QCoreApplication, QTimer
from multiprocessing import Process


# ANSI escape codes for coloring
COLOR_GREEN = "\033[92m"
COLOR_BLUE = "\033[94m"
COLOR_RESET = "\033[0m"


# Custom Log Formatter to color processName
class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.processName = f"{COLOR_GREEN}{record.processName}{COLOR_RESET}"
        return super().format(record)


# Configure logging to avoid overlapping output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(processName)s - PID:%(process)d] - %(message)s",
    datefmt="%H:%M:%S",
)

# Apply custom formatter
logger = logging.getLogger()
for handler in logger.handlers:
    handler.setFormatter(CustomFormatter('%(asctime)s - [%(processName)s - PID:%(process)d] - %(message)s', datefmt="%H:%M:%S"))


class Worker:
    def __init__(self, seconds):
        self.seconds = seconds

    def run(self):
        worker_name = f"{COLOR_BLUE}Worker {self.seconds} sec"
        logging.info(f"{worker_name}: {COLOR_BLUE}started.{COLOR_RESET}")
        for i in range(1, self.seconds + 1):
            logging.info(f"{worker_name}: {COLOR_BLUE}{i}{COLOR_RESET}")
            time.sleep(1)
        logging.info(f"{worker_name}: {COLOR_BLUE}finished.{COLOR_RESET}")


class WorkerManager(QObject):
    def __init__(self, process_count):
        super().__init__()
        # Colored name for MainProcess (WorkerManager)
        self.name = f"{COLOR_BLUE}WorkerManager"
        self.max_processes = process_count
        self.running_processes = []  # Store currently running worker processes
        self.pending_tasks = []  # Store pending tasks as a queue

        # Timer to periodically check for completed processes
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_running_processes)
        self.timer.start(100)  # Check every 100 ms

    def run_workers(self, int_list):
        # Queue up all tasks initially
        self.pending_tasks.extend(int_list)
        self._assign_tasks()

    def _assign_tasks(self):
        # Assign tasks if there are available slots
        while len(self.running_processes) < self.max_processes and self.pending_tasks:
            seconds = self.pending_tasks.pop(0)
            worker = Worker(seconds)

            # Start Worker in a new multiprocessing Process
            worker_process = Process(target=worker.run, name=f"{COLOR_GREEN}Worker_{seconds}_sec{COLOR_RESET}")
            worker_process.start()

            # Track the worker process
            self.running_processes.append(worker_process)
            logging.info(f"{self.name}: {COLOR_BLUE}Started Worker process for {seconds} seconds.{COLOR_RESET}")

    def _check_running_processes(self):
        # Check for completed processes
        for process in self.running_processes[:]:  # Copy list to allow modification
            if not process.is_alive():  # Process has finished
                process.join()  # Clean up the process
                self.running_processes.remove(process)
                logging.info(f"{self.name}: {COLOR_BLUE}Worker process completed and cleaned up.{COLOR_RESET}")

        # Assign more tasks if there are available slots
        self._assign_tasks()

        # Exit application if all tasks and processes are complete
        if not self.pending_tasks and not self.running_processes:
            logging.info(f"{self.name}: {COLOR_BLUE}All tasks completed. Exiting application.{COLOR_RESET}")
            self.timer.stop()
            QCoreApplication.quit()


if __name__ == "__main__":
    app = QCoreApplication(sys.argv)

    # Example usage
    manager = WorkerManager(process_count=5)
    int_list = random.choices(range(1, 50), k=20)
    manager.run_workers(int_list)

    sys.exit(app.exec())
