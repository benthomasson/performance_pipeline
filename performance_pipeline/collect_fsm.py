from gevent_pipeline.fsm import State, transitions

import performance_pipeline.messages as messages
import psutil
import gevent
import capnp  # noqa
import zmq.green as zmq
import os
import logging

measurements_capnp = capnp.load(os.path.join(os.path.dirname(__file__),'measurements.capnp'))

logger = logging.getLogger('collect_fsm')

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
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://meganuke:5559")
        socket.setsockopt(zmq.SUBSCRIBE, b'')
        logger.debug("Collecting.start")

        def collect():
            while True:
                logger.debug("Collecting.collect")
                message = socket.recv_multipart()
                if message[0] == b'Measurements':
                    for sample in measurements_capnp.Measurements.read_multiple_bytes(message[1]):
                        controller.handle_message('Measurements', sample)
        controller.context['thread'] = gevent.spawn(collect)

    def onMeasurements(self, controller, message_type, message):
        logger.debug("Collecting.onMeasurements")
        controller.outboxes['default'].put(messages.CpuUsage(message.cpu.cpu))

    @transitions('Disabled')
    def onDisable(self, controller, message_type, message):

        controller.changeState(Disabled)


    @transitions('Disabled')
    def onDisable(self, controller, message_type, message):
        controller.changeState(Disabled)


Collecting = _Collecting()


class _Start(State):

    @transitions('Collecting')
    def start(self, controller):

        controller.changeState(Collecting)


Start = _Start()
