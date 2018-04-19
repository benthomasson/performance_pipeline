
import pkg_resources
import logging
from gevent.queue import Queue
import gevent
import socketio

from jinja2 import Environment, PackageLoader

from bottle import Bottle
from bottle import static_file


logger = logging.getLogger('server')

env = Environment(loader=PackageLoader('performance_pipeline', 'templates'))

queue = Queue()
app = Bottle()
sio = socketio.Server(async_mode='gevent')


def read_queue():
    sio.emit("data", dict(log="reading queue"))
    while True:
        data = queue.get()
        logger.debug("DATA %s", data)
        sio.emit(data.__class__.__name__, data)


@sio.on('connect')
def connect(sid, environ):
    gevent.spawn(read_queue)


@sio.on('disconnect')
def disconnect(sid):
    pass


@app.route('/status')
def status():
    logger.debug("status")
    return "running"


@app.route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root=pkg_resources.resource_filename('performance_pipeline', 'static'))


@app.route('/')
def root():
    return env.get_template('index.html').render()


app = socketio.Middleware(sio, app)
