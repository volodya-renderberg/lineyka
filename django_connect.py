# -*- coding: utf-8 -*-

import requests
import os
import json
import datetime
import uuid

HTML = '/tmp/mtest.html'

def _get_cookie_path(studio):
    '''
    Возвращает путь до файла ``cookie``.

    Parameters
    ----------
    studio : :obj:`edit_db.studio`
        Экземпляр объетка студии или любого из его потомков.

    Returns
    -------
    path
        Путь до файла ``cookie``.
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
        Экземпляр объетка студии или любого из его потомков.
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
        Экземпляр объетка студии или любого из его потомков.
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
        Экземпляр объетка студии или любого из его потомков.
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
        Экземпляр объетка студии или любого из его потомков.
    user_data : dict, str
        Словарь данных пользователя.
    '''
    with open(_get_user_data_path(studio), 'w') as f:
        if isinstance(user_data, str):
            f.write(user_data)
        if isinstance(user_data, dict):
            f.write(json.dumps(user_data))

def _input_data_converter(type_dict, data):
    """Преобразует данные полученные от ``django`` согласно типу из ``type_dict``.

    Преобразует:

    * дату время из ``iso``.
    * строки в ``json.dumps`` (если тип данных в ``type_dict`` = ``json``).
    * hex в ``uuid`` (для *id*).

    Parameters
    ----------
    type_dict : dict
        Словарь типа данных данного объекта в Линейке (например :attr:`edit_db.studio.workroom_keys`).
    data : dict
        Словарь объекта полученного от ``django``.

    Returns
    -------
    dict
        Словарь объекта с преобразованными данными.
    """
    for key in data.keys():
        if key=='id' and data.get(key) and isinstance(data[key], str) and len(data[key])>=32:
            data[key]=uuid.UUID(data[key])
        if type_dict.get(key)=='json':
            try:
                data[key]=json.loads(data[key])
            except:
                print(data[key])
                data[key]='Except'
        elif type_dict.get(key)=='timestamp':
            data[key]=datetime.datetime.fromisoformat(data[key])

    return data

def _output_data_converter(type_dict, inst, from_dict=False):
    """Преобразует данные для отправки в ``django``.

    Преобразует:

    * дату время в ``iso``.
    * Итерируемые объекты в строки (если тип данных в ``type_dict`` = ``json``).
    * ``uuid`` в hex (для *id*).
    * добавляет ``studio_name``.

    Parameters
    ----------
    type_dict : dict
        Словарь типа данных данного объекта в Линейке (например :attr:`edit_db.studio.workroom_keys`).
    inst : объект линейки, dict
        Объект линейки, преобразуемый в словарь для передачи в линейку или уже словарь (если ``from_dict`` = *True*).
    from_dict : bool
        Если *False* - то ``inst`` это объект линейки, если *True* - то словарь. 

    Returns
    -------
    str
        Словарь объекта с преобразованными данными в строковом представлении.
    """
    if from_dict:
        data=inst
    else:
        data = inst.__dict__.copy()
        data['studio_name']=inst.studio_name
    for key in data.keys():
        if key=='id' and isinstance(data[key], uuid.UUID):
            data[key]=data[key].hex
        elif type_dict.get(key)=='json':
            data[key]=json.dumps(data[key])
        elif type_dict.get(key)=='timestamp':
            if data[key]:
                data[key]=datetime.datetime.isoformat(data[key])

    r_data = json.dumps(data)
    del data
    return r_data

def _make_sess(lnk_object):
    """
    Создаёт сессию с куком сессии авторизованного пользователя. Чтение файла ``cookie``.

    Parameters
    ----------
    lnk_object : :obj:`edit_db.studio`
        Объект студии, или любого из его потомков.

    Returns
    -------
    :obj:`requests.Session`
        Сессия
    """
    cookie=_read_cookie(lnk_object)
    sess = requests.Session()
    cj=requests.utils.cookiejar_from_dict(cookie)
    sess.cookies=cj
    return cookie, sess 

