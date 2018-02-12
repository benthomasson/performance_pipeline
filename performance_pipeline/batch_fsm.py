
from gevent_pipeline.fsm import State, transitions


class _Start(State):

    @transitions('Waiting')
    def start(self, controller, message_type, message):

        controller.changeState(Waiting)


Start = _Start()


class _Waiting(State):

    @transitions('Queuing')
    def onData(self, controller, message_type, message):

        controller.changeState(Queuing)

    @transitions('Sending')
    def onTick(self, controller, message_type, message):

        controller.changeState(Sending)


Waiting = _Waiting()


class _Sending(State):

    @transitions('Waiting')
    def start(self, controller, message_type, message):

        controller.changeState(Waiting)


Sending = _Sending()


class _Queuing(State):

    @transitions('Waiting', 'Sending')
    def start(self, controller, message_type, message):

        controller.changeState(Waiting)
        controller.changeState(Sending)


Queuing = _Queuing()
