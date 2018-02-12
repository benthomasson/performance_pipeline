
from gevent_pipeline.fsm import State, transitions

import time
import gevent
import messages


class _Start(State):

    @transitions('Running')
    def start(self, controller):

        controller.changeState(Running)


Start = _Start()


class _Running(State):

    def start(self, controller):
        thread = controller.context.get('thread', None)
        if thread is not None:
            gevent.kill(thread)

        def send_ticks():
            while True:
                controller.outboxes['default'].put(messages.Tick(time.time()))
                gevent.sleep(controller.context.get('delay_time', 1.0))

        controller.context['thread'] = gevent.spawn(send_ticks)

    @transitions('Stopped')
    def onStop(self, controller, message_type, message):

        controller.changeState(Stopped)


Running = _Running()


class _Stopped(State):

    def start(self, controller):
        thread = controller.context.get('thread', None)
        if thread is not None:
            gevent.kill(thread)

    @transitions('Running')
    def onRestart(self, controller, message_type, message):

        controller.changeState(Running)


Stopped = _Stopped()
