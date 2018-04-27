from gevent_pipeline.fsm import State, transitions

import performance_pipeline.messages as messages
import psutil
import gevent
import capnp  # noqa
import measurements_capnp
import zmq.green as zmq


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

        def collect():
            while True:
                message = socket.recv_multipart()
                if message[0] == "Measurements":
                    samples = measurements_capnp.Measurements.read_multiple_bytes(message[1])
                    sample = messages.Measurements(samples.next())
                    controller.handle_message('Measurements', sample)
        controller.context['thread'] = gevent.spawn(collect)

    def onMeasurements(self, controller, message_type, message):
        controller.outboxes['default'].put(messages.CpuUsage(message.measurements.cpu.cpu))

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
