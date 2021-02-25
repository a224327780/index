import json
import math
import os
import re
import time
from datetime import datetime, timezone, timedelta
from importlib import import_module

from bottle import request, template, redirect, abort
from pymongo import MongoClient

from src.drives.onedrive import OneDrive


def run_route(controller, action=None):
    m = import_module(f'src.api.{controller}')
    if not action:
        action = 'index'

    one_drive = OneDrive()
    if controller != 'install':
        IndexApp.before_request(one_drive)

    return getattr(m, f'{controller}_{action}')(one_drive)


def success(data=None, message=''):
    return {'status': 0, 'msg': message, 'data': data}


def fail(message='', status=1, data=None):
    return {'status': status, 'msg': message, 'data': data}


def print_json(json_data):
    return json.dumps(json_data, indent=4)


def format_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    return f'{round(size_bytes / p, 2)}{size_name[i]}'


def get_time():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')


class IndexApp:
    app = None
    mongo_db = None
    drive_data = None

    @classmethod
    def get_mongo(cls):
        if not cls.mongo_db:
            mongo_uri = os.environ.get('MONGO_URI')
            client = MongoClient(mongo_uri, connectTimeoutMS=5000, socketTimeoutMS=5000)
            db = client.get_database('db0')
            cls.mongo_db = db['oneindex']
        return cls.mongo_db

    @classmethod
    def init_route(cls):
        import_module('src.api.install')

    @classmethod
    def get_drives(cls):
        groups = {}
        mongodb = cls.get_mongo()
        for item in mongodb.find({}, {'_id': 1, 'drive_type': 1, 'name': 1}).sort('drive_type', 1).sort('_id', 1):
            drive_type = item.get('drive_type')
            if not groups.get(drive_type):
                groups[drive_type] = []
            groups[drive_type].append(item)
        return groups

    @classmethod
    def save_token(cls, name: str, data: dict, data2=None):
        mongodb = cls.get_mongo()
        params = {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'expires_time': int(time.time()) + 3500,
            'update_date': get_time(),
        }
        site_id = data.get('site_id')
        if site_id:
            params['site_id'] = site_id
        username = data.get('username')
        if username:
            params['username'] = username

        if data2:
            params.update(data2)
        return mongodb.update_one({'_id': name}, {'$set': params}).modified_count

    @classmethod
    def install(cls, params: dict):
        _id = params.get('id')
        del params['id']
        return cls.get_mongo().update_one({'_id': _id}, {'$set': params}, True)

    @classmethod
    def get_drive(cls, _id):
        mongodb = cls.get_mongo()
        return mongodb.find_one({'_id': _id})

    @classmethod
    def render(cls, tpl_name, **kwargs):
        name = request.query.get('name')
        kwargs.setdefault('name', name)
        kwargs.setdefault('request', request)
        kwargs.setdefault('drive', cls.drive_data)
        kwargs.setdefault('static_version', os.environ.get('STATIC_VERSION', 0.1))
        drives = cls.get_drives()
        kwargs.setdefault('drives', drives)
        html = template(f'{tpl_name}.html', **kwargs)
        if not request.is_ajax:
            html = re.sub(r'(\r?\n)', '', html)
            html = re.sub(r'>\s{2,}<', '><', html)
        return html.strip()

    @classmethod
    def before_request(cls, one_drive: OneDrive):
        _id = request.query.get('name')
        data = cls.get_drive(_id)
        if not data:
            redirect('/')

        if data.get('drive_type') == 'OneDrive':
            request.query['user_id'] = 'me'

        if data.get('drive_type') == 'SharePoint':
            request.query['site_id'] = data['site_id']

        cls.drive_data = data
        not_time = int(time.time())
        expires_time = int(data.get('expires_time'))
        if expires_time <= not_time:
            _data = one_drive.refresh_token(**data)

            access_token = _data.get('access_token')
            if not access_token:
                abort(text=f"[{_id}]: refresh token fail.")

            one_drive.access_token = access_token

            if data.get('drive_type') == 'OneDrive':
                drive_data = one_drive.get_drive()
            else:
                drive_data = one_drive.get_site_drive(data['site_id'])

            cls.save_token(_id, _data, {'drive_id': drive_data['id'], 'total': drive_data['quota']['total'],
                                        'remaining': drive_data['quota']['remaining']})
            data['access_token'] = access_token

        one_drive.access_token = data['access_token']
