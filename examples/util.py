
import gevent
import yaml
import json
import logging
import websocket
from itertools import count
from performance_pipeline.messages import serialize
from performance_pipeline.server import app
from performance_pipeline.conf import settings

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

logger = logging.getLogger('tick')


class Bundle(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def web_server():
    WSGIServer(('0.0.0.0', settings.web_port), app, handler_class=WebSocketHandler).serve_forever()


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


class FileChannel(object):

    def __init__(self, file, mode):
        self.file = open(file, mode, 0)

    def put(self, message):
        self.file.write(json.dumps(serialize(message)))
        self.file.write('\n')


class WebsocketChannel(object):

    def __init__(self, address):
        self.socket = websocket.WebSocketApp(address,
                                             on_message=self.on_message,
                                             on_error=self.on_error,
                                             on_close=self.on_close,
                                             on_open=self.on_open)
        self.thread = gevent.spawn(self.socket.run_forever)

    def put(self, message):
        self.socket.send(json.dumps(serialize(message)))

    def on_open(self, ws):
        pass

    def on_message(self, ws):
        pass

    def on_close(self, ws):
        self.thread.kill()

    def on_error(self, ws, error):
        print ('WebsocketChannel on_error', error)


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
