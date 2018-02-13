
from gevent_pipeline.fsm import State, transitions


class _Sending(State):

    @transitions('Waiting')
    def onTick(self, controller, message_type, message):

        if len(controller.context.get('buffer', [])) != 0:
            datum = controller.context['buffer'].pop(0)
            if controller.context.get('use_last', False):
                controller.context['last'] = datum
            controller.outboxes['default'].put(datum)
        elif controller.context.get('last', None) is not None:
            datum = controller.context['last']
            controller.outboxes['default'].put(datum)
        elif controller.context.get('default', None) is not None:
            datum = controller.context['default']
            controller.outboxes['default'].put(datum)
        else:
            controller.changeState(Waiting)

    def onBatch(self, controller, message_type, message):
        controller.context.get('buffer', []).extend(message.data)


Sending = _Sending()


class _Waiting(State):

    @transitions('Sending')
    def onTick(self, controller, message_type, message):
        if controller.context.get('default', None) is not None:
            controller.changeState(Sending)
            controller.handle_message(message_type, message)

    @transitions('Sending')
    def onBatch(self, controller, message_type, message):
        controller.context.get('buffer', []).extend(message.data)
        controller.changeState(Sending)


Waiting = _Waiting()


class _Start(State):

    @transitions('Waiting')
    def start(self, controller):

        controller.changeState(Waiting)


Start = _Start()
