from bottle import default_app

app = default_app


@app.route('/favicon.ico', method='GET')
def favicon():
    return ''


@app.route('/')
def index():
    return 'home'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
