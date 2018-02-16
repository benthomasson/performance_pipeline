

from collections import namedtuple


def serialize(message):
    return [message.__class__.__name__, dict(message._asdict())]


Tick = namedtuple('Tick', ['time'])
Data = namedtuple('Data', ['data'])
Batch = namedtuple('Batch', ['data'])
CpuUsage = namedtuple('CpuUsage', ['cpu_percent'])
MemUsage = namedtuple('MemUsage', ['mem_percent'])
