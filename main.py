from typing import Any, Callable, List, Optional, TypeVar
import questionary
import re
import argparse
from rich.console import Console
from rich.table import Table
from rich.highlighter import ReprHighlighter
from rich.text import Text
from rich import box

from cpu_sched_base import CPUSchedBase
import cpu_sched_algos as algos
from process import Process

console = Console()

algos_lookup: List[CPUSchedBase] = [
    algos.FCFSSched,
    algos.SJFSched,
    algos.SRTFSched,
    algos.RRSched,
    algos.PNPSched,
    algos.PPSched,
]

kv_algos_lookup = {algo.name: algo for algo in algos_lookup}

# COMMANDLINE ARGS

parser = argparse.ArgumentParser(description='CPU Scheduling Solver')
parser.add_argument('--algo', type=str, help='CPU Scheduling Algorithm')
parser.add_argument('--arrival', type=str, help='Arrival Times')
parser.add_argument('--burst', type=str, help='Burst Times')
parser.add_argument('--priority', type=str, help='Priorities')
parser.add_argument('--quantum', type=int, help='Time Quantum')

args = parser.parse_args()
vargs = vars(args)

# SELECT ALGORITHM
console.clear()

SelectedAlgo = None

if args.algo:
    if args.algo not in kv_algos_lookup:
        console.print('Invalid algorithm')
        exit(1)
    SelectedAlgo = kv_algos_lookup[args.algo]
else:
    SelectedAlgo = questionary.select(
        "Select an algorithm",
        choices=[questionary.Choice(algo.name, algo) for algo in algos_lookup],
    ).ask()


# SELECT PROCESSES
console.clear()

def multinum_parser(text: Optional[str]) -> Optional[List[int]]:
    if text is None:
        return None
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]

def multinum_validator(allow_zeroes=False) -> Callable[[str], bool]:
    def wrapper(text: str):
        if allow_zeroes:
            return re.match(r'^\d+(?:\s+\d+)*$', text) is not None
        return re.match(r'^[1-9][0-9]*(?:\s+[1-9][0-9]*)*$', text) is not None
    return wrapper

def variable_multinum_validator(length: int, allow_zeroes=False) -> Callable[[str], bool]:
    def wrapper(text: str):
        return multinum_validator(allow_zeroes)(text) and len(multinum_parser(text)) == length
    return wrapper

def get_input(prompt: str, meta_prompt: str, validator: Callable[[str], bool], parser: Callable[[str], Any]) -> Optional[Any]:
    if vargs and bool(text := vargs.get(prompt)):
        if validator(text):
            return parser(text)
        else:
            console.print(f'Invalid {meta_prompt}')
            exit(1)
    else:
        return parser(questionary.text(
            f"Input {meta_prompt}. Press Ctrl+C to exit.\n", 
            validate=validator
        ).ask())

def get_multinum_input(prompt: str, meta_prompt: str, validator: Callable[[str], bool]) -> Optional[List[int]]:
    return get_input(prompt, meta_prompt, validator, multinum_parser)

def get_num_input(prompt, meta_prompt: str, validator: Callable[[str], bool]) -> Optional[int]:
    return get_input(prompt, meta_prompt, validator, int)


T = TypeVar('T')

def gen_on_condition(bool: bool, generator: Callable[[], T], default) -> T:
    if bool:
        return generator()
    return default

time_quantum = gen_on_condition(
    SelectedAlgo == algos.RRSched, 
    lambda: get_num_input('quantum', 'Time Quantum', lambda x: (isinstance(x, int) or bool(re.match(r'^\d+$', x))) and int(x) >= 0),
    0
)
arrival_times = get_multinum_input('arrival', 'Arrival Times (space-separated)', multinum_validator(True))
burst_times = get_multinum_input('burst', 'Burst Times (space-separated)',variable_multinum_validator(len(arrival_times)))
priorities = gen_on_condition(
    SelectedAlgo in [algos.PNPSched, algos.PPSched], 
    lambda: get_multinum_input('priority', 'Priorities (space-separated)', variable_multinum_validator(len(arrival_times), True)),
    [0 for _ in range(len(arrival_times))]
)

processes = []

for i, (arrival, burst, priorities) in enumerate(zip(arrival_times, burst_times, priorities)):
    processes.append(Process(f'P{i+1}', arrival, burst, priorities))

# EXECUTE ALGORITHM
console.clear()

cpualgo: algos.CPUSchedBase = algos.RRSched(time_quantum, processes) if SelectedAlgo == algos.RRSched else SelectedAlgo(processes)

def print_cpu_sched_table(console: Console, algo: CPUSchedBase):
    table = Table(
        title=algo.name, 
        safe_box=False,
        show_lines=True,
        box=box.ROUNDED,
        caption=f"Time Quantum: {cpualgo.time_quantum}" if isinstance(cpualgo, algos.RRSched) else None
    )
    table.add_column("Process ID", justify="center", style="red")
    headers = [
        "Arrival Time",
        "Burst Time",
        "Ending Time",
        "Turnaround Time",
        "Waiting Time",
    ]
    if isinstance(cpualgo, (algos.PNPSched, algos.PPSched)):
        headers.insert(0, "Priority")
    for header in headers:
        table.add_column(header, justify="center")
    for process in sorted(algo.processes_list, key=lambda x: x.process_id):
        row = [
            process.name, 
            str(process.arrival), 
            str(process.burst), 
            str(process.end), 
            str(process.turnaround_time), 
            str(process.waiting_time)
        ]
        if isinstance(cpualgo, (algos.PNPSched, algos.PPSched)):
            row.insert(1, str(process.priority))
        table.add_row(*row)
    console.print(table)

cpualgo.execute()
console.print()
if isinstance(cpualgo, algos.RRSched):
    console.print(f"Time Quantum: {cpualgo.time_quantum}")
print_cpu_sched_table(console, cpualgo)
console.print()
console.print(f"CPU Utilization: {round(cpualgo.cpu_utilization*100*1000)/1000:.2f}%")
console.print(f"Average Turnaround Time: {round(cpualgo.avg_turnaround_time*1000)/1000:.2f}")
console.print(f"Average Waiting Time: {round(cpualgo.avg_waiting_time*1000)/1000:.2f}")
console.print()
timeline_display = Text(str(cpualgo.proc_timeline))
timeline_display.highlight_regex(r"\d+", "yellow")
timeline_display.highlight_regex(r"P\d+", "red")
console.print(timeline_display)
questionary.press_any_key_to_continue().ask()
