

from collections import namedtuple

Tick = namedtuple('Tick', ['time'])
Data = namedtuple('Data', ['data'])
Batch = namedtuple('Batch', ['data'])
CpuUsage = namedtuple('CpuUsage', ['cpu_percent'])
MemUsage = namedtuple('MemUsage', ['mem_percent'])
