# -*- coding: utf-8 -*-

import requests
import os
import json

def _get_cookie_path(studio):
    '''
    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка :obj:`edit_db.studio` или любого из его потомков.
    '''
    path=os.path.join(os.path.expanduser('~'), studio.INIT_FOLDER, studio.COOKIE_NAME)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(path, mod=448)
    return path

def _get_user_data_path(studio):
    '''
    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка :obj:`edit_db.studio` или любого из его потомков.
    '''
    path=os.path.join(os.path.expanduser('~'), studio.INIT_FOLDER, studio.USER_DATA_FILE_NAME)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(path, mod=448)
    return path

def _write_cookie(studio, cookie):
    '''
    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка :obj:`edit_db.studio` или любого из его потомков.
    cookie: dict
        словарь кука
    '''
    with open(_get_cookie_path(studio), 'w') as f:
        f.write(json.dumps(cookie))

def _read_cookie(studio):
    '''
    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка :obj:`edit_db.studio` или любого из его потомков.
    '''
    if not os.path.exists(_get_cookie_path(studio)):
        raise Exception('No Auth!')
    with open(_get_cookie_path(studio), 'r') as f:
        cookie=json.load(f)
    return cookie

def _write_user_data(studio, user_data):
    '''
    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка :obj:`edit_db.studio` или любого из его потомков.
    user_data : dict, str
        Словарь данных пользователя.
    '''
    with open(_get_user_data_path(studio), 'w') as f:
        if isinstance(user_data, str):
            f.write(user_data)
        if isinstance(user_data, dict):
            f.write(json.dumps(user_data))

def get_user_data(studio):
    '''
    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка :obj:`edit_db.studio` или любого из его потомков.
    '''
    path=_get_user_data_path(studio)
    if not os.path.exists(path):
        return(False, 'User data file not found!')
    with open(path, 'r') as f:
        user_data=json.load(f)
    return (True, user_data)

def login(studio, username, password):
    '''
    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка :obj:`edit_db.studio` или любого из его потомков.
    username : str
        ...
    password : str
        ...
    '''
    login_url=f'{studio.HOST}db/user/login/'
       
    sess = requests.Session()
    # (1) get to login
    r1=sess.get(login_url)
    # (2) post to login
    csrf_token = r1.cookies.get('csrftoken')
    r2 = sess.post(login_url, data=dict(username=username, password=password, csrfmiddlewaretoken=csrf_token))
    # (3) write cookie
    cookie=r2.cookies
    _write_cookie(studio, dict(cookie))
    
    if not r2.ok:
        return(False, r2.text)

    # (4) write user_data
    _write_user_data(studio, r2.text)
    # 
    return (True, json.loads(r2.text))