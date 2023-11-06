from typing import List, Optional
from dataclasses import dataclass
from collections.abc import Sequence

from Process import Process

@dataclass
class GanttTask:
    process: Optional[Process]
    start: int
    end: int

class GanttChart(Sequence):
    def __init__(self) -> None:
        self.__tasks: List[GanttTask] = []
        super().__init__()

    def add_task(self, process: Optional[Process], start: int, end: int) -> None:
        if (self.__tasks and self.__tasks[-1].end != start):
            raise ValueError("Invalid start time")
        elif (start >= end):
            raise ValueError("Invalid end time")
        self.__tasks.append(GanttTask(process, start, end))

    def clear(self) -> None:
        self.__tasks.clear()

    def __getitem__(self, index: int) -> GanttTask:
        return self.__tasks[index]

    def __len__(self) -> int:
        return len(self.__tasks)

    def __iter__(self):
        return iter(self.__tasks)
    
    def __str__(self) -> str:
        out = ""
        max_name_length = min(4, max(len(task.process.name) for task in self.__tasks) + 2)
        border = "-" * (max_name_length * len(self.__tasks) + len(self.__tasks) + 1)
        out += border + "\n"
        for task in self.__tasks:
            out += f"|{task.process.name.center(max_name_length)}"
        out += f"|\n{border}\n"
        for task in self.__tasks:
            out += str(task.start).ljust(max_name_length + 1)
        out += f"{str(task.end).ljust(max_name_length)}\n"
        return out
