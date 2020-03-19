# -*- coding: utf-8 -*-

import requests
import json

COOKIE_PATH = '/tmp/.cookie'

def _write_cookie(cookie):
    '''
    cookie: dict
    '''
    with open(COOKIE_PATH, 'w') as f:
        f.write(json.dumps(cookie))

def _read_cookie():
    if not os.path.exists(COOKIE_PATH):
        raise Exception('No Auth!')
    with open(COOKIE_PATH, 'r') as f:
        cookie=json.load(f)
    return cookie

def login(studio, username, password):
    login_url=f'{studio.HOST}db/user/login/'
       
    sess = requests.Session()
    # (1) get to login
    r1=sess.get(login_url)
    # (2) post to login
    csrf_token = r1.cookies.get('csrftoken')
    r2 = sess.post(login_url, data=dict(username=username, password=password, csrfmiddlewaretoken=csrf_token))
    # (3) write cookie
    cookie=r2.cookies
    _write_cookie(dict(cookie))

    if not r2.ok:
        return(False, r2.text)
    return (True, json.loads(r2.text))