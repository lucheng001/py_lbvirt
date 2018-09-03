#!/usr/bin/python3.6

import json

def rsp_data(rsp_code=0, msg=None, data=None):
    return {'rsp_code': rsp_code, 'msg': msg, 'data': data}

def load_json(data):
    return json.loads(data)

