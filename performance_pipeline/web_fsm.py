import gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from gevent_pipeline.fsm import State, transitions

import performance_pipeline
print(performance_pipeline)

from performance_pipeline.conf import settings
from performance_pipeline.server import app, queue


class _Start(State):

    @transitions('Running')
    def start(self, controller):

        controller.changeState(Running)


Start = _Start()


class _Running(State):

    def start(self, controller):
        gevent.spawn(WSGIServer(('0.0.0.0', settings.web_port), app, handler_class=WebSocketHandler).serve_forever)

    def onData(self, controller, message_type, message):
        queue.put(message.data)


Running = _Running()
