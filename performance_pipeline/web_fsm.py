import gevent
from gevent_pipeline.fsm import State, transitions
from bottle import run

import performance_pipeline
print(performance_pipeline)

from performance_pipeline.conf import settings
from performance_pipeline.server import SocketIOServer, queue


class _Start(State):

    @transitions('Running')
    def start(self, controller):

        controller.changeState(Running)


Start = _Start()


class _Running(State):

    def start(self, controller):
        gevent.spawn(run, server=SocketIOServer, host='0.0.0.0', port=settings.web_port)

    def onData(self, controller, message_type, message):
        queue.put(message.data)


Running = _Running()
