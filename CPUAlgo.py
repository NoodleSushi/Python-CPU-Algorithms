from abc import ABC, abstractmethod
from typing import Deque, Iterable, List, Optional, Set
import bisect
from collections import deque

from Process import Process
from GanttChart import GanttChart


class CPUAlgo(ABC):
    NEGATIVE_PROCESS_TIME_ERROR = ValueError("process_time cannot be negative")
    PROCESS_TIME_AND_PROCESS_NONE_ERROR = ValueError("process_time and process cannot both be None")
    
    def __init__(self, processes: Iterable[Process] = []) -> None:
        self.__init_procs: List[Process] = []
        self.__proc_id_ctr: int = 0
        self.__unfinished_procs: Set[Process] = set()
        self.__incoming_procs: Deque[Process] = deque()
        self._arrived_procs: Deque[Process] = deque()
        self.__gantt_chart: GanttChart = GanttChart()
        self.__time: int = 0
        self.__has_executed: bool = False
        self.__is_executing: bool = False
        for process in processes:
            self.insert_process(process)
    
    def __check_was_executed(func):
        def wrapper(self, *args, **kwargs):
            if not self.__has_executed:
                raise RuntimeError(f"{func.__name__} cannot be called before before or during execution")
            return func(self, *args, **kwargs)
        return wrapper
        
    def __check_is_executing(func):
        def wrapper(self, *args, **kwargs):
            if not self.__is_executing:
                raise RuntimeError(f"{func.__name__} should be only called within the _update() virtual method")
            return func(self, *args, **kwargs)
        return wrapper

    def __check_isnt_executing(func):
        def wrapper(self, *args, **kwargs):
            if self.__is_executing:
                raise RuntimeError(f"{func.__name__} should not be called within the _update() virtual method")
            return func(self, *args, **kwargs)
        return wrapper
    
    @property
    @__check_was_executed
    def total_turnaround_time(self) -> int:
        return sum(process.turnaround_time for process in self.__init_procs)

    @property
    @__check_was_executed
    def avg_turnaround_time(self) -> float:
        return self.total_turnaround_time / len(self.__init_procs)
    
    @property
    @__check_was_executed
    def total_waiting_time(self) -> int:
        return sum(process.waiting_time for process in self.__init_procs)

    @property
    @__check_was_executed
    def avg_waiting_time(self) -> float:
        return self.total_waiting_time / len(self.__init_procs)
    
    @property
    @__check_was_executed
    def gantt_chart(self) -> GanttChart:
        return self.__gantt_chart
    
    @property
    def processes_list(self) -> List[Process]:
        return self.__init_procs
    
    @__check_isnt_executing
    def insert_process(self, process: Process) -> None:
        process.process_id = self.__proc_id_ctr
        bisect.insort(self.__init_procs, process, key=lambda x: x.arrival)
        self.__proc_id_ctr += 1
    
    @__check_isnt_executing
    def rewind(self) -> None:
        self._arrived_procs.clear()
        self.__time = 0
        for process in self.__init_procs:
            process.rewind()
    
    @__check_is_executing
    def __queue_arrived_processes(self) -> None:
        next_arrival = self.time_to_next_arrival()
        while next_arrival is not None and next_arrival <= 0:
            self._arrived_procs.append(self.__incoming_procs.popleft())
            next_arrival = self.time_to_next_arrival()
    
    @__check_is_executing
    def skip_to_next_arrival(self) -> None:
        next_arrival_time = self.time_to_next_arrival()
        if not self._arrived_procs and self.__incoming_procs and next_arrival_time is not None and next_arrival_time >= 0:
            if next_arrival_time > 0:
                self.process(next_arrival_time, None)
            while self.__incoming_procs and self.__incoming_procs[0].arrival == self.__time:
                self._arrived_procs.append(self.__incoming_procs.popleft())
    
    @__check_is_executing
    def time_to_next_arrival(self) -> Optional[int]:
        if not self.__incoming_procs:
            return None
        return self.__incoming_procs[0].arrival - self.__time
    
    @__check_is_executing
    def process(self, _process_time: int = -1, process: Optional[Process] = None) -> bool:
        if _process_time == -1 and process is None:
            raise CPUAlgo.PROCESS_TIME_AND_PROCESS_NONE_ERROR
        if _process_time < 0 and _process_time != -1:
            raise CPUAlgo.NEGATIVE_PROCESS_TIME_ERROR
        is_finished = False
        process_time = _process_time
        if process is not None:
            if _process_time == -1:
                process_time = process.burst_modified
            process_time = min(process_time, process.burst_modified)
            is_finished = process.process(self.__time, process_time)
            if is_finished:
                self.__unfinished_procs.remove(process)
        self.__gantt_chart.add_task(process, self.__time, self.__time + process_time)
        self.__time += process_time
        return is_finished
    
    def _ready(self) -> None:
        self.rewind()
        self.__incoming_procs = deque(self.__init_procs)
        self.__unfinished_procs = set(self.__init_procs)
        self.__has_executed = False
    
    def execute(self) -> None:
        self._ready()
        while self.__unfinished_procs:
            self.__is_executing = True
            self.__queue_arrived_processes()
            self._update()
            self.__is_executing = False
        self.__has_executed = True

    @abstractmethod
    @__check_is_executing
    def _update(self) -> None:
        pass
