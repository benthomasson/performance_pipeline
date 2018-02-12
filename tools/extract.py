#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
    extract [options] <module>

Options:
    -h, --help        Show this page
    --debug            Show debug logging
    --verbose        Show verbose logging
"""
from docopt import docopt
import logging
import sys
import os
import yaml
from gevent_pipeline.fsm import State

logger = logging.getLogger('extract')


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parsed_args = docopt(__doc__, args)
    if parsed_args['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    elif parsed_args['--verbose']:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    module_name = parsed_args['<module>']

    module =  __import__(module_name)

    for part in parsed_args['<module>'].split('.')[1:]:
        module = getattr(module, part)

    logger.debug("Module %s", module)

    states = []
    transitions = []
    data = dict(states=states,
                transitions=transitions)

    for obj_name in dir(module):
        obj = getattr(module, obj_name)
        if isinstance(obj, State):
            logger.debug("%s type %s %s", obj_name, type(obj), isinstance(obj, State))
            for fn_name in dir(obj):
                fn = getattr(obj, fn_name)
                if getattr(fn, 'transitions', False):
                    logger.debug("%s:%s type %s %s", obj_name, fn_name, type(fn), getattr(fn, 'transitions'))
                    for transition in getattr(fn, 'transitions'):
                        transitions.append(dict(from_state=obj_name,
                                                to_state=transition,
                                                label=fn_name))
            states.append(obj_name)


    print yaml.dump(data, default_flow_style=False)

    return 0

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.abspath(os.getcwd()))
    sys.exit(main(sys.argv[1:]))

