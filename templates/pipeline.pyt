
import gevent
from gevent.queue import Queue
from gevent_pipeline.fsm import FSMController, Channel, NullTracer
from performance_pipeline.data_channel import DataChannel

{%for fsm in fsms-%}
import {{fsm.fsm}}
{%endfor%}

fsm_tracer = NullTracer
channel_tracer = NullTracer

{%for fsm in fsms-%}
{{fsm.name}} = FSMController(dict({%for key, value in fsm.get('context', {}).iteritems()%}{{key}}={{value}}{%if not loop.last%}, {%endif%}{%endfor%}),
                             '{{fsm.fsm.split('.')[-1]}}',
                             {{fsm.id}},
                            {{fsm.init_state}},
                            fsm_tracer,
                            channel_tracer)
{%endfor%}

{%for channel in channels%}{%if channel.inbox != "default"%}
{{channel.to_fsm}}.inboxes['{{channel.inbox}}'] = Queue()
{%endif%}{%endfor%}

{%for channel in channels%}
{{channel.from_fsm}}.outboxes['{{channel.outbox}}'] = {{channel.type}}({{channel.from_fsm}},
                                                                       {{channel.to_fsm}},
                                                                       channel_tracer,
                                                                       {{channel.to_fsm}}.inboxes['{{channel.inbox}}'])
{%endfor%}

def start_pipeline():
    gevent.joinall([{%for fsm in fsms%}gevent.spawn({{fsm.name}}.receive_messages),
                    {%endfor%}])
