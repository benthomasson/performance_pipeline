
import gevent
from gevent.queue import Queue
from gevent_pipeline.fsm import FSMController, Channel, NullTracer
from performance_pipeline.data_channel import DataChannel

import performance_pipeline.clock_fsm
import performance_pipeline.sample_fsm
import performance_pipeline.replicate_fsm
import performance_pipeline.batch_fsm
import performance_pipeline.web_fsm


fsm_tracer = NullTracer
channel_tracer = NullTracer

clock = FSMController(dict(delay_time=0.1),
                      'clock_fsm',
                      1,
                      performance_pipeline.clock_fsm.Start,
                      fsm_tracer,
                      channel_tracer)
batch_clock = FSMController(dict(delay_time=2),
                            'clock_fsm',
                            2,
                            performance_pipeline.clock_fsm.Start,
                            fsm_tracer,
                            channel_tracer)
sampler = FSMController(dict(),
                        'sample_fsm',
                        3,
                        performance_pipeline.sample_fsm.Start,
                        fsm_tracer,
                        channel_tracer)
replicator = FSMController(dict(),
                           'replicate_fsm',
                           4,
                           performance_pipeline.replicate_fsm.Start,
                           fsm_tracer,
                           channel_tracer)
batcher = FSMController(dict(buffer=[], limit=10),
                        'batch_fsm',
                        5,
                        performance_pipeline.batch_fsm.Start,
                        fsm_tracer,
                        channel_tracer)
webserver = FSMController(dict(),
                          'web_fsm',
                          6,
                          performance_pipeline.web_fsm.Start,
                          fsm_tracer,
                          channel_tracer)


replicator.inboxes['data'] = Queue()


clock.outboxes['default'] = Channel(clock,
                                    sampler,
                                    channel_tracer,
                                    sampler.inboxes['default'])

sampler.outboxes['default'] = Channel(sampler,
                                      replicator,
                                      channel_tracer,
                                      replicator.inboxes['data'])

replicator.outboxes['two'] = DataChannel(replicator,
                                         batcher,
                                         channel_tracer,
                                         batcher.inboxes['default'])

batch_clock.outboxes['default'] = Channel(batch_clock,
                                          batcher,
                                          channel_tracer,
                                          batcher.inboxes['default'])

replicator.outboxes['three'] = DataChannel(replicator,
                                           webserver,
                                           channel_tracer,
                                           webserver.inboxes['default'])


def start_pipeline():
    gevent.joinall([gevent.spawn(clock.receive_messages),
                    gevent.spawn(batch_clock.receive_messages),
                    gevent.spawn(sampler.receive_messages),
                    gevent.spawn(replicator.receive_messages),
                    gevent.spawn(batcher.receive_messages),
                    gevent.spawn(webserver.receive_messages),
                    ])
