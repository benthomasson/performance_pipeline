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
from gevent_pipeline.conf import settings as gp_settings
from performance_pipeline.conf import settings
import gevent
from performance_pipeline.server import SocketIOServer, queue
from bottle import run

logger = logging.getLogger('tick')

class Bundle(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)



def web_server():
    run(server=SocketIOServer, host='0.0.0.0', port=settings.web_port)


class _LoggingTracer(object):

    def __init__(self):
        pass

    def trace_order_seq(self):
        return 1

    def send_trace_message(self, message):
        logger.debug("TRACE: %s", message)

LoggingTracer = _LoggingTracer()


class _LoggingChannel(object):

    def put(self, message):
        logger.info("MESSAGE: %s", message)


LoggingChannel = _LoggingChannel()


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

    clock = FSMController(dict(delay_time=0.1), 'clock_fsm', performance_pipeline.clock_fsm.Start, LoggingTracer)
    batch_clock = FSMController(dict(delay_time=10), 'clock_fsm', performance_pipeline.clock_fsm.Start, LoggingTracer)
    collector = FSMController(dict(), 'collect_fsm', performance_pipeline.collect_fsm.Start, LoggingTracer)
    replicator = FSMController(dict(), 'replicate_fsm', performance_pipeline.replicate_fsm.Start, LoggingTracer)
    batcher = FSMController(dict(buffer=list(), limit=500), 'batch_fsm', performance_pipeline.batch_fsm.Start, LoggingTracer)
    clock.outboxes['default'] = Channel(clock, collector, LoggingTracer)
    collector.inboxes['default'] = clock.outboxes['default']
    collector.outboxes['default'] = Channel(collector, replicator, LoggingTracer)
    replicator.inboxes['data'] = collector.outboxes['default']
    replicator.outboxes['one'] = LoggingChannel
    c1 = Channel(replicator, batcher, LoggingTracer)
    batch_clock.outboxes['default'] = Channel(batch_clock, batcher, LoggingTracer, c1)
    replicator.outboxes['two'] = DataChannel(c1)
    replicator.outboxes['three'] = Channel(replicator, Bundle(name="webserver") , LoggingTracer, queue)
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
