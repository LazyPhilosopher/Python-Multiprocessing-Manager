import multiprocessing
from multiprocessing import Pipe
from typing import List

from PySide6.QtCore import QObject, QThread
from tabulate import tabulate

from core.modules.worker.Worker import Worker
from core.qt_communication.Task import Task
from core.qt_communication.common_signals import CommonSignals
from core.qt_communication.messages.MainWindow.Requests import SimplePrintRequest, UppercasePrintRequest
from core.qt_communication.messages.ProcessingModule.Requests import *
from core.qt_communication.messages.base import MessageBase
from core.utils.utils import count_from_k, long_task


class ProcessingModule(QObject):
    def __init__(self, process_count):
        super().__init__()
        self.qt_signals = CommonSignals()
        self.name = f"WorkerManager"
        self.max_processes = process_count
        self.pipe_read_thread = QThread

        self.pipe_read_thread = QThread()
        self.pipe_read_thread.started.connect(self.pipe_read_loop)
        self.pipe_read_thread.start()

        self.running_processes = []
        self.pipe_signal_dict = {}
        # self.pending_tasks = []
        self.pending_requests = []

        self.qt_signals.processing_module_request.connect(self.store_request)

        self.active_pipe_dict = {}
        self.pipe_callback_dict = {}

    def pipe_read_loop(self):
        while True:
            idx_range = range(0, len(self.pipe_callback_dict))
            for idx in idx_range:
                pipe: Pipe = list(self.pipe_callback_dict.keys())[idx]
                if pipe.poll():
                    msg = pipe.recv()
                    callback_dict = self.pipe_callback_dict[pipe]
                    callback_func = callback_dict["callback"]
                    signal = callback_dict["signal"]
                    message = callback_dict["message"]
                    signal.emit(message(callback_func(msg["data"])))

            for worker_process_info in self.running_processes:
                if not worker_process_info["process"].is_alive():
                    worker_uuid = worker_process_info["uuid"]
                    self.running_processes.remove(worker_process_info)
                    for child_pipe in self.active_pipe_dict[worker_uuid].keys():
                        parent_pipe = self.active_pipe_dict[worker_uuid][child_pipe]
                        self.pipe_callback_dict.pop(child_pipe)
                        parent_pipe.close()
                        child_pipe.close()

                    headers = ["Processes running", "Pipes open", "Remaining requests"]
                    data = [[len(self.running_processes), len( self.pipe_callback_dict), len(self.pending_requests)]]

                    print(tabulate(data, headers=headers, tablefmt="grid"))
                    self.assign_tasks()


    def store_request(self, request: MessageBase):
        if isinstance(request, List):
            list(map(self.pending_requests.append, request))
            pass
        else:
            self.pending_requests.append(request)
        self.assign_tasks()

    def assign_tasks(self):
        while len(self.running_processes) < self.max_processes:
            if not self.pending_requests:
                break

            req = self.pending_requests.pop(0)
            task_pipe_dict = self.parse_request_to_task(req)
            task = task_pipe_dict["task"]
            worker = Worker(task=task)
            self.active_pipe_dict[worker.uuid] = task_pipe_dict["active_pipe_dict"]
            self.pipe_callback_dict.update(task_pipe_dict["pipe_callback_dict"])
            # pass
            worker_process = multiprocessing.Process(target=worker.run)
            self.running_processes.append({"process": worker_process, "uuid": worker.uuid})
            worker_process.start()

    def parse_request_to_task(self, request: MessageBase) -> dict:
        request_handlers = {
            CountToKRequest: self.handle_count_to_k_request,
            LongTaskRequest: self._handle_long_task_request,
            # SSHKeyGenerationRequest: pass,
            # IntListGenerationRequest: pass
        }

        handler = request_handlers.get(type(request), None)
        if handler:
            task_pipe_dict: dict = handler(request)
            return task_pipe_dict
        raise Exception


    def handle_count_to_k_request(self, req: CountToKRequest) -> dict:
        func = count_from_k
        arg_dict = {"max_cnt": req.max_cnt}
        parent_print_conn, child_print_conn = Pipe(duplex=False)

        return {
            "task": Task(func=func,
                         arg_dict=arg_dict,
                         pipe_dict={
                             "print_pipe": child_print_conn
                         }),
            "pipe_callback_dict": {
                parent_print_conn: {
                    "callback": lambda x: f"**{x}**",
                    "signal": self.qt_signals.main_window_request,
                    "message": SimplePrintRequest}
            },
            "active_pipe_dict": {
                parent_print_conn: child_print_conn
            }
        }

    def _handle_long_task_request(self, req: LongTaskRequest) -> dict:
        func = long_task
        arg_dict = {"seed": req.seed}
        parent_wip_print_conn, child_wip_print_conn = Pipe(duplex=False)
        parent_done_print_conn, child_done_print_conn = Pipe(duplex=False)

        return {
            "task": Task(func=func,
                         arg_dict=arg_dict,
                         pipe_dict={
                             "wip_print_pipe": child_wip_print_conn,
                             "done_print_pipe": child_done_print_conn
                         }),
            "pipe_callback_dict": {
                parent_wip_print_conn: {
                    "callback": lambda x: f"WIP: {x}",
                    "signal": self.qt_signals.main_window_request,
                    "message": SimplePrintRequest},
                parent_done_print_conn: {
                    "callback": lambda x: f"{x}",
                    "signal": self.qt_signals.main_window_request,
                    "message": UppercasePrintRequest}
            },
            "active_pipe_dict": {
                parent_wip_print_conn: child_wip_print_conn,
                parent_done_print_conn: child_done_print_conn
            }
        }
