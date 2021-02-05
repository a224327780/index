from bottle import request, static_file, Bottle

from src.api.file import file_app
from src.api.install import install_app
from src.api.user import user_app

from src.lib.app import IndexApp

app = Bottle(autojson=False)
app.mount('/install', install_app)
app.mount('/user', user_app)
app.mount('/file', file_app)


@app.hook('before_request')
def authenticated():
    user, password = request.auth or (None, None)
    # abort(401, 'Access denied')


# # @app.error(401)
# # def error401(error_msg):
# #     return error_msg.body
# #
# #
# # @app.error(500)
# # def error500(error_msg):
# #     return error_msg.body
#
#
@app.route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')


@app.route('/', method='GET')
def index():
    return IndexApp.render('index')


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True, reloader=False)
