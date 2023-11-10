import shutil
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
        width = shutil.get_terminal_size().columns
        max_name_length = min(4, max(len(task.process.name if task.process else '──') for task in self.__tasks) + 2)
        max_cell_length = max_name_length + 1
        cells_per_row = (width // max_cell_length) - 1
        begin_spaces = " " * ((width - ((max_cell_length * cells_per_row) + len(str(self.__tasks[-1].end)))) // 2)
        for i in range(0, len(self.__tasks), cells_per_row):
            tasks = self.__tasks[i:i + cells_per_row]
            border_top = begin_spaces + "╭" + "─" * max_name_length + ("┬" + "─" * max_name_length) * (len(tasks) - 1) + "╮"
            border_bot = begin_spaces + "╰" + "─" * max_name_length + ("┴" + "─" * max_name_length) * (len(tasks) - 1) + "╯"
            out += border_top + "\n" + begin_spaces
            for task in tasks:
                out += f"│{(task.process.name if task.process else '──').center(max_name_length)}"
            out += f"│\n{border_bot}\n{begin_spaces}"
            for task in tasks:
                out += str(task.start).ljust(max_name_length + 1)
            out += f"{str(task.end).ljust(max_name_length)}\n"
        return out
