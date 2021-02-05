import logging
from datetime import datetime

from bottle import request, Bottle

from src.lib.app import IndexApp
from src.lib.onedrive import OneDrive

file_app = Bottle(autojson=False)
one_drive = OneDrive()


@file_app.hook('before_request')
def init():
    IndexApp.before_request(one_drive)


@file_app.route('/list')
def file_list():
    params = dict(request.query)
    items = []
    page_url = None
    try:
        data = one_drive.file_list(**params)
        for item in data['value']:
            item['lastModifiedDateTime'] = datetime.strptime(item['lastModifiedDateTime'], '%Y-%m-%dT%H:%M:%SZ')
            item['size'] = IndexApp.convert_size(item['size'])
            items.append(item)
        page_url = data.get('@odata.nextLink')
    except Exception as e:
        logging.error(e)
        items = False
    return IndexApp.render('file/list', items=items, page_url=page_url)
