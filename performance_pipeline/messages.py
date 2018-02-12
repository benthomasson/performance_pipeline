

from collections import namedtuple

Tick = namedtuple('Tick', ['time'])
Data = namedtuple('Data', ['data'])
CpuUsage = namedtuple('CpuUsage', ['cpu_percent'])
MemUsage = namedtuple('MemUsage', ['mem_percent'])
