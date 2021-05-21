import logging
import os

from bottle import request, static_file, default_app, redirect, response, auth_basic

from src.common import IndexApp, run_route

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'
logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.INFO)

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception as e:
    logging.debug(e)

app = default_app()


def authenticated(user, password):
    auth_user = os.environ.get('AUTH_USERNAME', 'root')
    auth_pwd = os.environ.get('AUTH_PASSWORD')
    if user != auth_user or password != auth_pwd:
        return False
    return True


@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@app.route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')


@app.route('/favicon.ico', method='GET')
def favicon():
    return ''


@app.route('/env1', method='GET')
def env():
    return dict(os.environ.items())


@app.route('/', method='GET')
@auth_basic(authenticated)
def index():
    drives = IndexApp.get_drives()
    if len(drives):
        for k, v in drives.items():
            redirect(f'/{v[0]["_id"]}')
    redirect('/install')


@app.route('/install', method=['GET', 'POST'])
@app.route('/install/:action/:name', method=['GET', 'POST'])
@auth_basic(authenticated)
def install(action=None, name=None):
    if name:
        request.query['name'] = name
    return run_route('install', action)


@app.route('/:name', method=['GET', 'POST'])
@app.route('/:name/<path:path>', method=['GET', 'POST'])
@auth_basic(authenticated)
def file(name, path=None):
    request.query['name'] = name
    action = 'index'

    a = request.query.get('a')
    if a:
        action = a

    if path:
        request.query['folder'] = path

        if '.' in path and not a:
            action = 'download'
    return run_route('file', action)


@app.error(404)
def error404(e1):
    return '<html><head><title>404 Not Found</title></head><body><center>' \
           '<h1>404 Not Found</h1></center><hr><center> nginx</center></body></html>'


@app.error(500)
def error500(e1):
    return IndexApp.render('500', e=e1)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
