

from collections import namedtuple

Tick = namedtuple('Tick', ['time'])
CpuUsage = namedtuple('CpuUsage', ['cpu_percent'])
MemUsage = namedtuple('MemUsage', ['mem_percent'])
