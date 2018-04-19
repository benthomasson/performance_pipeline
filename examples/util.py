
import logging
import yaml
from itertools import count
from performance_pipeline.messages import serialize
from performance_pipeline.server import SocketIOServer
from performance_pipeline.conf import settings
from bottle import run

logger = logging.getLogger('tick')


class Bundle(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def web_server():
    run(server=SocketIOServer, host='0.0.0.0', port=settings.web_port)


class _LoggingTracer(object):

    def __init__(self):
        self.counter = count(start=1, step=1)

    def trace_order_seq(self):
        return next(self.counter)

    def send_trace_message(self, message):
        logger.debug("TRACE: %s", message)

LoggingTracer = _LoggingTracer()


class _LoggingChannel(object):

    def put(self, message):
        logger.info("MESSAGE: %s", message)


LoggingChannel = _LoggingChannel()


class YAMLFileLoggingTracer(object):

    def __init__(self, file):
        self.file = file
        self.counter = count(start=1, step=1)

    def trace_order_seq(self):
        return next(self.counter)

    def send_trace_message(self, message):
        with open(self.file, 'a') as f:
            message_type, message_data = serialize(message)
            f.write(yaml.dump([message_data], default_flow_style=False))