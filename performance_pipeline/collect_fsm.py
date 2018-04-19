
from gevent_pipeline.fsm import State, transitions

import performance_pipeline.messages as messages
import psutil


class _Disabled(State):

    @transitions('Collecting')
    def onEnable(self, controller, message_type, message):

        controller.changeState(Collecting)


Disabled = _Disabled()


class _Collecting(State):

    def onTick(self, controller, message_type, message):

        controller.outboxes['default'].put(messages.CpuUsage(psutil.cpu_percent()))

    @transitions('Disabled')
    def onDisable(self, controller, message_type, message):

        controller.changeState(Disabled)


Collecting = _Collecting()


class _Start(State):

    @transitions('Collecting')
    def start(self, controller):

        controller.changeState(Collecting)


Start = _Start()
