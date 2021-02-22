import json
import logging
import os
from importlib import import_module

from bottle import request, static_file, default_app, response, redirect

from src.common import fail, IndexApp
from src.onedrive import OneDrive, OneDriveException

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'
logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.INFO)

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception as e:
    logging.debug(e)

app = default_app()


@app.route('/favicon.ico')
def favicon():
    return 'favicon.png'


@app.route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')


@app.route('/', method='GET')
@app.route('/:name', method='GET')
def index(name=None):
    return IndexApp.render('index')


@app.route('/install', method=['GET', 'POST'])
@app.route('/install/:action/:name', method=['GET', 'POST'])
def install(controller, action=None, name=None):
    if name:
        request.query['name'] = name

    m = import_module('src.api.install')
    if not action:
        action = 'index'

    one_drive = OneDrive()
    _action = f'{controller}_{action}'
    return getattr(m, f'{controller}_{action}')(one_drive)


# @app.error(500)
# def error500(e1):
#     if isinstance(e1.exception, OneDriveException):
#         data = json.loads(e1.exception.message)
#         error = data.get('error')
#         response.content_type = 'application/json'
#         return json.dumps(fail(error.get('message'), data=data))
#
#     if request.is_ajax:
#         response.content_type = 'application/json'
#         return json.dumps(fail(str(e1.exception), data=e1.traceback))
#
#     if e1.traceback:
#         return app.default_error_handler(e1)
#     return e1.body

@app.error(404)
def error404(e1):
    return '<html><head><title>404 Not Found</title></head><body><center>' \
           '<h1>404 Not Found</h1></center><hr><center> nginx</center></body></html>'


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=os.environ.get('DEBUG', True))
