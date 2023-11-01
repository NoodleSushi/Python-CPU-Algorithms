class Process:
    ERR_TIME_PROCESSED = ValueError("time_processed must be greater than 0")
    ERR_ALREADY_FINISHED = RuntimeError("process has already finished")
    ERR_WILL_FINISH = RuntimeError("process will finish before time_processed")
    ERR_NOT_FINISHED = RuntimeError("process has not finished")

    def __init__(self, name: str, arrival: int, burst: int, priority: int = 0) -> None:
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.burst_modified: int = burst
        self.priority = priority
        self.end: int = -1
        self.process_id: int = -1

    def rewind(self) -> None:
        self.burst_modified = self.burst
        self.end = -1

    def process(self, current_time: int, time_processed: int) -> bool:
        if time_processed <= 0:
            raise Process.ERR_TIME_PROCESSED
        if self.burst_modified <= 0:
            raise Process.ERR_ALREADY_FINISHED
        if self.burst_modified < time_processed:
            raise Process.ERR_WILL_FINISH
        self.burst_modified = self.burst_modified - time_processed
        if self.burst_modified <= 0:
            self.end = current_time + self.burst_modified + time_processed
            return True
        return False

    @property
    def turnaround_time(self) -> int:
        if self.end == -1:
            raise Process.ERR_NOT_FINISHED
        return self.end - self.arrival

    @property
    def waiting_time(self) -> int:
        if self.end == -1:
            raise Process.ERR_NOT_FINISHED
        return self.turnaround_time - self.burst