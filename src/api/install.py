from bottle import request, template, redirect

from src.common import IndexApp
from src.drives.onedrive import OneDrive


def install_index(one_drive: OneDrive):
    if request.method == 'GET':
        data = {}
        name = request.query.get('name')
        if name:
            data = IndexApp.get_mongo().find_one({'_id': name})
        return template('install.html', data=data)

    params = dict(request.forms.decode())

    _id = params.get('id')

    IndexApp.install(params)

    params['state'] = f"{request.url}/auth/{_id}"
    url = one_drive.authorize_url(**params)
    redirect(url)


def install_auth(one_drive: OneDrive):
    name = request.query.get('name')
    data = IndexApp.get_mongo().find_one({'_id': name})
    if not data:
        redirect('/install')

    code = request.query.get('code')
    one_data = one_drive.fetch_token(code=code, **data)

    one_drive.access_token = one_data.get('access_token')
    user_info = one_drive.user_info()

    if data.get('drive_type') == 'OneDrive':
        drive_data = one_drive.get_drive()
    else:
        site = one_drive.get_site(name)
        one_data['site_id'] = site['id']
        drive_data = one_drive.get_site_drive(one_data['site_id'])

    IndexApp.save_token(name, one_data, {'username': user_info['userPrincipalName'], 'drive_id': drive_data['id'],
                                         'total': drive_data['quota']['total'],
                                         'used': drive_data['quota']['used'],
                                         'remaining': drive_data['quota']['remaining']})
    if data['drive_type'] == 'SharePoint' and not one_data.get('site_id'):
        return f'Site: <b>{data["site_id"]}</b> Not Found'

    redirect(f'/{name}')
