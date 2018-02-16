#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
    tick [options]

Options:
    -h, --help        Show this page
    --debug            Show debug logging
    --verbose        Show verbose logging
"""
from gevent import monkey
monkey.patch_all()
from docopt import docopt
import logging
import sys
import performance_pipeline.clock_fsm
import performance_pipeline.collect_fsm
import performance_pipeline.replicate_fsm
import performance_pipeline.batch_fsm
from gevent_pipeline.fsm import FSMController, Channel
from performance_pipeline.data_channel import DataChannel
from performance_pipeline.messages import serialize
from gevent_pipeline.conf import settings as gp_settings
from performance_pipeline.conf import settings
import gevent
from performance_pipeline.server import SocketIOServer, queue
from bottle import run
import yaml
from itertools import count



logger = logging.getLogger('tick')

class Bundle(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)



def web_server():
    run(server=SocketIOServer, host='0.0.0.0', port=settings.web_port)


class _LoggingTracer(object):

    def __init__(self):
        self.counter = count(start=1, step=1)

    def trace_order_seq(self):
        return next(self.counter)

    def send_trace_message(self, message):
        logger.debug("TRACE: %s", message)

LoggingTracer = _LoggingTracer()


class _LoggingChannel(object):

    def put(self, message):
        logger.info("MESSAGE: %s", message)


LoggingChannel = _LoggingChannel()


class YAMLFileLoggingTracer(object):

    def __init__(self, file):
        self.file = file
        self.counter = count(start=1, step=1)

    def trace_order_seq(self):
        return next(self.counter)

    def send_trace_message(self, message):
        with open(self.file, 'a') as f:
            message_type, message_data = serialize(message)
            f.write(yaml.dump([message_data], default_flow_style=False))


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parsed_args = docopt(__doc__, args)
    if parsed_args['--debug']:
        logging.basicConfig(level=logging.DEBUG)
        gp_settings.instrumented = True
    elif parsed_args['--verbose']:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    fsm_tracer = YAMLFileLoggingTracer("fsm_trace.yml")
    channel_tracer = YAMLFileLoggingTracer("channel_trace.yml")

    fsm_id_seq = count(start=1, step=1)

    clock = FSMController(dict(delay_time=0.1), 'clock_fsm', next(fsm_id_seq), performance_pipeline.clock_fsm.Start, fsm_tracer, channel_tracer)
    batch_clock = FSMController(dict(delay_time=2), 'clock_fsm', next(fsm_id_seq), performance_pipeline.clock_fsm.Start, fsm_tracer, channel_tracer)
    collector = FSMController(dict(), 'collect_fsm', next(fsm_id_seq), performance_pipeline.collect_fsm.Start, fsm_tracer, channel_tracer)
    replicator = FSMController(dict(), 'replicate_fsm', next(fsm_id_seq), performance_pipeline.replicate_fsm.Start, fsm_tracer, channel_tracer)
    batcher = FSMController(dict(buffer=list(), limit=10), 'batch_fsm', next(fsm_id_seq), performance_pipeline.batch_fsm.Start, fsm_tracer, channel_tracer)
    clock.outboxes['default'] = Channel(clock, collector, channel_tracer)
    collector.inboxes['default'] = clock.outboxes['default']
    collector.outboxes['default'] = Channel(collector, replicator, channel_tracer)
    replicator.inboxes['data'] = collector.outboxes['default']
    replicator.outboxes['one'] = LoggingChannel
    c1 = Channel(replicator, batcher, channel_tracer)
    batch_clock.outboxes['default'] = Channel(batch_clock, batcher, channel_tracer, c1)
    replicator.outboxes['two'] = DataChannel(c1)
    replicator.outboxes['three'] = Channel(replicator, Bundle(name="webserver", fsm_id=next(fsm_id_seq)) , channel_tracer, queue)
    batcher.inboxes['default'] = replicator.outboxes['two']
    batcher.outboxes['default'] = LoggingChannel
    gevent.joinall([gevent.spawn(clock.receive_messages),
                    gevent.spawn(batch_clock.receive_messages),
                    gevent.spawn(collector.receive_messages),
                    gevent.spawn(replicator.receive_messages),
                    gevent.spawn(batcher.receive_messages),
                    gevent.spawn(web_server)])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
