from bottle import request, template, redirect

from src.common import IndexApp
from src.onedrive import OneDrive


def install_index(one_drive: OneDrive):
    if request.method == 'GET':
        return template('install.html')

    params = dict(request.forms)
    IndexApp.install(params)

    params['state'] = f"{request.url}/code/{params.get('name')}"
    url = one_drive.authorize_url(**params)
    redirect(url)


def install_code(one_drive: OneDrive):
    name = request.query.get('name')
    data = IndexApp.get_mongo().find_one({'_id': name})
    if not data:
        redirect('/install')

    code = request.query.get('code')
    one_data = one_drive.fetch_token(code=code, **data)
    IndexApp.save_token(name, one_data)
    redirect(f'/{name}')
