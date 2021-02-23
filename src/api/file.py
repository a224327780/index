import base64
from datetime import datetime
from pathlib import Path

from bottle import request, redirect

from src.common import format_size, IndexApp
from src.drives.onedrive import OneDrive


def file_index(one_drive: OneDrive):
    params = dict(request.query)
    folder = params.get('folder', '')
    page = params.get('page')
    name = params.get('name')

    page_url = None
    try:
        if page:
            page = base64.b64decode(page).decode('ascii')
            data = one_drive.api(page)
        else:
            data = one_drive.file_list(**params)

        items = []
        for item in data['value']:
            item['lastModifiedDateTime'] = datetime.strptime(item['lastModifiedDateTime'], '%Y-%m-%dT%H:%M:%SZ')
            item['size'] = format_size(item['size'])
            _folder = f"{folder.strip('/')}/{item.get('name')}"
            item['url'] = f"/{name}/{_folder.strip('/')}"
            if item.get('folder'):
                item['size'] = item.get('folder').get('childCount')

            items.append(item)
        page_url = data.get('@odata.nextLink')
    except Exception as e:
        items = None

    if page:
        html = IndexApp.render('data', file_items=items)
        return {'html': html, 'page_url': page_url}

    return IndexApp.render('index', file_items=items, page_url=page_url)


def file_detail(one_drive: OneDrive):
    params = dict(request.query)
    data = one_drive.get_file(**params)
    download_url = data.get('@microsoft.graph.downloadUrl')
    return redirect(download_url)


def file_folder(one_drive: OneDrive):
    if request.method == 'GET':
        return IndexApp.render('file/folder', layout=False)

    params = dict(request.query)
    parent_folder = params.get('folder', '')
    folder_name = request.forms.get('folder_name')
    return one_drive.create_folder(parent_folder, folder_name, **params)


def file_upload(one_drive: OneDrive):
    upload = request.files.get('file')
    file = Path(upload.file.name)
    print(file.stat().st_size)
    print(upload.filename)
    return 'upload'
