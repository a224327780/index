import json
import logging
import math
import time
from datetime import datetime, timezone, timedelta
from importlib import import_module

from bottle import template, request, redirect, abort
from pymongo import MongoClient

from src.lib.onedrive import OneDrive

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'
logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.INFO)

mongo_uri = 'mongodb+srv://root:hack3321@cluster0.9v4wz.azure.mongodb.net/?retryWrites=true&w=majority'


class IndexApp:

    mongo_db = None

    @classmethod
    def get_mongo(cls):
        if not cls.mongo_db:
            client = MongoClient(mongo_uri)
            db = client.get_database('index')
            cls.mongo_db = db['index']
        return cls.mongo_db

    @classmethod
    def init_route(cls):
        import_module('src.api.install')

    @classmethod
    def get_drives(cls):
        groups = {}
        mongodb = cls.get_mongo()
        for item in mongodb.find({'admin': 1}, {'_id': 1, 'one_type': 1}).sort('_id', 1):
            one_type = item.get('one_type')
            if not groups.get(one_type):
                groups[one_type] = []
            groups[one_type].append(item)
        return groups

    @classmethod
    def save_token(cls, name: str, data: dict):
        mongodb = cls.get_mongo()
        params = {
            'access_token': data.get('access_token'),
            'expires_time': int(time.time()) + data.get('expires_in', 3599),
            'refresh_token': data.get('refresh_token', ''),
            'update_date': cls.get_time()
        }
        # if data.get('scope'):
        #     params['scope'] = data['scope']
        return mongodb.update_one({'_id': name}, {'$set': params}).modified_count

    @classmethod
    def install(cls, params: dict):
        return IndexApp.get_mongo().update_one({'_id': params.get('name')}, {'$set': params}, True)

    @classmethod
    def get_drive(cls, _id):
        mongodb = cls.get_mongo()
        return mongodb.find_one({'_id': _id})

    @classmethod
    def get_time(cls):
        utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        return utc_dt.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def render(cls, tpl_name, layout=True, **kwargs):
        _id = request.query.get('id')
        kwargs.setdefault('_id', _id)
        kwargs.setdefault('request', request)
        content = template(f'{tpl_name}.html', **kwargs)
        if not layout:
            return content
        drives = cls.get_drives()
        return template('layout.html', content=content, drives=drives, **kwargs)

    @classmethod
    def before_request(cls, one_drive: OneDrive):
        _id = request.query.get('id')
        data = cls.get_drive(_id)
        if not data:
            redirect('/')

        not_time = int(time.time())
        expires_time = data.get('expires_time')
        if type(expires_time) == int and expires_time <= not_time:
            if data['oauth_type'] == 'application':
                _data = one_drive.get_ms_token(**data)
            else:
                _data = one_drive.refresh_token(**data)

            access_token = _data.get('access_token')
            if not access_token:
                abort(text=f"[{_id}]: refresh token fail.")

            data['access_token'] = access_token
            data['refresh_token'] = _data.get('refresh_token', '')
            data['expires_time'] = int(time.time()) + _data.get('expires_in', 3599)
            IndexApp.save_token(_id, data)

        one_drive.access_token = data['access_token']

    @classmethod
    def convert_size(cls, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        return f'{round(size_bytes / p, 2)}{size_name[i]}'

    @classmethod
    def print_json(cls, json_data):
        print(json.dumps(json_data, indent=4))


if __name__ == '__main__':
    one = OneDrive()
    drive = IndexApp.get_drive('MNEW')
    access = one.get_ms_token(**drive)
    one.access_token = access['access_token']

    # IndexApp.print_json(one.assign_license('0004@atcaoyufei.onmicrosoft.com', '94763226-9b3c-4e75-a931-5c89701abe66'))
    #
    # IndexApp.print_json(one.file_list(user_id='b88a6c34-0abe-446b-b53b-e410024cdf64'))
    # IndexApp.print_json(one.get_drives('1a46e535-bbaa-46e6-b32b-2122ee656d4c'))
    IndexApp.print_json(one.site('menwloc.sharepoint.com,7959fb7b-e58b-45d3-a01e-26c12be2d31d,252e09c2-e867-4772-8f29-e304bcb5ff91'))