def get_user_data(studio):
    '''
    Чтение словаря данных залогиненного пользователя из локального файла.

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

    .. attention:: Пустая процедура. Принадлежность к студии проверяется декоратором ``permissions.is_studio_member``

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

def user_get(artist, username):
    """
    Чтение данных артиста для текущей студии.

    Parameters
    ----------
    artist : :obj:`edit_db.artist`
        Экземпляр объетка :obj:`edit_db.artist`.
    username : str
        ``username`` читаемого артиста.

    Returns
    -------
    tuple
        (*True*, {User.__dict__}) или (*False, comment*)
    """
    url=f'{artist.HOST}db/user/get/{username}/'
    cookie=_read_cookie(artist)
    
    # (1) session
    sess = requests.Session()
    cj=requests.utils.cookiejar_from_dict(cookie)
    sess.cookies=cj
    # (1) get to login
    r1=sess.get(url, cookies = cookie)
    # (2) post to login
    csrf_token = r1.cookies.get('csrftoken')
    inst=_output_data_converter(artist.artists_keys, artist)
    r2 = sess.post(url, data=dict(inst=inst, csrfmiddlewaretoken=csrf_token))
        
    if not r2.ok:
        return(False, r2.text)
    #
    r_data = _input_data_converter(artist.artists_keys, r2.json())
    return (True, r_data)

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

def workroom_add(workroom, wr_name, wr_type):
    '''
    Parameters
    ----------
    workroom : :obj:`edit_db.workroom`
        Экземпляр объетка :obj:`edit_db.workroom`.
    wr_name : str
        Имя создаваемого объекта.
    wr_type : list
        Список типов для создаваемого отдела.

    Returns
    -------
    tuple
        (*True*, {Словарь созданного отдела}) или (*False, comment*)
    '''
    url=f'{workroom.HOST}db/workroom/add/'
    cookie=_read_cookie(workroom)

    # (1) session
    sess = requests.Session()
    cj=requests.utils.cookiejar_from_dict(cookie)
    sess.cookies=cj
    # (2) GET
    params=dict(studio_name=workroom.studio_name)
    r1=sess.get(url, cookies = cookie, params=params)
    #
    if not r1.ok:
        return(False, r1.text)

    # (3) POST
    csrf_token = r1.cookies.get('csrftoken')
    # ()
    wr_dict=_output_data_converter(workroom.workroom_keys, workroom)
    try:
        wr_type=json.dumps(wr_type)
    except:
        wr_type='[]'
    #
    r2=sess.post(url, data=dict(csrfmiddlewaretoken=csrf_token, cookies=cookie, wr_name=wr_name, wr_type=wr_type, inst=wr_dict))
    
    if not r2.ok:
        return(False, r2.text)
    #
    return(True, _input_data_converter(workroom.workroom_keys, r2.json()) )

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
    # (2) GET
    r1=sess.get(url, cookies = cookie)
    
    if not r1.ok:
        return(False, r1.text)

    data = r1.json()
    r_data=list()
    for item in data:
        r_data.append(_input_data_converter(studio.workroom_keys, item))

    return (True, r_data)

def workroom_rename(workroom, new_name):
    '''
    Parameters
    ----------
    workroom : :obj:`edit_db.workroom`
        Экземпляр изменяемого объетка :obj:`edit_db.workroom`.
    new_name : str
        Новое имя отдела.

    Returns
    -------
    tuple
        (*True*, {словарь отдела}) или (*False, comment*)
    '''
    url=f'{workroom.HOST}db/workroom/rename/'
    cookie=_read_cookie(workroom)
    
    # (1) session
    sess = requests.Session()
    cj=requests.utils.cookiejar_from_dict(cookie)
    sess.cookies=cj
    # (2) GET
    params=dict(studio_name=workroom.studio_name)
    r1=sess.get(url, cookies = cookie, params=params)
    #
    if not r1.ok:
        return(False, r1.text)

    # (3) POST
    csrf_token = r1.cookies.get('csrftoken')
    #
    wr_dict=_output_data_converter(workroom.workroom_keys, workroom)
    #
    r2=sess.post(url, data=dict(csrfmiddlewaretoken=csrf_token, cookies=cookie, new_name=new_name, inst=wr_dict))
    
    if not r2.ok:
        return(False, r2.text)
    #
    return(True, _input_data_converter(workroom.workroom_keys, r2.json()) )

def workroom_edit_type(workroom, new_type):
    '''
    Parameters
    ----------
    workroom : :obj:`edit_db.workroom`
        Экземпляр изменяемого объетка :obj:`edit_db.workroom`.
    new_type : list
        Список новых типов задач для отдела.

    Returns
    -------
    tuple
        (*True*, {словарь отдела}) или (*False, comment*)
    '''
    url=f'{workroom.HOST}db/workroom/edit_type/'
    cookie=_read_cookie(workroom)
    
    # (1) session
    sess = requests.Session()
    cj=requests.utils.cookiejar_from_dict(cookie)
    sess.cookies=cj
    # (2) GET
    params=dict(studio_name=workroom.studio_name)
    r1=sess.get(url, cookies = cookie, params=params)
    #
    if not r1.ok:
        return(False, r1.text)

    # (3) POST
    csrf_token = r1.cookies.get('csrftoken')
    #
    wr_dict=_output_data_converter(workroom.workroom_keys, workroom)
    #
    r2=sess.post(url, data=dict(csrfmiddlewaretoken=csrf_token, cookies=cookie, new_type=json.dumps(new_type), inst=wr_dict))
    
    if not r2.ok:
        return(False, r2.text)
    #
    return(True, _input_data_converter(workroom.workroom_keys, r2.json()) )

def workroom_get_artists(workroom):
    """
    Получение списка артистов отдела.

    .. note:: *params['studio_name']* передаётся для ``permission_required``.

    Parameters
    ----------
    workroom : :obj:`edit_db.workroom`
        Экземпляр читаемого объетка :obj:`edit_db.workroom`.

    Returns
    -------
    tuple
        (*True, [список словарей артистов]*) или (*False, comment*)
    """
    url=f'{workroom.HOST}db/workroom/get_artists/'
    cookie, sess =_make_sess(workroom)
    # (2) GET
    params=dict(studio_name=workroom.studio_name, wr_id=workroom.id)
    r1=sess.get(url, cookies = cookie, params=params)
    #
    if not r1.ok:
        return(False, r1.text)
    # (3) make return data
    r_data=list()
    i_data=r1.json()
    for user in i_data:
        r_data.append(_input_data_converter(workroom.artists_keys, user))
    #
    del i_data
    return (True, r_data)