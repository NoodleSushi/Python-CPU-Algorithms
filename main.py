from typing import Deque, Iterable, List, Optional
import bisect
from collections import deque

from tabulate import tabulate

from Process import Process
from CPUAlgo import CPUAlgo


class FCFS(CPUAlgo):
    def __init__(self, processes: Iterable[Process] = []) -> None:
        super().__init__(processes)
    
    def _ready(self) -> None:
        super()._ready()

    def _update(self):
        self.skip_to_next_arrival()
        while self._arrived_procs:
            self.process(-1, self._arrived_procs.popleft())


class SJF(CPUAlgo):
    def __init__(self, processes: Iterable[Process] = []) -> None:
        super().__init__(processes)
        self.__procs_list: List[Process] = []
    
    def _ready(self) -> None:
        super()._ready()
        self.__procs_list = []

    def _update(self):
        self.skip_to_next_arrival()
        while self._arrived_procs:
            bisect.insort(self.__procs_list, self._arrived_procs.popleft(), key=lambda x: x.burst)
        if self.__procs_list:
            self.process(-1, self.__procs_list.pop(0))


class SRTF(CPUAlgo):
    def __init__(self, processes: Iterable[Process] = []) -> None:
        super().__init__(processes)
        self.__procs_list: List[Process] = []
    
    def _ready(self) -> None:
        super()._ready()
        self.__procs_list = []

    def _update(self):
        if not self.__procs_list:
            self.skip_to_next_arrival()
        while self._arrived_procs:
            bisect.insort(self.__procs_list, self._arrived_procs.popleft(), key=lambda x: x.burst_modified)
        if self.__procs_list:
            process = self.__procs_list.pop(0)
            is_finished = self.process(self.time_to_next_arrival() or -1, process)
            if not is_finished:
                bisect.insort(self.__procs_list, process, key=lambda x: x.burst_modified)

class RR(CPUAlgo):
    def __init__(self, time_quantum: int, processes: Iterable[Process] = []) -> None:
        super().__init__(processes)
        self.time_quantum = time_quantum
        self.__procs_queue: Deque[Process] = deque()
        self.__process: Optional[Process] = None
    
    def _ready(self) -> None:
        super()._ready()
        self.__procs_queue = deque()
        self.__process = None
    
    def _update(self):
        if not self.__procs_queue or not self.__process:
            self.skip_to_next_arrival()
        while self._arrived_procs:
            self.__procs_queue.append(self._arrived_procs.popleft())
        if self.__procs_queue:
            if self.__process:
                self.__procs_queue.append(self.__process)
            self.__process = self.__procs_queue.popleft()
        if self.__process:
            is_finished = self.process(self.time_quantum, self.__process)
            if is_finished:
                self.__process = None

class PNP(CPUAlgo):
    def __init__(self, processes: Iterable[Process] = []) -> None:
        super().__init__(processes)
        self.__procs_list: List[Process] = []
    
    def _ready(self) -> None:
        super()._ready()
        self.__procs_list = []

    def _update(self):
        self.skip_to_next_arrival()
        while self._arrived_procs:
            bisect.insort(self.__procs_list, self._arrived_procs.popleft(), key=lambda x: x.priority)
        if self.__procs_list:
            self.process(-1, self.__procs_list.pop(0))

class PP(CPUAlgo):
    def __init__(self, processes: Iterable[Process] = []) -> None:
        super().__init__(processes)
        self.__procs_list: List[Process] = []
    
    def _ready(self) -> None:
        super()._ready()
        self.__procs_list = []

    def _update(self):
        if not self.__procs_list:
            self.skip_to_next_arrival()
        while self._arrived_procs:
            bisect.insort(self.__procs_list, self._arrived_procs.popleft(), key=lambda x: x.priority)
        if self.__procs_list:
            process = self.__procs_list[0]
            is_finished = self.process(self.time_to_next_arrival() or -1, process)
            if is_finished:
                self.__procs_list.pop(0)

def print_cpualgo(algo: CPUAlgo):
    print(tabulate(
        [
            [
                process.name,
                process.arrival,
                process.burst,
                process.end,
                process.turnaround_time,
                process.waiting_time,
            ]
            for process in algo.processes_list
        ],
        headers=[
            "Name",
            "Arrival Time",
            "Burst Time",
            "Finish Time",
            "Turnaround Time",
            "Waiting Time",
        ],
    ))

cpualgo = PP(
    [
        Process("A", 0, 8, 4),
        Process("B", 3, 4, 3),
        Process("C", 4, 5, 1),
        Process("D", 6, 3, 2),
        Process("E", 10, 2, 2),
    ]
)

cpualgo.execute()
print_cpualgo(cpualgo)
