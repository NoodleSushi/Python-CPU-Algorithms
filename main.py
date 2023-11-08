import tabulate
from cpu_sched_base import CPUSchedBase
from cpu_sched_algos import PPSched
from process import Process

cpualgo = PPSched(
    [
        Process("A", 0, 8, 4),
        Process("B", 3, 4, 3),
        Process("C", 4, 5, 1),
        Process("D", 6, 3, 2),
        Process("E", 10, 2, 2),
    ]
)

def print_cpu_sched_table(algo: CPUSchedBase):
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

cpualgo.execute()
print_cpu_sched_table(cpualgo)
