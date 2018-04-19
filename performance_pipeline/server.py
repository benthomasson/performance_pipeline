
import socket
import pkg_resources
import logging
from bottle import ServerAdapter
from gevent.queue import Queue
import gevent

from jinja2 import Environment, PackageLoader

from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin


from bottle import route, request
from bottle import static_file

from socketio import socketio_manage


logger = logging.getLogger('server')

env = Environment(loader=PackageLoader('performance_pipeline', 'templates'))

queue = Queue()


class DefaultNamespace(BaseNamespace, BroadcastMixin):

    def initialize(self):
        logger.debug("INIT")
        print(self.__dict__.keys())
        print(self.ns_name)
        print(self.request)

        self.emit("data", dict(log="connected"))
        gevent.spawn(self.read_queue)

    def read_queue(self):
        self.emit("data", dict(log="reading queue"))
        while True:
            data = queue.get()
            logger.debug("DATA %s", data)
            self.emit(data.__class__.__name__, data)


@route('/socket.io/<namespace:path>')
def index(namespace):
    logger.debug("DefaultNamespace")
    socketio_manage(request.environ, {'/connect': DefaultNamespace})


@route('/status')
def status():
    logger.debug("status")
    return "running"


@route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root=pkg_resources.resource_filename('performance_pipeline', 'static'))


@route('/')
def root():
    return env.get_template('index.html').render()


class SocketIOServer(ServerAdapter):
    def run(self, handler):
        from socketio.server import SocketIOServer
        resource = self.options.get('resource', 'socket.io')
        policy_server = self.options.get('policy_server', False)
        done = False
        while not done:
            try:
                SocketIOServer((self.host, self.port),
                               handler,
                               resource=resource,
                               policy_server=policy_server,
                               transports=['websocket', 'xhr-multipart', 'xhr-polling']).serve_forever()
            except socket.error as e:
                if e.errno == 98:
                    logger.warning(str(e))
                    raise
                else:
                    raise
