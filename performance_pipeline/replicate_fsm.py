
from gevent_pipeline.fsm import State, transitions


class _Disabled(State):

    @transitions('Replicating')
    def onEnable(self, controller, message_type, message):

        controller.changeState(Replicating)


Disabled = _Disabled()


class _Start(State):

    @transitions('Replicating')
    def start(self, controller, message_type, message):

        controller.changeState(Replicating)


Start = _Start()


class _Replicating(State):

    @transitions('Disabled')
    def onDisable(self, controller, message_type, message):

        controller.changeState(Disabled)


Replicating = _Replicating()
