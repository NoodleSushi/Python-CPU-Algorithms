from typing import List, Optional
from dataclasses import dataclass
from collections.abc import Sequence

from process import Process

@dataclass
class ProcessTask:
    process: Optional[Process]
    start: int
    end: int

class ProcessTimeline(Sequence):
    def __init__(self) -> None:
        self.__tasks: List[ProcessTask] = []
        super().__init__()

    def add_task(self, process: Optional[Process], start: int, end: int) -> None:
        if (self.__tasks and self.__tasks[-1].end != start):
            raise ValueError("Invalid start time")
        elif (start >= end):
            raise ValueError("Invalid end time")
        self.__tasks.append(ProcessTask(process, start, end))

    def clear(self) -> None:
        self.__tasks.clear()

    def __getitem__(self, index: int) -> ProcessTask:
        return self.__tasks[index]

    def __len__(self) -> int:
        return len(self.__tasks)

    def __iter__(self):
        return iter(self.__tasks)
    
    def __str__(self) -> str:
        out = ""
        max_name_length = min(4, max(len(task.process.name if task.process else '──') for task in self.__tasks) + 2)
        border_top = "╭" + "─" * max_name_length + ("┬" + "─" * max_name_length) * (len(self.__tasks) - 1) + "╮"
        border_bot = "╰" + "─" * max_name_length + ("┴" + "─" * max_name_length) * (len(self.__tasks) - 1) + "╯"
        out += border_top + "\n"
        for task in self.__tasks:
            out += f"│{(task.process.name if task.process else '──').center(max_name_length)}"
        out += f"│\n{border_bot}\n"
        for task in self.__tasks:
            out += str(task.start).ljust(max_name_length + 1)
        out += f"{str(task.end).ljust(max_name_length)}\n"
        return out
