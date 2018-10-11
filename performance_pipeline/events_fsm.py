from gevent_pipeline.fsm import State, transitions

import performance_pipeline.messages as messages
import gevent
import capnp  # noqa
import zmq.green as zmq
import os
import logging

measurements_capnp = capnp.load(os.path.join(os.path.dirname(__file__), 'measurements.capnp'))

logger = logging.getLogger('events_fsm')


class _Disabled(State):

    @transitions('Collecting')
    def onEnable(self, controller, message_type, message):

        controller.changeState(Collecting)


Disabled = _Disabled()


class _Collecting(State):

    def start(self, controller):
        thread = controller.context.get('thread', None)
        if thread is not None:
            gevent.kill(thread)

        context = zmq.Context()
        socket = context.socket(zmq.ROUTER)
        socket.bind("tcp://127.0.0.1:5560")
        logger.debug("Collecting.start")

        def collect():
            while True:
                logger.debug("Collecting.collect")
                message = socket.recv_multipart()
                client_id = message.pop(0)
                logger.debug("Message %r", message)
                if message[0] == b'Event':
                    for event in measurements_capnp.Event.read_multiple_bytes(message[1]):
                        controller.handle_message('Event', event)
        controller.context['thread'] = gevent.spawn(collect)

    def onEvent(self, controller, message_type, message):
        logger.debug("Collecting.onEvent")
        controller.outboxes['default'].put(messages.Event(message.name))

    @transitions('Disabled')
    def onDisable(self, controller, message_type, message):

        controller.changeState(Disabled)


Collecting = _Collecting()


class _Start(State):

    @transitions('Collecting')
    def start(self, controller):

        controller.changeState(Collecting)


Start = _Start()
