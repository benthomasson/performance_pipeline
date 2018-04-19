
import performance_pipeline.messages as messages

from gevent_pipeline.fsm import Channel


class DataChannel(object):

    def __init__(self, from_fsm, to_fsm, tracer, queue=None):
        self.channel = Channel(from_fsm, to_fsm, tracer, queue)

    def put(self, item):
        self.channel.put(messages.Data(item))

    def get(self, blocking=True, timeout=None):
        return self.channel.get(blocking, timeout)
