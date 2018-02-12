
from gevent_pipeline.fsm import State, transitions

import gevent


class _Disabled(State):

    def start(self, controller):
        thread = controller.context.get('thread', None)
        if thread is not None:
            gevent.kill(thread)

    @transitions('Replicating')
    def onEnable(self, controller, message_type, message):

        controller.changeState(Replicating)


Disabled = _Disabled()


class _Start(State):

    @transitions('Replicating')
    def start(self, controller):

        controller.changeState(Replicating)


Start = _Start()


class _Replicating(State):

    def start(self, controller):
        thread = controller.context.get('thread', None)
        if thread is not None:
            gevent.kill(thread)

        def send_data():
            while True:
                gevent.sleep(0)
                if controller.inboxes.get('data', None) and controller.outboxes:
                    message = controller.inboxes['data'].get()
                    for outbox in controller.outboxes.values():
                        outbox.put(message)
                else:
                    break

        controller.context['thread'] = gevent.spawn(send_data)

    @transitions('Disabled')
    def onDisable(self, controller, message_type, message):

        controller.changeState(Disabled)


Replicating = _Replicating()
