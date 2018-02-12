
import messages

class DataChannel(object):

    def __init__(self, channel):
        self.channel = channel

    def put(self, item):
        self.channel.put(messages.Data(item))

    def get(self, blocking=True, timeout=None):
        return self.channel.get(blocking, timeout)

