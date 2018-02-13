
from gevent_pipeline.fsm import State, transitions

import messages


class _Start(State):

    @transitions('Waiting')
    def start(self, controller):

        controller.changeState(Waiting)


Start = _Start()


class _Waiting(State):

    @transitions('Queuing')
    def onData(self, controller, message_type, message):

        controller.changeState(Queuing)
        controller.handle_message(message_type, message)

    @transitions('Sending')
    def onTick(self, controller, message_type, message):

        controller.changeState(Sending)


Waiting = _Waiting()


class _Sending(State):

    @transitions('Waiting')
    def start(self, controller):

        data = controller.context['buffer']
        controller.context['buffer'] = []
        controller.outboxes['default'].put(messages.Batch(data))
        controller.changeState(Waiting)

Sending = _Sending()


class _Queuing(State):

    @transitions('Waiting', 'Sending')
    def onData(self, controller, message_type, message):

        controller.context['buffer'].append(message.data)
        if len(controller.context['buffer']) < controller.context['limit']:
            controller.changeState(Waiting)
        else:
            controller.changeState(Sending)


Queuing = _Queuing()
