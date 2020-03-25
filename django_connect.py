# -*- coding: utf-8 -*-

import requests
import os
import json
import datetime

HTML = '/tmp/mtest.html'

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

def _data_converter(c_dict, data):
    """Преобразует данные согласно типу.

    Преобразует:

    * дату время из ``iso``.
    * строки в ``json``.

    Parameters
    ----------
    c_dict : dict
        Словарь данных данного объекта в Линейке.
    data : dict
        Словарь объекта полученного от ``django``.

    Returns
    -------
    dict
        Словарь объекта с преобразованными данными.
    """
    for key in data.keys():
        if c_dict.get(key)=='json':
            data[key]=json.loads(data[key])
        elif c_dict.get(key)=='timestamp':
            data[key]=datetime.datetime.fromisoformat(data[key])

    return data

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

def is_member(studio, username):
    """
    Проверка является ли данный юзер, в составе данной студии. Для случая смены студии или перелогинивания пользователя.

    Returns
    -------
    tuple
        (*True, 'Ok!'*) или (*False, commit*)
    """
    pass

def test_exists_object(studio, model, field, value, translit=True):
    """
    Проверка наличия модели со значением определённого параметра.

    .. note:: Выполняется запрос ``count={model}.objects.filter({field}="{value}").count()``

    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка :obj:`edit_db.studio` или любого из его потомков.
    model : str
        Название *django* модели, нпример ``User``.
    field : str
        Название поля модели, например ``username``.
    value : str
        Значение данного поля. Для данного значения может быть сделана транслитерация.
    translit : bool, optional
        Если *True* - то будет произведена транслитерация ``value``.

    Returns
    -------
    tuple
        (*True, comment*) если совпадений нет, или (*False, comment*) если совпадение есть.
    """
    url=f'{studio.HOST}db/test_exists/'
    #
    sess = requests.Session()
    # (1) GET
    r1=sess.get(url)
    # (2) POST
    csrf_token = r1.cookies.get('csrftoken')
    r2 = sess.post(url, data=dict(model=model, field=field, value=value, translit=translit, csrfmiddlewaretoken=csrf_token))
    # (3) return
    if not r2.ok:
        return(False, r2.text)
    return (True, r2.text)

def user_registration(studio, username, email, password, login=False):
    '''
    Создание облачных пользователей.

    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка :obj:`edit_db.studio` или любого из его потомков.
    username : str
        ...
    email : str
        ...
    password : str
        ...
    login : bool, optional
        Если *True* - то будут записаны файлы :attr:`edit_db.studio.COOKIE_NAME` и :attr:`edit_db.studio.USER_DATA_FILE_NAME`.
    
    Returns
    -------
    tuple
        (*True*, {User.__dict__}) или (*False, comment*)

    '''

    url=f'{studio.HOST}db/user/rgistration/'
        
    sess = requests.Session()
    # (1) get to login
    r1=sess.get(url)
    # (2) post to login
    csrf_token = r1.cookies.get('csrftoken')
    r2 = sess.post(url, data=dict(username=username, password=password, email=email, csrfmiddlewaretoken=csrf_token))
        
    if not r2.ok:
        # with open(HTML, 'w') as f:
        #     f.write(r2.text)
        # webbrowser.open(HTML)

        return(False, r2.text)

    if login:
        # (3) write cookie
        cookie=r2.cookies
        _write_cookie(studio, dict(cookie))

        # (4) write user_data
        _write_user_data(studio, r2.text)
    # 
    return (True, json.loads(r2.text))

def login(studio, username, password):
    '''
    Логин, запись файлов :attr:`edit_db.studio.COOKIE_NAME` и :attr:`edit_db.studio.USER_DATA_FILE_NAME`.

    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка :obj:`edit_db.studio` или любого из его потомков.
    username : str
        ...
    password : str
        ...

    Returns
    -------
    tuple
        (*True*, {User.__dict__}) или (*False, comment*)
    '''
    login_url=f'{studio.HOST}db/user/login/'
       
    sess = requests.Session()
    # (1) get to login
    r1=sess.get(login_url)
    # (2) post to login
    csrf_token = r1.cookies.get('csrftoken')
    r2 = sess.post(login_url, data=dict(username=username, password=password, csrfmiddlewaretoken=csrf_token))
        
    if not r2.ok:
        return(False, r2.text)

    # (3) write cookie
    cookie=r2.cookies
    _write_cookie(studio, dict(cookie))

    # (4) write user_data
    _write_user_data(studio, r2.text)
    # 
    return (True, json.loads(r2.text))

def studio_create(studio, studio_name, studio_label):
    """Создание студии.

    * Создание объекта *Studio*.
    * Создание группы (*Group*) с именем ``<studio_name>_head``.
    * Создание для группы ``permissions`` расширенных прав: ``'add'``, ``'change'``, ``'delete'``, ``'view'``.
    * Добавление текущего пользователя в группу и в студию.

    Parameters
    ----------
    studio_name : str
        Имя студии.
    studio_label : str
        Лейбл студии.

    Returns
    -------
    tuple
        (*True*, {studio_dict}) или (*False, comment*).
    """
    url=f'{studio.HOST}db/studio/create/'
    cookie=_read_cookie(studio)
    
    # (1) session
    sess = requests.Session()
    cj=requests.utils.cookiejar_from_dict(cookie)
    sess.cookies=cj
    # (2) get to create
    r1=sess.get(url, cookies = cookie)
    # (3) post to create
    csrf_token = r1.cookies.get('csrftoken')
    r2=sess.post(url, data=dict(csrfmiddlewaretoken=csrf_token, cookies=cookie, studio_label=studio_label, studio_name=studio_name))

    if not r2.ok:
        return(False, r2.text)
    return (True, r2.text)

def studio_get_list(studio):
    '''
    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка :obj:`edit_db.studio` или любого из его потомков.

    Returns
    -------
    tuple
        (*True*, [список словарей]) или (*False, comment*)
    '''
    url=f'{studio.HOST}db/studio/get_list/'
    cookie=_read_cookie(studio)
    
    # (1) session
    sess = requests.Session()
    cj=requests.utils.cookiejar_from_dict(cookie)
    sess.cookies=cj
    # (2) get to create
    r1=sess.get(url, cookies = cookie)
    
    if not r1.ok:
        return(False, r1.text)

    return (True, r1.json())

def workroom_get_list(studio):
    '''
    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка :obj:`edit_db.studio` или любого из его потомков.

    Returns
    -------
    tuple
        (*True*, [список словарей]) или (*False, comment*)
    '''
    url=f'{studio.HOST}db/workroom/get_list/{studio.studio_name}'
    cookie=_read_cookie(studio)

    # (1) session
    sess = requests.Session()
    cj=requests.utils.cookiejar_from_dict(cookie)
    sess.cookies=cj
    # (2) get to create
    r1=sess.get(url, cookies = cookie)
    
    if not r1.ok:
        return(False, r1.text)

    data = r1.json()
    r_data=list()
    for item in data:
        r_data.append(_data_converter(studio.workroom_keys, item))

    return (True, r_data)
