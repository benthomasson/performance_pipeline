
from gevent_pipeline.fsm import State, transitions

import performance_pipeline.messages as messages
import psutil


class _Disabled(State):

    @transitions('Sampling')
    def onEnable(self, controller, message_type, message):

        controller.changeState(Sampling)


Disabled = _Disabled()


class _Sampling(State):

    def onTick(self, controller, message_type, message):

        controller.outboxes['default'].put(messages.CpuUsage(psutil.cpu_percent()))

    @transitions('Disabled')
    def onDisable(self, controller, message_type, message):

        controller.changeState(Disabled)


Sampling = _Sampling()


class _Start(State):

    @transitions('Sampling')
    def start(self, controller):

        controller.changeState(Sampling)


Start = _Start()
