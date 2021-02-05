from bottle import request, Bottle

from src.lib.app import IndexApp
from src.lib.onedrive import OneDrive

user_app = Bottle()
one_drive = OneDrive()


@user_app.hook('before_request')
def init():
    IndexApp.before_request(one_drive)


@user_app.route('/list')
def user_list():
    params = dict(request.query)
    page = params.get('page')
    if page:
        data = one_drive.api(page)
    else:
        data = one_drive.user_list()

    items = []
    for item in data['value']:
        status = item['accountEnabled']
        item['status_icon'] = 'icon-cross text-error' if not status else 'icon-check text-success'

        licenses = []
        for sku in item['assignedLicenses']:
            licenses.append(one_drive.get_sku_name(sku['skuId']))
        item['licenses'] = licenses
        items.append(item)
    page_url = data.get('@odata.nextLink') or ''
    if page:
        html = IndexApp.render('user/data', layout=False, items=items)
        return {'html': html, 'page_url': page_url}
    return IndexApp.render('user/list', items=items, page_url=page_url)


@user_app.route('/site')
def site_list():
    data = one_drive.site_list()
    return IndexApp.render('user/site', items=data)
