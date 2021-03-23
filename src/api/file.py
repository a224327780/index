import base64
import json
from datetime import datetime

from bottle import request, redirect

from src.common import format_size, IndexApp, format_file_type
from src.drives.onedrive import OneDrive


def file_index(one_drive: OneDrive):
    params = dict(request.query)
    folder = params.get('folder', '')
    page = params.get('page')
    name = params.get('name')

    if page:
        page = base64.b64decode(page).decode('ascii')
        data = one_drive.api(page)
    else:
        data = one_drive.file_list(**params)
    # print(json.dumps(data, indent=4))
    items = []
    for item in data['value']:
        item['lastModifiedDateTime'] = str(datetime.strptime(item['lastModifiedDateTime'], '%Y-%m-%dT%H:%M:%SZ'))
        item['size'] = format_size(item['size'])
        item['meta'] = format_file_type(item['name'])
        _folder = f"{folder.strip('/')}/{item.get('name')}"
        item['url'] = f"/{name}/{_folder.strip('/')}"
        if item.get('folder'):
            item['size'] = item.get('folder').get('childCount')

        items.append(item)

    page_url = data.get('@odata.nextLink', '')
    m = params.get('m')
    if page:
        view_name = 'grid' if m == 'grid' else 'list'
        html = IndexApp.render(f'data/{view_name}', items=items)
        return {'html': html, 'page_url': page_url}
    # print(json.dumps(data, indent=4))
    return IndexApp.render('index', items=items, page_url=page_url)


def file_download(one_drive: OneDrive):
    params = dict(request.query)
    params['file'] = params['folder']
    data = one_drive.get_file(**params)
    download_url = data.get('@microsoft.graph.downloadUrl')
    return redirect(download_url)


def file_delete(one_drive: OneDrive):
    params = dict(request.query)
    params['file'] = params['folder']
    return one_drive.delete_file(**params)


def file_folder(one_drive: OneDrive):
    if request.method == 'GET':
        return IndexApp.render('folder')

    params = dict(request.query)
    parent_folder = params.get('folder')

    folder_name = request.forms.folder_name
    return one_drive.create_folder(parent_folder, folder_name, **params)


def file_rename(one_drive: OneDrive):
    org_name = request.query.org_name
    if request.method == 'GET':
        return IndexApp.render('rename', org_name=org_name)

    params = dict(request.query)

    new_name = request.forms.new_name
    return one_drive.rename_file(org_name, new_name, **params)


def file_upload(one_drive: OneDrive):
    params = dict(request.query)
    upload = request.files.get('file')
    folder = params.get('folder')
    # file = Path(upload.file.name)
    # print(file.stat().st_size)
    # print(upload.file.name)
    filename = upload.filename
    if folder:
        filename = f'{folder.strip("/")}/{filename}'
    return one_drive.upload_file(filename, upload.file.read(), **params)


def file_rclone(one_drive: OneDrive):
    return IndexApp.render('rclone')
