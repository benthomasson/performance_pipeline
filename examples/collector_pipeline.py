
import gevent
from gevent.queue import Queue
from gevent_pipeline.fsm import FSMController, NullTracer
from performance_pipeline.data_channel import DataChannel, Channel

import performance_pipeline.collect_fsm
import performance_pipeline.web_fsm
import performance_pipeline.replicate_fsm
from util import FileChannel


fsm_tracer = NullTracer
channel_tracer = NullTracer

collector = FSMController(dict(),
                          'collect_fsm',
                          1,
                          performance_pipeline.collect_fsm.Start,
                          fsm_tracer,
                          channel_tracer)
replicator = FSMController(dict(),
                           'replicate_fsm',
                           2,
                           performance_pipeline.replicate_fsm.Start,
                           fsm_tracer,
                           channel_tracer)
webserver = FSMController(dict(),
                          'web_fsm',
                          3,
                          performance_pipeline.web_fsm.Start,
                          fsm_tracer,
                          channel_tracer)

replicator.inboxes['data'] = Queue()

collector.outboxes['default'] = DataChannel(collector,
                                            replicator,
                                            channel_tracer,
                                            replicator.inboxes['data'])


replicator.outboxes['default'] = Channel(replicator,
                                         webserver,
                                         channel_tracer,
                                         webserver.inboxes['default'])

replicator.outboxes['persist'] = FileChannel('measurements', 'a')


def start_pipeline():
    gevent.joinall([gevent.spawn(collector.receive_messages),
                    gevent.spawn(replicator.receive_messages),
                    gevent.spawn(webserver.receive_messages),
                    ])
