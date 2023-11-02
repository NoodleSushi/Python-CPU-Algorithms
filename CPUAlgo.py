from abc import ABC, abstractmethod
from typing import Deque, Iterable, List, Optional, Set
import bisect
from collections import deque

from Process import Process


class CPUAlgo(ABC):
    NEGATIVE_PROCESS_TIME_ERROR = ValueError("process_time cannot be negative")
    PROCESS_TIME_AND_PROCESS_NONE_ERROR = ValueError("process_time and process cannot both be None")
    
    def __init__(self, processes: Iterable[Process] = []) -> None:
        self.__init_procs: List[Process] = []
        self.__proc_id_ctr: int = 0
        self.__unfinished_procs: Set[Process] = set()
        self.__incoming_procs: Deque[Process] = deque()
        self._arrived_procs: Deque[Process] = deque()
        self.__time: int = 0
        for process in processes:
            self.insert_process(process)
    
    @property
    def avg_turnaround_time(self) -> float:
        return sum(process.turnaround_time for process in self.__init_procs) / len(self.__init_procs)
    
    @property
    def avg_waiting_time(self) -> float:
        return sum(process.waiting_time for process in self.__init_procs) / len(self.__init_procs)
    
    @property
    def processes_list(self) -> List[Process]:
        return self.__init_procs
    
    def insert_process(self, process: Process) -> None:
        process.process_id = self.__proc_id_ctr
        bisect.insort(self.__init_procs, process, key=lambda x: x.arrival)
        self.__proc_id_ctr += 1
    
    def rewind(self) -> None:
        self._arrived_procs.clear()
        self.__time = 0
        for process in self.__init_procs:
            process.rewind()
    
    def __queue_arrived_processes(self) -> None:
        next_arrival = self.time_to_next_arrival()
        while next_arrival is not None and next_arrival <= 0:
            self._arrived_procs.append(self.__incoming_procs.popleft())
            next_arrival = self.time_to_next_arrival()
    
    def skip_to_next_arrival(self) -> None:
        next_arrival_time = self.time_to_next_arrival()
        if not self._arrived_procs and self.__incoming_procs and next_arrival_time is not None and next_arrival_time >= 0:
            if next_arrival_time > 0:
                self.process(next_arrival_time, None)
            while self.__incoming_procs and self.__incoming_procs[0].arrival == self.__time:
                self._arrived_procs.append(self.__incoming_procs.popleft())
    
    def time_to_next_arrival(self) -> Optional[int]:
        if not self.__incoming_procs:
            return None
        return self.__incoming_procs[0].arrival - self.__time
    
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
        
        self.__time += process_time
        print(process.name if process else 'BLANK', self.__time)
        return is_finished
    
    def _ready(self) -> None:
        self.rewind()
        self.__incoming_procs = deque(self.__init_procs)
        self.__unfinished_procs = set(self.__init_procs)
    
    def execute(self) -> None:
        self._ready()
        while self.__unfinished_procs:
            self.__queue_arrived_processes()
            self._update()

    @abstractmethod
    def _update(self) -> None:
        pass
