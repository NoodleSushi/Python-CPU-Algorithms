from typing import Deque, Iterable, List, Optional
import bisect
from collections import deque

from process_timeline import Process
from cpu_sched_base import CPUSchedBase


class FCFSSched(CPUSchedBase):
    def __init__(self, processes: Iterable[Process] = []) -> None:
        super().__init__(processes)
    
    @classmethod
    @property
    def name(self) -> str:
        return "First Come First Serve"

    def _update(self):
        self.skip_to_next_arrival()
        while self._arrived_procs:
            self.process(-1, self._arrived_procs.popleft())


class SJFSched(CPUSchedBase):
    def __init__(self, processes: Iterable[Process] = []) -> None:
        super().__init__(processes)
        self.__procs_list: List[Process] = []

    @classmethod
    @property
    def name(self) -> str:
        return "Shortest Job First"
    
    def _ready(self) -> None:
        super()._ready()
        self.__procs_list = []

    def _update(self):
        if not self.__procs_list:
            self.skip_to_next_arrival()
        while self._arrived_procs:
            bisect.insort(self.__procs_list, self._arrived_procs.popleft(), key=lambda x: x.burst)
        if self.__procs_list:
            self.process(-1, self.__procs_list.pop(0))


class SRTFSched(CPUSchedBase):
    def __init__(self, processes: Iterable[Process] = []) -> None:
        super().__init__(processes)
        self.__procs_list: List[Process] = []
    
    @classmethod
    @property
    def name(self) -> str:
        return "Shortest Remaining Time First"
    
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

class RRSched(CPUSchedBase):
    def __init__(self, time_quantum: int, processes: Iterable[Process] = []) -> None:
        super().__init__(processes)
        self.time_quantum = time_quantum
        self.__procs_queue: Deque[Process] = deque()
        self.__process: Optional[Process] = None
    
    @classmethod
    @property
    def name(self) -> str:
        return "Round Robin"
    
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

class PNPSched(CPUSchedBase):
    def __init__(self, processes: Iterable[Process] = []) -> None:
        super().__init__(processes)
        self.__procs_list: List[Process] = []
    
    @classmethod
    @property
    def name(self) -> str:
        return "Priority Non-Preemptive"
    
    def _ready(self) -> None:
        super()._ready()
        self.__procs_list = []

    def _update(self):
        if not self.__procs_list:
            self.skip_to_next_arrival()
        while self._arrived_procs:
            bisect.insort(self.__procs_list, self._arrived_procs.popleft(), key=lambda x: x.priority)
        if self.__procs_list:
            self.process(-1, self.__procs_list.pop(0))

class PPSched(CPUSchedBase):
    def __init__(self, processes: Iterable[Process] = []) -> None:
        super().__init__(processes)
        self.__procs_list: List[Process] = []
    
    @classmethod
    @property
    def name(self) -> str:
        return "Priority Based Scheduling"
    
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
