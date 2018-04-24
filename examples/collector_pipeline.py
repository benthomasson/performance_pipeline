
import gevent
from gevent_pipeline.fsm import FSMController, NullTracer
from performance_pipeline.data_channel import DataChannel

import performance_pipeline.collect_fsm
import performance_pipeline.web_fsm


fsm_tracer = NullTracer
channel_tracer = NullTracer

collector = FSMController(dict(),
                          'collect_fsm',
                          1,
                          performance_pipeline.collect_fsm.Start,
                          fsm_tracer,
                          channel_tracer)
webserver = FSMController(dict(),
                          'web_fsm',
                          2,
                          performance_pipeline.web_fsm.Start,
                          fsm_tracer,
                          channel_tracer)


collector.outboxes['default'] = DataChannel(collector,
                                        webserver,
                                        channel_tracer,
                                        webserver.inboxes['default'])


def start_pipeline():
    gevent.joinall([gevent.spawn(collector.receive_messages),
                    gevent.spawn(webserver.receive_messages),
                    ])
