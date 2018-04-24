
import gevent
from gevent.queue import Queue
import logging
from itertools import count
from gevent_pipeline.fsm import FSMController, Channel
from performance_pipeline.data_channel import DataChannel
from util import YAMLFileLoggingTracer
from util import LoggingChannel, Bundle, web_server

from performance_pipeline.server import queue

import performance_pipeline.clock_fsm
import performance_pipeline.sample_fsm
import performance_pipeline.replicate_fsm
import performance_pipeline.batch_fsm


logger = logging.getLogger('tick')

fsm_tracer = YAMLFileLoggingTracer("fsm_trace.yml")
channel_tracer = YAMLFileLoggingTracer("channel_trace.yml")

fsm_id_seq = count(start=1, step=1)

# FSMs
clock = FSMController(dict(delay_time=0.1),
                      'clock_fsm',
                      next(fsm_id_seq),
                      performance_pipeline.clock_fsm.Start,
                      fsm_tracer,
                      channel_tracer)
batch_clock = FSMController(dict(delay_time=2),
                            'clock_fsm',
                            next(fsm_id_seq),
                            performance_pipeline.clock_fsm.Start,
                            fsm_tracer,
                            channel_tracer)
sampler = FSMController(dict(),
                        'sample_fsm',
                        next(fsm_id_seq),
                        performance_pipeline.sample_fsm.Start,
                        fsm_tracer,
                        channel_tracer)
replicator = FSMController(dict(),
                           'replicate_fsm',
                           next(fsm_id_seq),
                           performance_pipeline.replicate_fsm.Start,
                           fsm_tracer,
                           channel_tracer)
batcher = FSMController(dict(buffer=list(),
                             limit=10),
                        'batch_fsm',
                        next(fsm_id_seq),
                        performance_pipeline.batch_fsm.Start,
                        fsm_tracer,
                        channel_tracer)

# Channels
replicator.inboxes['data'] = Queue()

clock.outboxes['default'] = Channel(clock,
                                    sampler,
                                    channel_tracer,
                                    sampler.inboxes['default'])
sampler.outboxes['default'] = Channel(sampler,
                                      replicator,
                                      channel_tracer,
                                      replicator.inboxes['data'])
replicator.outboxes['one'] = LoggingChannel
replicator.outboxes['two'] = DataChannel(replicator,
                                         batcher,
                                         channel_tracer,
                                         batcher.inboxes['default'])
batch_clock.outboxes['default'] = Channel(batch_clock,
                                          batcher,
                                          channel_tracer,
                                          batcher.inboxes['default'])
replicator.outboxes['three'] = Channel(replicator,
                                       Bundle(name="webserver",
                                              fsm_id=next(fsm_id_seq)),
                                       channel_tracer,
                                       queue)
batcher.outboxes['default'] = LoggingChannel


def start_pipeline():
    gevent.joinall([gevent.spawn(clock.receive_messages),
                    gevent.spawn(batch_clock.receive_messages),
                    gevent.spawn(sampler.receive_messages),
                    gevent.spawn(replicator.receive_messages),
                    gevent.spawn(batcher.receive_messages),
                    gevent.spawn(web_server)])
