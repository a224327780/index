import logging
import os

from bottle import request, static_file, default_app, redirect

from src.common import IndexApp, run_route

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
    return static_file('favicon.png', root='static')


@app.route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')


@app.route('/', method='GET')
def index():
    drives = IndexApp.get_drives()
    if len(drives):
        for k, v in drives.items():
            redirect(f'/{v[0]["_id"]}')
    redirect('/install')


@app.route('/install', method=['GET', 'POST'])
@app.route('/install/:action/:name', method=['GET', 'POST'])
def install(action=None, name=None):
    if name:
        request.query['name'] = name
    return run_route('install', action)


@app.route('/:name', method='GET')
@app.route('/:name/<path:path>')
def file(name, path=None):
    request.query['name'] = name
    if path:
        request.query['folder'] = path
    return run_route('file', 'index')


@app.error(404)
def error404(e1):
    return '<html><head><title>404 Not Found</title></head><body><center>' \
           '<h1>404 Not Found</h1></center><hr><center> nginx</center></body></html>'


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=os.environ.get('DEBUG', True))
