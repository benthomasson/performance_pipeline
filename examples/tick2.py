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
from gevent_pipeline.conf import settings as gp_settings
from tick_pipeline2 import start_pipeline


logger = logging.getLogger('tick')


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

    start_pipeline()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
