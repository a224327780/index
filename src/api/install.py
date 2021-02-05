from bottle import request, template, redirect, Bottle

from src.lib.app import IndexApp
from src.lib.onedrive import OneDrive

install_app = Bottle(autojson=False)


@install_app.route('/', method=['GET', 'POST'])
def install_index():
    if request.method == 'GET':
        return template('install.html')

    one = OneDrive()

    params = dict(request.forms)
    params['scope'] = one.admin_scope if params.get('oauth_type') == 'oauth' else ''

    name = params.get('name')
    IndexApp.install(params)
    if params.get('oauth_type') == 'oauth':
        params['state'] = f"{request.url}/{name}"
        url = one.authorize_url(**params)
        redirect(url)
        return

    data = one.get_ms_token(**params)
    IndexApp.save_token(name, data)
    redirect(f'/user/list?id={name}')


@install_app.route('/<name>')
def install_authorize(name):
    data = IndexApp.get_drive(name)
    if not data:
        redirect('/install/')

    code = request.query.get('code')
    one = OneDrive()
    one_data = one.fetch_token(code=code, **data)
    IndexApp.save_token(name, one_data)
    redirect(f'/user/list?id={name}')
