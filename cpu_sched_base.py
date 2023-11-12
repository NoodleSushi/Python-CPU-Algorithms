from abc import ABC, abstractmethod
from typing import Deque, Iterable, List, Optional, Set
import bisect
from collections import deque

from process import Process
from process_timeline import ProcessTimeline


class CPUSchedBase(ABC):
    NEGATIVE_PROCESS_TIME_ERROR = ValueError("process_time cannot be negative")
    PROCESS_TIME_AND_PROCESS_NONE_ERROR = ValueError("process_time and process cannot both be None")
    
    def __init__(self, processes: Iterable[Process] = []) -> None:
        self.__init_procs: List[Process] = []
        self.__proc_id_ctr: int = 0
        self.__unfinished_procs: Set[Process] = set()
        self.__incoming_procs: Deque[Process] = deque()
        self._arrived_procs: Deque[Process] = deque()
        self.__proc_timeline: ProcessTimeline = ProcessTimeline()
        self.__time: int = 0
        self.__has_executed: bool = False
        self.__is_executing: bool = False
        for process in processes:
            self.insert_process(process)
    
    def __was_executed(func):
        def wrapper(self, *args, **kwargs):
            if not self.__has_executed:
                raise RuntimeError(f"{func.__name__} cannot be called before before or during execution")
            return func(self, *args, **kwargs)
        return wrapper
        
    def __is_inside_update(func):
        def wrapper(self, *args, **kwargs):
            if not self.__is_executing:
                raise RuntimeError(f"{func.__name__} should be only called inside the _update() virtual method")
            return func(self, *args, **kwargs)
        return wrapper

    def __is_outside_update(func):
        def wrapper(self, *args, **kwargs):
            if self.__is_executing:
                raise RuntimeError(f"{func.__name__} should be only called outside the _update() virtual method")
            return func(self, *args, **kwargs)
        return wrapper

    @property
    @__was_executed
    def avg_turnaround_time(self) -> float:
        return sum(process.turnaround_time for process in self.__init_procs) / len(self.__init_procs)

    @property
    @__was_executed
    def avg_waiting_time(self) -> float:
        return sum(process.waiting_time for process in self.__init_procs) / len(self.__init_procs)
    
    @property
    @__was_executed
    def proc_timeline(self) -> ProcessTimeline:
        return self.__proc_timeline
    
    @property
    def processes_list(self) -> List[Process]:
        return self.__init_procs
    
    @property
    @__was_executed
    def cpu_utilization(self) -> float:
        return sum(process.burst for process in self.__init_procs)/self.__time
    
    @__is_outside_update
    def insert_process(self, process: Process) -> None:
        process.process_id = self.__proc_id_ctr
        bisect.insort(self.__init_procs, process, key=lambda x: x.arrival)
        self.__proc_id_ctr += 1
    
    @__is_outside_update
    def rewind(self) -> None:
        self.__unfinished_procs.clear()
        self.__incoming_procs.clear()
        self._arrived_procs.clear()
        self.__proc_timeline.clear()
        self.__time = 0
        for process in self.__init_procs:
            process.rewind()
    
    @__is_inside_update
    def __queue_arrived_processes(self) -> None:
        next_arrival = self.time_to_next_arrival()
        while next_arrival is not None and next_arrival <= 0:
            self._arrived_procs.append(self.__incoming_procs.popleft())
            next_arrival = self.time_to_next_arrival()
    
    @__is_inside_update
    def skip_to_next_arrival(self) -> None:
        next_arrival_time = self.time_to_next_arrival()
        if not self._arrived_procs and self.__incoming_procs and next_arrival_time is not None and next_arrival_time >= 0:
            if next_arrival_time > 0:
                self.process(next_arrival_time, None)
            while self.__incoming_procs and self.__incoming_procs[0].arrival == self.__time:
                self._arrived_procs.append(self.__incoming_procs.popleft())
    
    @__is_inside_update
    def time_to_next_arrival(self) -> Optional[int]:
        if not self.__incoming_procs:
            return None
        return self.__incoming_procs[0].arrival - self.__time
    
    @__is_inside_update
    def process(self, _process_time: int = -1, process: Optional[Process] = None) -> bool:
        if _process_time == -1 and process is None:
            raise CPUSchedBase.PROCESS_TIME_AND_PROCESS_NONE_ERROR
        if _process_time < 0 and _process_time != -1:
            raise CPUSchedBase.NEGATIVE_PROCESS_TIME_ERROR
        is_finished = False
        process_time = _process_time
        if process is not None:
            if _process_time == -1:
                process_time = process.burst_modified
            process_time = min(process_time, process.burst_modified)
            is_finished = process.process(self.__time, process_time)
            if is_finished:
                self.__unfinished_procs.remove(process)
        self.__proc_timeline.add_task(process, self.__time, self.__time + process_time)
        self.__time += process_time
        return is_finished

    @classmethod
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
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
    @__is_inside_update
    def _update(self) -> None:
        pass
