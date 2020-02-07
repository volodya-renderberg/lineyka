#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
#import sys
import platform
import json
import sqlite3
import datetime
import getpass
import random
import shutil
import uuid
import tempfile
import subprocess

try:
    from .lineyka_publish import publish
except:
    from lineyka_publish import publish

def NormPath(input_path):
    if not input_path:
        return(input_path)
    if platform.system() == 'Windows':
            # windows
            path = str(input_path)
            path = os.path.normpath(path.encode('string-escape'))
    else:
        # linux etc...
        path = os.path.normpath(input_path)
    return(path)

def print_args(fn):
    def inner_fn(*args):
        print(args)
        return fn(*args)
    return(inner_fn)

class studio:
    """Базовый класс для всех остальных классов.
    
    Создание экземпляра обязательно, прежде всего.
    """

    farme_offset = 100
    """int: Номер кадра, который будет считаться стартовым для сцен анимации. """
    studio_folder = False
    """str: Директория студии. """
    tmp_folder = False
    """str: *tmp* директория пользователя, в неё копируются открываемые сцены. """
    work_folder = False
    """str: Директория для локального хранения ассетов пользователя. Создаётся вся файловая структура ``project/assets/asset/activity/version_dir/file``. Определяе методом :func:`edit_db.studio.set_work_folder`. """
    convert_exe = False
    """str: Путь к исполняемому файлу *convert* приложения 'Imagemagick' """
    studio_database = ['sqlite3', False]
    """list: Определение используемой в студии базы данных. """
    init_path = False
    """str: ``?`` """
    set_path = False
    """str: ``?`` """
    share_dir = False
    """str: ``?`` """
    list_projects = {}
    """list: ``?`` """
    list_active_projects = []
    """list: ``?`` """
    extensions = ['.blend', '.ma', '.tiff', '.ntp']
    """list: Список возможных расширений для рабочих файлов, которым будет сопоставляться приложение. 
    
    Заполняется в :func:`edit_db.studio.get_studio`
    
    .. note:: Возможно совершенно бесполезный атрибут, так как эти значения есть :attr:`edit_db.studio.setting_data` ['extension'].keys()
    """
    setting_data = {
    'extension': {
        '.tiff':'krita',
        '.blend': 'blender',
        '.ntp': 'natron',
        '.ma': 'maya',
        '.ods':'libreoffice',
        },
    'task_visible_fields':[
        'activity',
        'task_type',
        'artist',
        'priority',
        'extension',]}
    """dict: словарь пользовательский настроек. Хранится в *json* файле :attr:`edit_db.studio.set_file`
    
    :Значения по ключам: * **extension** (dict): ключи - расширения файлов, значения - приложение которое им соответствует (имя экзешника или путь к нему).
                         * **task_visible_fields** (list): список полей, отображаемых в ячейке задачи таблицы таск менеджера.
    
    .. note:: А возможно наоборот превратить этот словарь в два атрибута, соответсвующих его ключам.
    """
    look_extension = '.jpg'
    """str: расширение файла изображения, которое используется в просмотре. """
    preview_extension = '.png'
    """str: расширение файла изображения, которое используется при создании превью изображения. """
    publish_folder_name = 'publish'
    """str: имя паблиш директории """
    soft_data = None
    """ ``?`` """
    priority = ('normal', 'high', 'top', 'ultra')
    """tuple: Список используемых приоритетов
    
    .. note:: Возможно устарело, так как мы перешли просто на множество натуральных чисел (от 0 до бесконечности).
    """
    user_levels = ('user', 'extend_user', 'manager', 'root')
    """tuple: Список существующих пользователей
    
    .. note:: Возможно стоит добавить ``superroot`` - который будет всего один, когда root`ов может быть сколько угодно.
    """
    manager_levels = ('manager', 'root')
    """tuple: Список пользовательских уровней, обладающих функцией менеджера. """
    task_status = ('null','ready', 'ready_to_send', 'work', 'work_to_outsorce', 'pause', 'recast', 'checking', 'done', 'close')
    """tuple: список существующих статусов задач. """
    working_statuses = ('ready', 'ready_to_send', 'work', 'work_to_outsorce', 'pause', 'recast')
    """tuple: Список статусов задач, не выполненного состояния.
    
    .. note:: Возможно тупость, достаточно просто проверять, находится ли статуc в :attr:`edit_db.studio.end_statuses`
    """
    end_statuses = ('done', 'close')
    """tuple: Статусы задач завершённого состояния. """

    #NOT_USED_EXTENSIONS = ['.blend','.tiff', '.ods', '.xcf', '.svg']
    EMPTY_FILES_DIR_NAME = 'empty_files'
    """str: имя директории для хранения пользовательских заготовок файлов, для тех приложений, которые не могут создавать пустой файл при открытии по несуществующему пути.
    
    Создаётся в :func:`edit_db.studio.make_init_file`
    
    Расположение в директории: ``~/.lineyka/``
    """

    color_status = {
    'null':(0.451000005, 0.451000005, 0.451000005),
    #'ready':(0.7627863884, 0, 1),
    'ready':(0.826, 0.249, 1),
    'ready_to_send':(0.9367088675, 0.2608556151, 0.4905878305),
    'work':(0.520749867, 0.7143493295, 0.8227847815),
    'work_to_outsorce':(0.2161512673, 0.5213058591, 0.8987341523),
    #'pause':(0.3417721391, 0.2282493114, 0.1557442695),
    'pause':(0.670, 0.539, 0.827),
    'recast':(0.8481012583, 0.1967110634, 0.1502964497),
    'checking':(1, 0.5872552395, 0.2531645298),
    'done':(0.175, 0.752, 0.113),
    #'close':(0.1645569652, 0.08450711519, 0.02499599569)
    'close':(0.613, 0.373, 0.195)
    }
    """dict: ключ - название статуса задачи, значение - соответствующий ему ``rgb`` (0 - 1) """

    projects_units = ('m', 'cm', 'mm')
    """tuple: Список возможных размерностей юнита 3d сцен. """
    
    PROJECTS_STATUSES = ('active', 'none')
    """tuple: Список возможных статусов для проектов. """

    task_types = (
    # -- film
    'animatic',
    'film',
    #
    'sketch',
    'textures',
    # -- model
    'sculpt',
    'model',
    # -- rig
    'rig',
    'test_animation', # анимация для проверки рига - активити test_animation
    # -- location,
    'specification',
    'location',
    #'location_full',
    #'location_for_anim',
    # -- animation
    'animation_shot',
    'tech_anim',
    'simulation_din',
    #'simulation_fluid',
    'render',
    'composition',
    )
    """tuple: Список используемых типов задач. """

    multi_publish_task_types = ('sketch',)
    """tuple: Список задач, для которых возможен паблиш всех существующих веток, подробнее тут :ref:`branch-page` и тут :ref:`commit-push-publish-page`. """

    service_tasks = ('all', 'pre')
    """tuple: Префиксы сервисных задач. """

    asset_types = (
    'object',
    'location',
    'shot_animation',
    'film'
    )
    """tuple: Список используемых типов ассетов. """

    asset_types_with_season = (
    'animatic',
    'shot_animation',
    'camera',
    'shot_render',
    'shot_composition',
    'film'
    )
    """tuple: Список ассетов для которых имеет значение сезон.
    
    .. attention:: Совсем устаревшее, возможно надо полностью удалить.
    """

    asset_keys = {
    'name': 'text',
    'group': 'text',
    #'path': 'text', # каждый раз определяется при инициализации.
    'type': 'text',
    'loading_type': 'text', # способ загрузки ассета object в анимационную сцену, значения из studio.loading_types
    'season': 'text',
    'priority': 'integer',
    'description': 'text',
    'content': 'text',
    'id': 'text',
    'status': 'text',
    'parent': 'json' # {'name':asset_name, 'id': asset_id} - возможно не нужно
    }
    """dict: Обозначение данных хранимых в БД для объектов :obj:`edit_db.asset` . Ключи - заголовки, значения - тип данных БД. """

    loading_types = ('mesh', 'group', 'rig')
    """tuple: Типы загрузок ассетов в сцену. """

    # constants (0 - 3 required parameters)
    tasks_keys = {
    'activity': 'text',
    'task_name': 'text',
    'task_type': 'text',
    'source': 'json',
    'input': 'json',
    'status': 'text',
    'outsource': 'integer',
    'artist': 'text',
    'level': 'text',        # пользовательский уровень сложности задачи.
    'planned_time': 'real',
    'time':  'json',        # словарь: ключи - nik_name, значения - ссумарное время атриста по этой задаче (ед. измерения - секунда).
    'full_time': 'real',    # ссумарное время всех атристов по этой задаче (ед. измерения - секунда).
    'deadline': 'timestamp',# расчётная дата окончания работ
    'start': 'timestamp',
    'end': 'timestamp',
    'price': 'real',
    'specification': 'text',
    'chat_local': 'json',
    'web_chat': 'text',
    'supervisor': 'text',
    'readers': 'json',
    'output': 'json',
    'priority':'integer',
    'extension': 'text',
    'description': 'text',  # описание задачи
    }
    """dict: Обозначение данных хранимых в БД для объектов :obj:`edit_db.task` . Ключи - заголовки, значения - тип данных БД. """
    
    workroom_keys = {
    'name': 'text',
    'id': 'text',
    'type': 'json'
    }
    """dict: Обозначение данных хранимых в БД для объектов :obj:`edit_db.workroom` . Ключи - заголовки, значения - тип данных БД. """

    statistics_keys = (
    ('project_name', 'text'),
    ('task_name', 'text'),
    ('data_start', 'timestamp'),
    ('data_end', 'timestamp'),
    ('long_time', 'text'),
    ('cost', 'text'),
    ('status', 'text')
    )
    """(tuple) ``?`` """
    
    artists_keys = {
    'nik_name': 'text',
    'user_name': 'text',
    'password': 'text',
    'date_time': 'timestamp',
    'email': 'text',
    'phone': 'text',
    'specialty': 'text',
    'outsource': 'integer',
    'workroom': 'json',# список id отделов
    'level': 'text',
    'share_dir': 'text',
    'status': 'text',
    'working_tasks': 'json',# список имён назначенных в работу задач
    'checking_tasks': 'json',# список имён назначенных на проверку задач
    }
    """dict: Обозначение данных хранимых в БД для объектов :obj:`edit_db.artist` . Ключи - заголовки, значения - тип данных БД. """
    
    chats_keys = {
    'message_id':'text',
    'date_time': 'timestamp',
    'date_time_of_edit': 'timestamp',
    'author': 'text',
    'topic': 'json',
    'color': 'json',
    'status': 'text',
    'reading_status': 'json',
    }
    """dict: Обозначение данных хранимых в БД для объектов :obj:`edit_db.chat` . Ключи - заголовки, значения - тип данных БД. """

    projects_keys = {
    'name': 'text',
    'path': 'text',
    'status': 'text',
    'project_database': 'json',
    'chat_img_path': 'text',
    'list_of_assets_path': 'text',
    'preview_img_path': 'text',
    'fps': 'real',
    'units': 'text',
    }
    """dict: Обозначение данных хранимых в БД для объектов :obj:`edit_db.project` . Ключи - заголовки, значения - тип данных БД. """

    group_keys = {
    'name': 'text',
    'type': 'text',
    'season': 'text',
    'description': 'text',
    'id': 'text',
    }
    """dict: Обозначение данных хранимых в БД для объектов :obj:`edit_db.group` . Ключи - заголовки, значения - тип данных БД. """

    season_keys = {
    'name': 'text',
    'status':'text',
    'id': 'text',
    }
    """dict: Обозначение данных хранимых в БД для объектов :obj:`edit_db.season` . Ключи - заголовки, значения - тип данных БД.
    
    .. attention:: Устаревшее, так же как и класс, смотри :ref:`season-series-shot-page`.
    """

    list_of_assets_keys = (
    'asset_name',
    'asset_type',
    'set_of_tasks',
    )
    """tuple: ``?`` """
    
    logs_keys = {
    'version': 'text',
    'date_time': 'timestamp',
    'activity': 'text',
    'task_name': 'text',
    'action': 'text',
    'artist': 'text',
    'description': 'text',
    'source': 'json', # для push - версия коммита источника (в случае sketch - список версий по всем веткам, порядок совпадает с порядком записи веток в branch), для publish - версия push источника.
    'branch' : 'json', # ветка - в случае push, publish для sketch - списки веток.
    'time' : 'real', # время затраченное на commit, ед. измерения секунда.
    }
    """dict: Обозначение данных хранимых в БД для лога задачи (на самом деле - лог активити ассета). Ключи - заголовки, значения - тип данных БД. Спецификация :ref:`time-log-page`"""

    artists_logs_keys = {
    'project_name': 'text',
    'task_name': 'text',
    'full_time': 'integer', # суммарное время затраченое артистом на задачу, ед. измерения секунда.
    'price': 'real', 		# сумма начисленная за выполнение задачи. вносится по принятию задачи.
    'start': 'timestamp', 	# дата-время создания записи, запись создаётся при первом open задачи.
    'finish': 'timestamp',  # дата-время принятия задачи.
    }
    """dict: Обозначение данных хранимых в БД для лога *артиста*. Автоматическое заполнение при выполнении :func:`edit_db.task.commit`. Строка - задача. Ключи - заголовки, значения - тип данных БД. Спецификации - :ref:`commit-push-publish-page` и :ref:`time-log-page` """

    # лог артиста по дням, заполняемый вручную: день/проект/задача/время
    artists_time_logs_keys = {
    'project_name':'text',
    'task_name':'text',
    'date':'timestamp',  # возможно только дата без времени?
    'time':'integer',    # суммарное время затраченое артистом на задачу, ед. измерения секунда. Заполняется вручную.
    }
    """dict: Обозначение данных хранимых в БД для тайм лога *артиста*. Заполнение вручную по дням, для корректировки автозаполнения. Строка - задача/день. Ключи - заголовки, значения - тип данных БД. Спецификация :ref:`time-log-page`"""

    init_folder = '.lineyka'
    """str: Имя домашней директории линейки с файлами пользовательской конфигурации. Расположение в ``~/`` """
    init_file = 'lineyka_init.json'
    """str: Имя *json* файла конфигурации. Содержит пути. 
    
    Создаётся в :func:`edit_db.studio.make_init_file`
    
    Расположение в ~/:attr:`edit_db.studio.init_folder`/
    """
    set_file = 'user_setting.json'
    """str: Имя *json* файла конфигурации пользователя. Содержит словарь :attr:`edit_db.studio.setting_data`
    
    Создаётся в :func:`edit_db.studio.make_init_file`
    
    Расположение в ~/:attr:`edit_db.studio.init_folder`/
    """
    location_position_file = 'location_content_position.json'
    """str: ``?`` """
    user_registr_file_name = 'user_registr.json'
    """str: ``?`` """
    recycle_bin_name = '-Recycle_Bin-'
    """str: Имя группы корзины удаляемых ассетов. """
    list_of_assets_name = '.list_of_assets.json'
    """str: ``?`` """
    PROJECT_SETTING = '.project_setting.json'
    """str: имя *json* файла c параметрами проекта, дублируются из базы данных. Применяются к проекту при его повторном добавлении в студию. """

    #database files
    projects_db = '.projects.db'
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных :obj:`edit_db.project` """
    projects_t = 'projects'
    """str: Имя таблицы БД для :obj:`edit_db.project` """
    assets_db = '.assets.db'
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных :obj:`edit_db.asset`. Имя таблицы - тип ассета. """
    #assets_t = 'assets' # имя таблицы - тип ассета
    artists_db = '.artists.db'
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных :obj:`edit_db.artist` """
    artists_t = 'artists'
    """str: Имя таблицы БД для :obj:`edit_db.artist` """
    workroom_db = artists_db
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных :obj:`edit_db.workroom` """
    workroom_t = 'workrooms'
    """str: Имя таблицы БД для :obj:`edit_db.workroom` """
    statistic_db = '.statistic.db'
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных :obj:`edit_db.statistic` """
    statistic_t = 'statistic'
    """str: Имя таблицы БД для :obj:`edit_db.statistic` """
    season_db = assets_db
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных :obj:`edit_db.season` """
    season_t = 'season'
    """str: Имя таблицы БД для :obj:`edit_db.season` """
    group_db = assets_db
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных :obj:`edit_db.group` """
    group_t = 'groups'
    """str: Имя таблицы БД для :obj:`edit_db.group` """
    tasks_db = '.tasks.db'
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных :obj:`edit_db.task` """
    tasks_t = 'tasks'
    """str: Имя таблицы БД для :obj:`edit_db.task` """
    logs_db = '.tasks_logs.db'
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных логов задачи/активити, :obj:`edit_db.log`. """
    logs_t = 'logs'
    """str: Имя таблицы БД для лога задачи/активити """
    artists_logs_db = '.artists_logs.db'
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных логов \`артистов, :obj:`edit_db.log`.
    
    Имя таблицы - '[nik_name]_tasks_logs'
    """
    artists_time_logs_db = '.artists_time_logs.db'
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных тайм логов \`артистов, :obj:`edit_db.log`.
    
    Имя таблицы - '[nik_name]_time_logs'
    """
    chats_db = '.chats.db'
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных :obj:`edit_db.chat` """
    set_of_tasks_db = '.set_of_tasks.db'
    """str: Имя файла ДБ (для Sqlite3) где содержится таблица данных :obj:`edit_db.set_of_tasks` """
    set_of_tasks_t = 'set_of_tasks'
    """str: Имя таблицы БД для :obj:`edit_db.set_of_tasks` """
    meta_data_file = '.shot_meta_data.json'
    """str: Имя *json* файла с метадатой шота. Хранение в ``asset_folder/common/`` """
    
    # blender
    blend_service_images = {
        'preview_img_name' : 'Lineyka_Preview_Image',
        'bg_image_name' : 'Lineyka_BG_Image',
        }
    """dict: Имена служебных файлов графических изображений, которые не сохраняются в ``asset_folder/textures/`` при выполнении процедуры ``Save Images`` в блендер аддоне. """
        
    def __init__(self):
        self.make_init_file()
        self.get_studio()

    @classmethod
    def make_init_file(self):
        """Создание при их отсутствии:
        
        * :attr:`edit_db.studio.init_file` 
        * :attr:`edit_db.studio.set_file`
        * :attr:`edit_db.studio.EMPTY_FILES_DIR_NAME`
        
        Расположение файлов ~/:attr:`edit_db.studio.init_folder`/
        
        Returns
        -------
        None
            *None*
        """
        
        home = os.path.expanduser('~')
        
        folder = NormPath(os.path.join(home, self.init_folder))
        empty_folder = NormPath(os.path.join(folder, self.EMPTY_FILES_DIR_NAME))
        self.init_path = NormPath(os.path.join(home, self.init_folder, self.init_file))
        self.set_path = NormPath(os.path.join(folder, self.set_file))
        
        # make folder
        if not os.path.exists(folder):
            os.mkdir(folder)
        if not os.path.exists(empty_folder):
            os.mkdir(empty_folder)
        
        # make init_file
        if not os.path.exists(self.init_path):
            # make jason
            d = {
                'studio_folder': None,
                'work_folder': None,
                'convert_exe': None,
                'tmp_folder': tempfile.gettempdir(),
                'use_database': ['sqlite3', False],
                }
            m_json = json.dumps(d, sort_keys=True, indent=4)
            # save
            data_fale = open(self.init_path, 'w')
            data_fale.write(m_json)
            data_fale.close()
            
        # make set_file
        if not os.path.exists(self.set_path):
            # make jason
            d = self.setting_data
            m_json = json.dumps(d, sort_keys=True, indent=4)
            # save
            data_fale = open(self.set_path, 'w')
            data_fale.write(m_json)
            data_fale.close()

    @classmethod
    def set_studio(self, path):
        """Инициализация студийной директории.
        
        * Перезапись :attr:`edit_db.studio.init_file`
        * Создание файловой структуры, при остуствии.
        
        Parameters
        ----------
        path : str
            Путь до новой директории студии.
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        if not os.path.exists(path):
            return(False, "****** to studio path not Found!")
        
        home = os.path.expanduser('~')	
        init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
        if not os.path.exists(init_path):
            return(False, "****** init_path not Found!")
        
        # write studio path
        try:
            with open(init_path, 'r') as read:
                data = json.load(read)
                data['studio_folder'] = path
                read.close()
        except:
            return(False, "****** in set_studio() -> init file  can not be read")

        try:
            with open(init_path, 'w') as f:
                jsn = json.dump(data, f, sort_keys=True, indent=4)
                f.close()
        except:
            return(False, "****** in set_studio() ->  init file  can not be read")

        self.studio_folder = path
        
        return(True, 'Ok')

    @classmethod
    def set_tmp_dir(self, path):
        """Определение пользовательской *tmp* директории - :attr:`edit_db.studio.tmp_folder`, в неё копируются открываемые сцены.
        
        Parameters
        ----------
        path : str
            Путь до *tmp* директории.
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        if not os.path.exists(path):
            return "****** to studio path not Found!"
        
        home = os.path.expanduser('~')	
        init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
        if not os.path.exists(init_path):
            return "****** init_path not Found!"
        
        # write studio path
        try:
            with open(init_path, 'r') as read:
                data = json.load(read)
                data['tmp_folder'] = path
                read.close()
        except:
            return "****** init file  can not be read"

        try:
            with open(init_path, 'w') as f:
                jsn = json.dump(data, f, sort_keys=True, indent=4)
                f.close()
        except:
            return "****** init file  can not be read"

        self.tmp_folder = path
                
        return(True, 'Ok')

    @classmethod
    def set_convert_exe_path(self, path):
        """Определение пути до исполняемого файла *convert* приложения ‘Imagemagick’, параметр :attr:`edit_db.studio.convert_exe`.
        
        Parameters
        ----------
        path : str
            Путь до файла *convert* .
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        pass
        #if not os.path.exists(path):
            #return(False, "****** to convert.exe path not Found!")
        
        home = os.path.expanduser('~')
        init_path = NormPath(os.path.join(home, self.init_folder, self.init_file))
        if not os.path.exists(init_path):
            return(False, "****** init_path not Found!")
        
        # write path
        try:
            with open(init_path, 'r') as read:
                data = json.load(read)
                data['convert_exe'] = NormPath(path)
                read.close()
        except:
            return(False, "****** init file  can not be read")

        try:
            with open(init_path, 'w') as f:
                jsn = json.dump(data, f, sort_keys=True, indent=4)
                f.close()
        except:
            return(False, "****** init file  can not be read")

        self.convert_exe = path
        
        return(True, 'Ok!')

    @classmethod
    def set_work_folder(self, path):
        """Определение директории для локального хранения ассетов пользователя, параметр :attr:`edit_db.studio.work_folder`.
        
        Parameters
        ----------
        path : str
            Путь до директории.
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        if not os.path.exists(path):
            return(False, 'The path "%s" - not Found!' % path)
        
        home = os.path.expanduser('~')
        init_path = NormPath(os.path.join(home, self.init_folder, self.init_file))
        if not os.path.exists(init_path):
            return(False, "****** init_path not Found!")
        
        # write path
        try:
            with open(init_path, 'r') as read:
                data = json.load(read)
                data['work_folder'] = NormPath(path)
                read.close()
        except:
            return(False, "****** init file  can not be read")

        try:
            with open(init_path, 'w') as f:
                jsn = json.dump(data, f, sort_keys=True, indent=4)
                f.close()
        except:
            return(False, "****** init file  can not be read")

        self.work_folder = path
        
        return True, 'Ok'

    def _template_version_num(self, version):
        """Приобразование номера версии к строке нужного формата (от 4 симолов).
        
        Examples
        --------
        
        .. code-block:: python
        
            >> import edit_db as db
            >> db.studio._template_version_num(5)
            >> (True, '0005')
            >> db.studio._template_version_num('25')
            >> (True, '0025')
        
        Parameters
        ----------
        version : str, int
            Номер или строковое представление номера.
            
        Returns
        -------
        tuple
            (*True*, str_version) или (*False*, comment)
        """
        try:
            str_version = '{:04d}'.format(int(version))
            return(True, str_version)
        except:
            return (False, 'Wrong version format "%s"' %  str(version))

    def _template_get_work_path(self, c_task, version=False):
        """Шаблонный путь к файлу или активити в рабочей директории пользователя (:attr:`edit_db.studio.work_folder`).
        
        Examples
        --------
        
        .. code-block:: python
        
            >> import edit_db as db
            >> ...
            >> # получаем объект текущей задачи current_task
            >> ...
            >> db._template_get_work_path(current_task, version=25)
            >> (True, 'path_to_work_folder/project_folder_name/assets/asset_name/activity_name/'0025'/asset_name.ext')
            >> db._template_get_work_path(current_task)
            >> (True, 'path_to_work_folder/project_folder_name/assets/asset_name/activity_name/')
        
        Parameters
        ----------
        c_task : :obj:`edit_db.task`
            Объект задачи, для которой ищется файл.
            
        version : int, str, optional
            Версия, число или строковое представление, если *False* - то возврат только пути до активити.
            
        Returns
        -------
        tuple
            (*True*, path) или (*False*, comment)
        """
        pass
        # exists work folder
        if not self.work_folder:
            return(False, 'Working directory not defined!')
        elif not os.path.exists(self.work_folder):
            return(False, 'The path "%s" to working directory does not exist!' % self.work_folder)
        
        if version or version==0:
            # test version
            b, str_version = self._template_version_num(version)
            if not b:
                return (b, str_version)
            # file path
            return (True, NormPath(os.path.join(self.work_folder, c_task.asset.project.name, 'assets', c_task.asset.name, c_task.activity, str_version, '%s%s' % (c_task.asset.name, c_task.extension))))
        else:
            # activity path
            return (True, NormPath(os.path.join(self.work_folder, c_task.asset.project.name, 'assets', c_task.asset.name, c_task.activity)))

    def _template_get_push_path(self, c_task, version=False, branches=False, look=False): # v2
        """Шаблонный путь к файлу или активити *push* версии на сервере студии.
        
        Examples
        --------
        
        .. code-block:: python
        
            >> import edit_db as db
            >> ...
            >> # получаем объект текущей задачи current_task
            >> ...
            >> db._template_get_push_path(current_task, version=25, branches=['master', 'branch1'], look=True)
            >> (True, {'master' : 'path_to_project/assets/asset_name/activity_name/'0025'/asset_name#master.look_extension',
                       'branch1' : 'path_to_project/assets/asset_name/activity_name/'0025'/asset_name#branch1.look_extension'})
            >> db._template_get_push_path(current_task, version=25)
            >> (True, 'path_to_project/assets/asset_name/activity_name/'0025'/asset_name.ext')
            >> db._template_get_push_path(current_task)
            >> (True, 'path_to_project/assets/asset_name/activity_name/')
        
        Parameters
        ----------
        c_task : :obj:`edit_db.task`
            Объект задачи, для которой ищется файл.
            
        version : int, str, optional
            Версия, число или строковое представление, если *False* - то возврат только пути до активити.
            
        branches : list, optional
             Список веток из которых делался *push* - для *task_type* из списка :attr:`edit_db.studio.multi_publish_task_types` (например *'sketch'*).
             
        look : bool, optional
            Рассматривается только если *task_type* из списка :attr:`edit_db.studio.multi_publish_task_types` (например *'sketch'*), если *False* - то используется *c_task.extension*, если *True* - то используется :attr:`edit_db.studio.look_extension`.
            
        Returns
        -------
        tuple
            * (*True*, path) или (*False*, comment)
            * (*True*, {branch_name : path1, ...}) или (*False*, comment) - для *task_type* из списка :attr:`edit_db.studio.multi_publish_task_types` (например *'sketch'*)
        """
        pass
        # 1 - task_type = sketch
        # 1.1 - преобразование version
        # 1.2 - branches - тест типа данных
        # 1.3 - получение списка путей
        # 2 - не sketch
        # 2.1 - преобразование version
        # 2.2 - путь до файла
        # 2.3 - путь до активити
        
        # (1)
        if c_task.task_type in self.multi_publish_task_types:
            #
            if not version is False:
                # ( 1.1)
                b, str_version = self._template_version_num(version)
                if not b:
                    return (b, str_version)
                # (1.2)
                if not isinstance(branches, list):
                    return(False, 'Branch data type should be a "list" and not a "%s"' % branches.__class__.__name__)
                # (1.3)
                path_dict = dict()
                for branch in branches:
                    if look:
                        path_dict[branch] = NormPath(os.path.join(c_task.asset.path, c_task.activity, str_version, '%s#%s%s' % (c_task.asset.name, branch, self.look_extension)))
                    else:
                        path_dict[branch] = NormPath(os.path.join(c_task.asset.path, c_task.activity, str_version, '%s#%s%s' % (c_task.asset.name, branch, c_task.extension)))
                return(True, path_dict)
                
            else:
                return (True, NormPath(os.path.join(c_task.asset.path, c_task.activity)))
        # (2)
        else:
            if not version is False:
                # ( 2.1)
                b, str_version = self._template_version_num(version)
                if not b:
                    return (b, str_version)
                # (2.2)
                return (True, NormPath(os.path.join(c_task.asset.path, c_task.activity, str_version, '%s%s' % (c_task.asset.name, c_task.extension))))
            else:
                # (2.3)
                return (True, NormPath(os.path.join(c_task.asset.path, c_task.activity)))

    def _template_get_publish_path(self, c_task, version=False, branches=list(), look=False): # v2
        """Получение шаблонных путей для *publish* версий на сервере студии.
        
        .. note:: Если не передавать ``version`` - то будет получен путь к файлам, которые располагаются сверху директорий версий - это файлы последней версии.
        
        Examples
        --------
        
        .. code-block:: python
        
            >> import edit_db as db
            >> ...
            >> # получаем объект текущей задачи current_task
            >> ...
            >> db._template_get_publish_path(current_task, version=25, branches=['master', 'branch1'], look=True)
            >> (True, {'master' : 'path_to_project/assets/asset_name/publish/activity_name/'0025'/asset_name#master.look_extension',
                       'branch1' : 'path_to_project/assets/asset_name/publish/activity_name/'0025'/asset_name#branch1.look_extension'})
            >> db._template_get_publish_path(current_task, version=25)
            >> (True, 'path_to_project/assets/asset_name/publish/activity_name/'0025'/asset_name.ext')
            >> # Путь до финальной версии (для не скетч)
            >> db._template_get_publish_path(current_task)
            >> (True, 'path_to_project/assets/asset_name/publish/activity_name/asset_name.ext')
            >> # Путь до финальной версии (для скетч)
            >> db._template_get_publish_path(current_task, branches=['master', 'branch1'])
            >> (True, {'master' : 'path_to_project/assets/asset_name/publish/activity_name/asset_name#master.ext',
                       'branch1' : 'path_to_project/assets/asset_name/publish/activity_name/asset_name#branch1.ext'})
        
        Parameters
        ----------
        c_task : :obj:`edit_db.task`
            Объект задачи, для которой ищется файл.
            
        version : int, str, optional
            Версия, число или строковое представление, если *False* - то путь до финальной версии, которая сверху версий (в паблиш/активити).
            
        branches : list, optional
             Список веток из которых делался *push* или *publish* (в случае репаблиша) - для *task_type* из списка :attr:`edit_db.studio.multi_publish_task_types` (например *'sketch'*).
             
        look : bool, optional
            Рассматривается только если *task_type* из списка :attr:`edit_db.studio.multi_publish_task_types` (например *'sketch'*), если *False* - то используется *c_task.extension*, если *True* - то используется :attr:`edit_db.studio.look_extension`.
            
        Returns
        -------
        tuple
            * (*True*, path) или (*False*, comment)
            * (*True*, {branch_name : path1, ...}) или (*False*, comment) - для *task_type* из списка :attr:`edit_db.studio.multi_publish_task_types` (например *'sketch'*)
        """
        pass
        # 1 - 
        
        if not version is False and not version is None:
            #
            b, str_version = self._template_version_num(version)
            if not b:
                return (b, str_version)
            #
            if c_task.task_type in self.multi_publish_task_types:
                path_dict = dict()
                for branch in branches:
                    if look:
                        path = os.path.join(c_task.asset.path, self.publish_folder_name, c_task.activity, str_version, '%s#%s%s' % (c_task.asset.name, branch, self.look_extension))
                    else:
                        path = os.path.join(c_task.asset.path, self.publish_folder_name, c_task.activity, str_version, '%s#%s%s' % (c_task.asset.name, branch, c_task.extension))
                    path_dict[branch] = NormPath(path)
                return(True, path_dict)
            else:
                path = os.path.join(c_task.asset.path, self.publish_folder_name, c_task.activity, str_version, '%s%s' % (c_task.asset.name, c_task.extension))
                return (True, NormPath(path))
        else:
            if c_task.task_type in self.multi_publish_task_types:
                path_dict = dict()
                for branch in branches:
                    if look:
                        path = os.path.join(c_task.asset.path, self.publish_folder_name, c_task.activity, '%s#%s%s' % (c_task.asset.name, branch, self.look_extension))
                    else:
                        path = os.path.join(c_task.asset.path, self.publish_folder_name, c_task.activity, '%s#%s%s' % (c_task.asset.name, branch, c_task.extension))
                    path_dict[branch] = NormPath(path)
                return(True, path_dict)
            else:
                return (True, NormPath(os.path.join(c_task.asset.path, self.publish_folder_name, c_task.activity, '%s%s' % (c_task.asset.name, c_task.extension))))
        
    def set_share_dir(self, path):
        """Пока не используется. """
        if not os.path.exists(path):
            return "****** to studio path not Found!"
        
        home = os.path.expanduser('~')	
        init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
        if not os.path.exists(init_path):
            return "****** init_path not Found!"
        
        # write studio path
        try:
            with open(init_path, 'r') as read:
                data = json.load(read)
                data['share_folder'] = path
                read.close()
        except:
            return "****** init file  can not be read"

        try:
            with open(init_path, 'w') as f:
                jsn = json.dump(data, f, sort_keys=True, indent=4)
                f.close()
        except:
            return "****** init file  can not be read"

        #self.out_source_share_folder = path
        
        self.get_studio()
        return True, 'Ok'
        
    def get_share_dir(self):
        """Пока не используется. """
        pass
        # get lineyka_init.json
        home = os.path.expanduser('~')	
        init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
        if not os.path.exists(init_path):
            return False, "****** init_path not Found!"
            
        # write studio path
        
        try:
            with open(init_path, 'r') as read:
                data = json.load(read)
                try:
                    path = data['share_folder']
                    self.share_dir = path
                    return True, path
                except:
                    return False, 'Not key \"share_folder\"'
                read.close()
        except:
            return False, '****** init file not Read!'

    @classmethod
    def get_studio(self):
        """Заполнение атрибутов класса текущей студии. Которая определяется в :func:`edit_db.studio.set_studio`.
        
        Заполняемые атрибуты:
        
        * :attr:`edit_db.studio.studio_folder`
        * :attr:`edit_db.studio.work_folder`
        * :attr:`edit_db.studio.convert_exe`
        * :attr:`edit_db.studio.tmp_folder`
        * :attr:`edit_db.studio.studio_database`
        * :attr:`edit_db.studio.extensions`
        * :attr:`edit_db.studio.soft_data`
        
        Returns
        -------
        tuple
            (*True*, [self.studio_folder, self.tmp_folder]) или (*False*, comment)
        
        """
        
        if self.init_path == False:
            return(False, '****** in get_studio() -> init_path = False!')
        # write studio path
        try:
            with open(self.init_path, 'r') as read:
                data = json.load(read)
                #self.studio_folder = data['studio_folder']
                #self.tmp_folder = data['tmp_folder']
                read.close()
        except:
            return(False, "****** init file  can not be read")
        try:
            self.studio_folder = data['studio_folder']
            self.work_folder = data['work_folder']
            self.convert_exe = data['convert_exe']
            self.tmp_folder = data['tmp_folder']
            self.studio_database = data['use_database']
        except Exception as e:
            print(e)
            
        #print('artist path: ', self.artists_path)
            
        '''
        # get list_active_projects
        if self.list_projects:
            self.list_active_projects = []
            for key in self.list_projects:
                if self.list_projects[key]['status'] == 'active':
                    self.list_active_projects.append(key)
        '''
                
        # fill self.extensions
        try:
            with open(self.set_path, 'r') as read:
                data = json.load(read)
                self.extensions = data['extension'].keys()
                self.soft_data = data['extension']
                read.close()
        except:
            return(False, 'in get_studio -> not read user_setting.json!')
        
        print('studio.get_studio')
        return True, [self.studio_folder, self.tmp_folder]

    # ****** SETTING ******
    # ------- EXTENSION -------------
    def get_extension_dict(self):
        """Получение словаря соответсвия расширения файлов и приложений для них, из файла :attr:`edit_db.studio.set_file`. 
        
        Returns
        -------
        tuple
            (*True*, extension_dict) или (*False*, comment)
        """
        extension_dict = dict()
        
        home = os.path.expanduser('~')
        #folder = os.path.join(home, self.init_folder)
        #set_path = os.path.join(folder, self.set_file)
        set_path = NormPath(os.path.join(home, self.init_folder, self.set_file))
        
        if not os.path.exists(set_path):
            return(False, ('Not Path ' + set_path))
        
        with open(set_path, 'r') as read:
            extension_dict = json.load(read)['extension']
            
        return(True, extension_dict)
        
    def edit_extension_dict(self, key, path):
        """Изменение словаря соответсвия расширения файлов и приложений для них, в файле :attr:`edit_db.studio.set_file` 
        
        Parameters
        ----------
        key : str
            Расширение файла с точкой, например: *'.obj'*
        path : str
            Путь до экзшника приложения или имя приложения (в зависимости от конфигурации), например '~/blender2.8/blender' или 'gimp'.
            
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False*, comment)
        """
        extension_dict = dict()
        
        home = os.path.expanduser('~')
        #folder = os.path.join(home, self.init_folder)
        #set_path = os.path.join(folder, self.set_file)
        set_path = NormPath(os.path.join(home, self.init_folder, self.set_file))
        
        if not os.path.exists(set_path):
            return(False, ('Not Path ' + set_path))
        
        with open(set_path, 'r') as read:
            data = json.load(read)
        
        data['extension'][key] = path
        
        with open(set_path, 'w') as f:
            jsn = json.dump(data, f, sort_keys=True, indent=4)
            f.close()
        
        self.get_studio()
        return(True, 'Ok')
        
    def edit_extension(self, extension, action, new_extension = False):
        """Редактирование расширений (ключей) словаря соответсвия расширения файлов и приложений для них, в файле :attr:`edit_db.studio.set_file`
        
        Parameters
        ----------
        extension : str
            Изменяемое расширение файла (с точкой, например: *'.obj'*)
        action : str
            Совершаемое действие. Действие из списка: *['ADD', 'REMOVE', 'EDIT']*
        new_extension : str, optional
            Добавляемое расширение (с точкой, например: *'.obj'*) взамен существующего (первый параметр), для *action* = *'EDIT'*
            
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False*, comment)
        """
        if not extension:
            return(False, 'Extension not specified!')
            
        if not action in ['ADD', 'REMOVE', 'EDIT']:
            return(False, 'Incorrect Action!')
            
        # get file path
        home = os.path.expanduser('~')
        folder = os.path.join(home, self.init_folder)
        set_path = os.path.join(folder, self.set_file)
        
        if not os.path.exists(set_path):
            return(False, ('Not Path ' + set_path))
        
        # preparation extension
        if extension[0] != '.':
            extension = '.' + extension
            
        # read extensions
        with open(set_path, 'r') as read:
            data = json.load(read)
            
        if action == 'ADD':
            if not extension in data['extension'].keys():
                data['extension'][extension] = ''
            else:
                return(False, ('This Extension \"' + extension + '\" Already Exists!'))
        elif action == 'REMOVE':
            if extension in data['extension'].keys():
                del data['extension'][extension]
            else:
                return(False, ('This Extension \"' + extension + '\" Not Found!'))
        elif action == 'EDIT':
            if new_extension: 
                if extension in data['extension'].keys():
                    value = data['extension'][extension]
                    del data['extension'][extension]
                    data['extension'][new_extension] = value
            else:
                return(False, 'Not New Extension!')
            
        with open(set_path, 'w') as f:
            jsn = json.dump(data, f, sort_keys=True, indent=4)
            f.close()
        
        self.get_studio()
        return(True, 'Ok!')

class database():
    """Взаимодействия с базой данных. """

    def __init__(self):
        self.sqlite3_db_folder_attr = {
            'studio': 'studio_folder',
            'project': 'path',
            }
        
        self.use_db_attr = {
            'studio': 'studio_database',
            'project': 'project_database',
            }

    # level - studio or project; or: studio, project, season, group, asset, task, chat, log, statistic ...
    # read_ob - object of studio or project;
    # table_root - assets, chats - те случаи когда имя файла ДБ не соответствует имени таблицы, если есть table_root - имя файла ДБ будет определяться по нему.
    # table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
    def get(self, level, read_ob, table_name, com, table_root=False):
        """Чтение БД, с использованием *sql* команды.
        
        Parameters
        ----------
        level : str
            Уровень, варианты: ``studio``, ``project`` (данные проекта или студии).
        read_ob : :obj:`edit_db.studio`, :obj:`edit_db.project`
            Объект студии или проекта, для которого идёт взаимодействие с базой данных. 
        table_name : str
            Имя таблицы БД (для проверки наличия).
        com : str
            *SQL* команда.
        table_root : str, optional
            Имя файла БД для ``sqlite3``. Например :attr:`edit_db.studio.tasks_db`. Для тех случаев когда имя файла ДБ не соответствует имени таблицы (лучше передавать всегда).
            
        Returns
        -------
        tuple
            (*True*, [строки-словари]) или (*False*, comment)
        """
        
        # get use_db
        attr = self.use_db_attr.get(level)
        if not attr:
            raise Exception('database.get()', 'Unknown Level : %s' % level)
        
        db_name, db_data = eval('read_ob.%s' % attr)
        #return(db_name, db_data)
        
        if db_name == 'sqlite3':
            return_data = self.__sqlite3_get(level, read_ob, table_name, com, table_root)
            return(return_data)

    # table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
    def set_db(self, level, read_ob, table_name, com, data_com=False, table_root=False):
        """Внесение изменений в БД, с использованием *sql* команды.
        
        Parameters
        ----------
        level : str
            Уровень, варианты: ``studio``, ``project`` (данные проекта или студии).
        read_ob : :obj:`edit_db.studio`, :obj:`edit_db.project`
            Объект студии или проекта, для которого идёт взаимодействие с базой данных. 
        table_name : str
            Имя таблицы БД.
        com : str
            *SQL* команда.
        data_com : tuple, optional
            Кортеж значений для *com*.
        table_root : str, optional
            Имя файла БД для ``sqlite3``. Например :attr:`edit_db.studio.tasks_db`. Для тех случаев когда имя файла ДБ не соответствует имени таблицы (лучше передавать всегда).
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        pass
        # get use_db
        attr = self.use_db_attr.get(level)
        if not attr:
            raise Exception('database.set_db()', 'Unknown Level : %s' % level)
        
        db_name, db_data = eval('read_ob.%s' % attr)
        #return(db_name, db_data)
        
        if db_name == 'sqlite3':
            return_data = self.__sqlite3_set(level, read_ob, table_name, com, data_com, table_root)
            return(return_data)

    # table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
    def create_table(self, level, read_ob, table_name, keys, table_root = False):
        """Создание таблицы БД, при её отсутствии.
        
        Parameters
        ----------
        level : str
            Уровень, варианты: ``studio``, ``project`` (данные проекта или студии).
        read_ob : :obj:`edit_db.studio`, :obj:`edit_db.project`
            Объект студии или проекта, для которого идёт взаимодействие с базой данных. 
        table_name : str
            Имя таблицы БД.
        keys : dict
            Словарь, инициализирующий данную таблицу: ключи - заголовки, значения - типы данных (стандартные для sqlite3 + дополнительные, например ``json``) например :attr:`edit_db.studio.tasks_keys`
        table_root : str, optional
            Имя файла БД для ``sqlite3``. Например :attr:`edit_db.studio.tasks_db`. Для тех случаев когда имя файла ДБ не соответствует имени таблицы (лучше передавать всегда).
        
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        attr = self.use_db_attr.get(level)
        if not attr:
            raise Exception('database.write()', 'Unknown Level : %s' % level)
        
        db_name, db_data = eval('read_ob.%s' % attr)
        #return(db_name, db_data)
        
        if db_name == 'sqlite3':
            return_data = self.__sqlite3_create_table(level, read_ob, table_name, keys, table_root)
            return(return_data)
        
    # write_data - словарь по ключам keys, также может быть списком словарей, для записи нескольких строк.
    # keys - это: tasks_keys, projects_keys итд.
    # table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
    def insert(self, level, read_ob, table_name, keys, write_data, table_root=False):
        """Добавление строки или нескольких строк в таблицу БД.
        
        Parameters
        ----------
        level : str
            Уровень, варианты: ``studio``, ``project`` (данные проекта или студии).
        read_ob : :obj:`edit_db.studio`, :obj:`edit_db.project`
            Объект студии или проекта, для которого идёт взаимодействие с базой данных. 
        table_name : str
            Имя таблицы БД.
        keys : dict
            Словарь, инициализирующий данную таблицу: ключи - заголовки, значения - типы данных (стандартные для sqlite3 + дополнительные, например ``json``) например :attr:`edit_db.studio.tasks_keys`
        write_data : dict, list
            Словарь строки по ключам ``keys``, также может быть списком словарей, для записи нескольких строк.
        table_root : str, optional
            Имя файла БД для ``sqlite3``. Например :attr:`edit_db.studio.tasks_db`. Для тех случаев когда имя файла ДБ не соответствует имени таблицы (лучше передавать всегда).
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        attr = self.use_db_attr.get(level)
        if not attr:
            raise Exception('database.insert()', 'Unknown Level : %s' % level)
        
        db_name, db_data = eval('read_ob.%s' % attr)
        #return(db_name, db_data)
        
        if db_name == 'sqlite3':
            # create table
            bool_, r_data = self.__sqlite3_create_table(level, read_ob, table_name, keys, table_root)
            if not bool_:
                return(bool_, r_data)
            # write
            return_data = self.__sqlite3_insert(level, read_ob, table_name, keys, write_data, table_root)
            return(return_data)

    # where - 1) строка условия, 2) словарь по keys, 3) False - значит выделяется всё.
    # columns - False - означает все столбцы если не False - то список столбцов.
    def read(self, level, read_ob, table_name, keys, columns = False, where=False, table_root=False):
        """Чтение БД, используя условие.
        
        Parameters
        ----------
        level : str
            Уровень, варианты: ``studio``, ``project`` (данные проекта или студии).
        read_ob : :obj:`edit_db.studio`, :obj:`edit_db.project`
            Объект студии или проекта, для которого идёт взаимодействие с базой данных. 
        table_name : str
            Имя таблицы БД.
        keys : dict
            Словарь, инициализирующий данную таблицу: ключи - заголовки, значения - типы данных (стандартные для sqlite3 + дополнительные, например ``json``) например :attr:`edit_db.studio.tasks_keys`
        columns : list, optional
            Список читаемых столбцов, если не передавать - то читаются все столбцы.
        where : str, dict
            * Строка условия для *sql* оператора ``WHERE``.
            * Словарь для формирования строки *sql* оператора ``WHERE``, содержит ключи по ``keys``, плюс может содержать ``condition`` значения из [``or``, ``end``].
        table_root : str, optional
            Имя файла БД для ``sqlite3``. Например :attr:`edit_db.studio.tasks_db`. Для тех случаев когда имя файла ДБ не соответствует имени таблицы (лучше передавать всегда).
        
        Returns
        -------
        tuple
            (*True*, [строки-словари]) или (*False*, comment)
        """
        attr = self.use_db_attr.get(level)
        if not attr:
            raise Exception('database.read()', 'Unknown Level : %s' % level)
        
        db_name, db_data = eval('read_ob.%s' % attr)
        #return(db_name, db_data)
        
        if db_name == 'sqlite3':
            b, r = self.__sqlite3_read(level, read_ob, table_name, keys, columns, where, table_root)
            return(b, r)

    # update_data - словарь по ключам из keys
    # where - словарь по ключам, так как значения маскируются под "?" не может быть None или False
    # table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
    def update(self, level, read_ob, table_name, keys, update_data, where, table_root=False):
        """Редактирование строк в таблице БД.
        
        Parameters
        ----------
        level : str
            Уровень, варианты: ``studio``, ``project`` (данные проекта или студии).
        read_ob : :obj:`edit_db.studio`, :obj:`edit_db.project`
            Объект студии или проекта, для которого идёт взаимодействие с базой данных. 
        table_name : str
            Имя таблицы БД.
        keys : dict
            Словарь, инициализирующий данную таблицу: ключи - заголовки, значения - типы данных (стандартные для sqlite3 + дополнительные, например ``json``) например :attr:`edit_db.studio.tasks_keys`
        update_data : dict
            Данные на замену, словарь по ключам из ```keys``.
        where : dict
            Словарь для формирования строки *sql* оператора ``WHERE``, содержит ключи по ``keys``.
        table_root : str, optional
            Имя файла БД для ``sqlite3``. Например :attr:`edit_db.studio.tasks_db`. Для тех случаев когда имя файла ДБ не соответствует имени таблицы (лучше передавать всегда).
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        attr = self.use_db_attr.get(level)
        if not attr:
            raise Exception('database.update()', 'Unknown Level : %s' % level)
        
        db_name, db_data = eval('read_ob.%s' % attr)
        #return(db_name, db_data)
        
        if db_name == 'sqlite3':
            return_data = self.__sqlite3_update(level, read_ob, table_name, keys, update_data, where, table_root)
            return(return_data)
        
    # удаление строки из таблицы БД
    # where - словарь по ключам, так как значения маскируются под "?" не может быть None или False
    # table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
    def delete(self, level, read_ob, table_name, where, table_root=False):
        """Удаление строки из таблицы БД.
        
        Parameters
        ----------
        level : str
            Уровень, варианты: ``studio``, ``project`` (данные проекта или студии).
        read_ob : :obj:`edit_db.studio`, :obj:`edit_db.project`
            Объект студии или проекта, для которого идёт взаимодействие с базой данных. 
        table_name : str
            Имя таблицы БД.
        where : dict
            Словарь для формирования строки *sql* оператора ``WHERE``, содержит ключи по ``keys``.
        table_root : str, optional
            Имя файла БД для ``sqlite3``. Например :attr:`edit_db.studio.tasks_db`. Для тех случаев когда имя файла ДБ не соответствует имени таблицы (лучше передавать всегда).
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        attr = self.use_db_attr.get(level)
        if not attr:
            raise Exception('database.update()', 'Unknown Level : %s' % level)
        
        db_name, db_data = eval('read_ob.%s' % attr)
        #return(db_name, db_data)
        
        if db_name == 'sqlite3':
            return_data = self.__sqlite3_delete(level, read_ob, table_name, where, table_root)
            return(return_data)

    ### SQLITE3
    # table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
    #@print_args
    def __get_db_path(self, level, read_ob, table_name, table_root):
        attr = self.sqlite3_db_folder_attr.get(level)
        db_folder = getattr(read_ob, attr)
        if not db_folder:
            return(None)
        if table_root:
            if table_root.endswith('.db'):
                db_path = os.path.join(db_folder, table_root)
            else:
                db_path = os.path.join(db_folder, '.%s.db' % table_root)
        else:
            db_path = os.path.join(db_folder, '.%s.db' % table_name)
        return(db_path)

    # update_data - словарь по ключам из keys
    # where - словарь по ключам, так как значения маскируются под "?" не может быть None или False
    def __sqlite3_update(self, level, read_ob, table_name, keys, update_data, where, table_root):
        data_com = []
        # set_data
        set_data = ''
        if update_data.__class__.__name__ != 'dict':
            return(False, 'update_data not dict!')
        else:
            for i, key in enumerate(update_data):
                if i==0:
                    set_data = '"%s" = ?' % key
                else:
                    set_data = set_data + ', "%s" = ?' % key
                if keys[key]=='json':
                    data_com.append(json.dumps(update_data[key]))
                else:
                    data_com.append(update_data[key])
        # where
        where_data = ''
        if where.__class__.__name__ != 'dict':
            return(False, 'where not dict!')
        else:
            for i, key in enumerate(where):
                if i==0:
                    where_data = '%s = ?' % key
                else:
                    where_data = where_data + 'AND %s = ?' % key
                data_com.append(where[key])
        # com
        com = 'UPDATE %s SET %s WHERE %s' % (table_name, set_data, where_data)
        
        # connect
        # -- db_path
        db_path = self.__get_db_path(level, read_ob, table_name, table_root)
        if not db_path:
            return(False, 'No path to database!')
        # -- connect
        conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # -- com
        try:
            c.execute(com, data_com)
        except Exception as e:
            print('#'*3, 'Exception in database.__sqlite3_update:')
            print('#'*3, 'com:', com)
            print('#'*3, 'data_com:', data_com)
            print('#'*3, e)
            conn.close()
            return(False, 'Exception in database.__sqlite3_update, please look the terminal!')
        conn.commit()
        conn.close()
        return(True, 'Ok!')

    # where - словарь по ключам, так как значения маскируются под "?" не может быть None или False
    def __sqlite3_delete(self, level, read_ob, table_name, where, table_root):
        data_com = []
        
        # where
        where_data = ''
        if where.__class__.__name__ != 'dict':
            return(False, 'where not dict!')
        else:
            for i, key in enumerate(where):
                if i==0:
                    where_data = '%s = ?' % key
                else:
                    where_data = where_data + ', %s = ?' % key
                data_com.append(where[key])
        # com
        com = 'DELETE FROM %s WHERE %s' % (table_name, where_data)
        
        # connect
        # -- db_path
        db_path = self.__get_db_path(level, read_ob, table_name, table_root)
        if not db_path:
            return(False, 'No path to database!')
        # -- connect
        conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # -- com
        try:
            c.execute(com, data_com)
        except Exception as e:
            print('#'*3, 'Exception in database.__sqlite3_delete:')
            print('#'*3, 'com:', com)
            print('#'*3, 'data_com:', data_com)
            print('#'*3, e)
            conn.close()
            return(False, 'Exception in database.__sqlite3_delete, please look the terminal!')
        conn.commit()
        conn.close()
        return(True, 'Ok!')

    # where - 1) строка условия, 2) словарь по keys, может иметь ключ условия - 'condition' значения из [or, end] 3) False - значит выделяется всё.
    # columns - False - означает все столбцы если не False - то список столбцов.
    #@print_args
    def __sqlite3_read(self, level, read_ob, table_name, keys, columns, where, table_root):
        # columns
        col = ''
        if not columns:
            col = '*'
        elif columns.__class__.__name__ == 'list':
            for i, item in enumerate(columns):
                if i == 0:
                    col = col + item
                else:
                    col = col + ', %s' % item
        # com
        com = 'SELECT %s FROM %s ' % (col, table_name)
        if where:
            if where.__class__.__name__ == 'string':
                com = '%s WHERE %s' % (com, where)
            elif where.__class__.__name__ == 'dict':
                were_string = ''
                i=0
                if not where.get('condition'):
                    for key in where:
                        if i == 0:
                            were_string = were_string + '"%s" = "%s"' % (key, where.get(key))
                        else:
                            were_string = were_string + 'AND "%s" = "%s"' % (key, where.get(key))
                        i=i+1
                else:
                    var = where['condition'].upper()
                    for key in where:
                        if key == 'condition':
                            continue
                        for item in where[key]:
                            if i == 0:
                                were_string = were_string + '"%s" = "%s"' % (key, item)
                            else:
                                were_string = were_string + '%s "%s" = "%s"' % (var, key, item)
                            i=i+1
                        break
                com = '%s WHERE %s' % (com, were_string)
        # connect
        # -- db_path
        db_path = self.__get_db_path(level, read_ob, table_name, table_root)
        # -- connect
        try:
            conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
        except Exception as e:
            print('#'*3, 'Exception in database.__sqlite3_read:')
            print('#'*3, 'db_path:', db_path)
            print('#'*3, e)
            return(False, 'Exception in database.__sqlite3_read, please look the terminal!')
        
        # -- exists table_name
        res = c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = []
        for item in res:
            #print(item[0], item[0].__class__.__name__)
            #print(table_name, table_name.__class__.__name__)
            #print(item[0] == table_name)
            tables.append(item[0])
        if not table_name.replace('"', '') in tables:
            conn.close()
            #print('not %s in %s' % (table_name, str(tables)))
            return(True, list())
        
        # -- execute
        try:
            c.execute(com)
        except Exception as e:
            conn.close()
            print('#'*3, 'Exception in database.__sqlite3_read:')
            print('#'*3, 'com:', com)
            print('#'*3, e)
            return(False, 'Exception in database.__sqlite3_read, please look the terminal!')
        
        data = []
        for row in c.fetchall():
            '''
            dict_row = dict(row)
            '''
            dict_row = {}
            for key in row.keys():
                if keys[key]=='json':
                    #print('#'*10, key)
                    #print('*'*10, row[key])
                    try:
                        dict_row[key] = json.loads(row[key])
                    except Exception as e:
                        print('%s Exception in database.__sqlite3_read:' % '#'*10)
                        print('%s table = %s, key = %s, row[key] = %s' % ('#'*10, table_name, key, row[key]))
                        print('#'*10, e)
                        dict_row[key] = None
                else:
                    dict_row[key] = row[key]
            
            data.append(dict_row)
        conn.close()
        return(True, data)

    def __sqlite3_create_table(self, level, read_ob, table_name, keys, table_root):
        com = ''
        #data_com = []
        for i, key in enumerate(keys):
            if keys[key] == 'json':
                type_data = 'text'
            else:
                type_data = keys[key]
            if i==0:
                com = com + '"%s" "%s"' % (key, type_data)
            else:
                com = com + ', "%s" "%s"' % (key, type_data)
        com = 'CREATE TABLE IF NOT EXISTS %s (%s)' % (table_name, com)
        return_data = self.__sqlite3_set(level, read_ob, table_name, com, False, table_root)
        return(return_data)

    # write_data - словарь по ключам keys, также может быть списком словарей, для записи нескольких строк.
    # keys - это: tasks_keys, projects_keys итд.
    def __sqlite3_insert(self, level, read_ob, table_name, keys, write_data, table_root):
        if write_data.__class__.__name__ == 'dict':
            iterator = [write_data]
        elif write_data.__class__.__name__ == 'list':
            iterator = write_data
        # connect
        # -- db_path
        db_path = self.__get_db_path(level, read_ob, table_name, table_root)
        #if not db_path:
            #return(False, 'No path to database!')
        # -- connect
        conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # -- com
        for item in iterator:
            com = 'INSERT INTO %s VALUES' % table_name
            com_=''
            data_com = []
            for i, key in enumerate(keys):
                if i==0:
                    com_ = com_ + ' ?'
                else:
                    com_ = com_ + ', ?'
                if keys[key] == 'json':
                    data_ = json.dumps(item.get(key))
                else:
                    data_ = item.get(key)
                data_com.append(data_)
            com = '%s (%s)' % (com, com_)
            try:
                c.execute(com, data_com)
            except Exception as e:
                print('#'*3, 'Exception in database.__sqlite3_insert:')
                print('#'*3, 'com:', com)
                print('#'*3, 'data_com:', data_com)
                print('#'*3, e)
                conn.close()
                return(False, 'Exception in database.__sqlite3_insert, please look the terminal!')
        conn.commit()
        conn.close()
        return(True, 'Ok!')
            
    def __sqlite3_get(self, level, read_ob, table_name, com, table_root):
        #db_path
        db_path = self.__get_db_path(level, read_ob, table_name, table_root)
        if not db_path:
            return(True, list())
        #print('__sqlite3_get()', db_path, os.path.exists(db_path))
        
        try:
            # -- CONNECT  .db
            conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            # -- exists table_name
            res = c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = list()
            for item in res:
                tables.append(item[0])
            if not table_name.replace('"', '') in tables:
                conn.close()
                return(True, list())
            
            # -- execute
            c.execute(com)
            data = []
            for row in c.fetchall():
                data.append(dict(row))
            #print('*'*10, data)
        except Exception as e:
            try:
                conn.close()
            except:
                pass
            print('__sqlite3_get()', e)
            return(False, e)
        
        conn.close()
        return(True, data)

    # if com = False - создаётся пустая таблица ,при отсутствии
    def __sqlite3_set(self, level, read_ob, table_name, com, data_com, table_root):
        #db_path
        db_path = self.__get_db_path(level, read_ob, table_name, table_root)
        #if not db_path:
            #return(False, 'No path to database!')
        #print('__sqlite3_get()', db_path, os.path.exists(db_path))
        
        try:
            # -- CONNECT  .db
            conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            if data_com:
                c.execute(com, data_com)
            elif com:
                c.execute(com)
            else:
                pass
        except Exception as e:
            try:
                conn.close()
            except:
                pass
            print('#'*3, 'Exception in __sqlite3_set()', e)
            print('#'*3, 'com:', com)
            print('#'*3, 'data_com:', data_com)
            return(False, 'Exception in __sqlite3_set(), please read the terminal!')
        
        conn.commit()
        conn.close()
        return(True, 'Ok!')

class project(studio):
    """
    **level** = 'studio'

    .. rubric:: Данные хранимые в БД (имя столбца : тип данных) :attr:`edit_db.studio.projects_keys`:

    .. code-block:: python

        projects_keys = {
        'name': 'text',
        'path': 'text',
        'status': 'text',
        'project_database': 'json',
        'chat_img_path': 'text',
        'list_of_assets_path': 'text',
        'preview_img_path': 'text',
        'fps': 'real',
        'units': 'text',
        }

    Examples
    --------
    Создание экземпляра класса:

    .. code-block:: python

        import edit_db as db
        
        project = db.project()
    
        
    Attributes
    ----------
    name : str
        Имя проекта (уникально)    
    
    path : str
        Путь до директории проекта.
    
    status : str
        Теущий статус проекта, значение из списка :attr:`edit_db.studio.PROJECTS_STATUSES`.
    
    project_database : list
        Параметры используемой базы данных, по умолчанию: ``['sqlite3', False]``.
    
    chat_img_path : str
        Путь до директории с картинками чата.
    
    list_of_assets_path : str
        Путь до файла с временными данными создаваемых ассетов.
    
    preview_img_path : str
        Путь до директории с превью картинок чата.
    
    fps : float
        *fps* проекта (по умолчанию 24).
    
    units : str
        Юниты 3d сцен, значение из списка: :attr:`edit_db.studio.projects_units` по умолчанию ``'m'``.
    
    list_active_projects : list
        ``атрибут класса`` Список активных проектов, только имена. Заполняется при выполнении метода :func:`edit_db.project.get_list`, значение по умолчанию - ``[]``.
    
    list_projects : list
        ``атрибут класса`` Список всех проектов (экземпляры). Заполняется при выполнении метода :func:`edit_db.project.get_list`, значение по умолчанию - ``[]``.
        
    dict_projects : dict
        ``атрибут класса`` Cловарь содержащий все проекты (экземпляры) с ключами по именам. Заполняется при выполнении метода :func:`edit_db.project.get_list`, значение по умолчанию - ``{}``.
        
    folders : dict
        ``атрибут класса`` Служебные директории папки проекта.
    
    """

    list_active_projects = []
    
    list_projects = []
    
    dict_projects = {}
    
    folders = {
        'assets':'assets',
        'chat_img_folder':'.chat_images',
        'preview_images': '.preview_images'
        }

    def __init__(self):
        pass
        #base fields
        for key in self.projects_keys:
            exec('self.%s = False' % key)

    def init(self, name, new=True): # v2
        """Инициализация по имени, возвращает новый, или инициализирует текущий экземпляр.
        
        Parameters
        ----------
        name : str
            имя проекта.
        new : bool
            если *True* - возвращает новый инициализированный экземпляр, если *False* то инициализирует текущий экземпляр
            
        Returns
        -------
        :obj:`edit_db.project`, tuple
            * если new= *True* - экземпляр класса :obj:`edit_db.project`,
            * если new= *False* - (*True,  'Ok!'*) или (*False, comment*)
        """
        pass
        b, r = database().read('studio', self, self.projects_t, self.projects_keys, table_root=self.projects_db)
        if not b:
            return(b, r)
        
        for data in r:
            if data['name'] == name:
                return(self.init_by_keys(data, new=new))
        if new:
            return(None)
        else:
            return(False, 'Project with the same name "%s" does not exist!' % name)

    def init_by_keys(self, keys, new=True): # v2
        """Инициализация по словарю (без чтения БД), возвращает новый, или инициализирует текущий экземпляр.
        
        Parameters
        ----------
        keys : dict
            словарь по :attr:`edit_db.studio.projects_keys`
        new : bool, optional
            если *True* - возвращает новый инициализированный экземпляр, если *False* то инициализирует текущий.
        
        Returns
        -------
        :obj:`edit_db.project`, tuple
            * если new= *True* - экземпляр класса :obj:`edit_db.project`,
            * если new= *False* - (*True,  'Ok!'*) или (*False, comment*)
        """
        
        if new:
            r_ob = project()
        else:
            r_ob = self
        
        for key in self.projects_keys:
            setattr(r_ob, key, keys[key])
            
        if new:
            return r_ob
        else:
            return(True, 'Ok!')

    def add_project(self, name, path): # v2
        """Создаёт проект согласно :ref:`make-project-page`
        
        .. note:: При создании проекта новый экземпляр не возвращается, заполняются поля текущего экземпляра.
  
        Parameters
        ----------
        name : str
            имя проекта, если имя не указано, но указана директория, проект будет назван именем директории
        path : str
            путь к директории проекта, если путь не указан, директория проекта будет создана в директории студии
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        
        project_path = NormPath(path)
        # test by name
        self.get_list()
        if name in self.dict_projects.keys():
            return(False, "This project name already exists!")
        
        # project_name, get project_path
        if not project_path and not name:
            return(False, 'No options!')
            
        elif not project_path:
            project_path = os.path.join(self.studio_folder, name)
            #self.path=project_path
            try:
                os.mkdir(project_path)
            except:
                return(False, ('Failed to create folder: %s' % project_path))
        elif name == '':
            if not os.path.exists(project_path):
                return(False, ('Project Path: \"%s\" Not Found!' % project_path))
            name = os.path.basename(project_path)
        
        if not os.path.exists(project_path):
            text = '****** studio.project.add_project() -> %s not found' % project_path
            return False, text
        else:
            self.name = name
            self.path = project_path
        
        # read data
        data = self._read_settings()
        #print(data)
        if not data:
            self.project_database = ['sqlite3', False] # новый проект в начале всегда sqlite3, чтобы сработало всё в database
            self.fps = 24
            self.units = 'm'
        else:
            self.project_database = data['project_database']
            self.fps = data['fps']
            self.units = data['units']
            self.name = data['name']
            
        #print(self.name, self.path, self.fps)
        #return
        
        #
        self.list_of_assets_path = NormPath(os.path.join(self.path, self.list_of_assets_name))
        # create folders
        self.__make_folders(self.path)
        # -- get chat_img_folder
        img_folder_path = os.path.join(self.path, self.folders['chat_img_folder'])
        if os.path.exists(img_folder_path):
            self.chat_img_path = img_folder_path
        else:
            self.chat_img_path = False
        # -- get preview_images
        preview_img_path = os.path.join(self.path, self.folders['preview_images'])	
        if os.path.exists(preview_img_path):
            self.preview_img_path = preview_img_path
        else:
            self.chat_img_path = False
        
        # status
        self.status = 'active'
        
        # create project
        # -- write data
        write_data = {}
        for key in self.projects_keys:
            write_data[key] = eval('self.%s' % key)
        #print('#'*3, write_data)
        bool_, return_data = database().insert('studio', self, self.projects_t, self.projects_keys, write_data)
        if not bool_:
            return(bool_, return_data)
        
        # create_recycle_bin
        
        result = group(self).create_recycle_bin()
        if not result[0]:
            return(False, result[1])
        #
        self._write_settings()
        return True, 'ok'

    def get_list(self): # v2
        """Заполняет атрибуты класса:
        
        * :attr:`edit_db.project.list_active_projects`
        * :attr:`edit_db.project.list_projects`
        * :attr:`edit_db.project.dict_projects`
        
        Returns
        -------
        tuple
            (*True*, :attr:`edit_db.project.list_projects`) или (*False, comment*)
        """
        
        pass
        b, r = database().read('studio', self, self.projects_t, self.projects_keys)
        if not b:
            return(b,r)
        
        list_active_projects = [] # имена активных проектов
        list_projects = [] # все проекты (объекты)
        dict_projects = {} # все проекты (объекты) по именам.
        
        for item in r:
            ob = self.init_by_keys(item)
            list_projects.append(ob)
            dict_projects[ob.name] = ob
            if ob.status == 'active':
                list_active_projects.append(ob.name)
        
        self.__fill_class_fields(list_active_projects, list_projects, dict_projects)
        return(True, list_projects)

    @classmethod
    def __fill_class_fields(self, list_active_projects, list_projects, dict_projects):
        self.list_active_projects = list_active_projects
        self.list_projects = list_projects
        self.dict_projects = dict_projects

    def rename_project(self, new_name): # v2
        """
        * переименование проекта (данного экземпляра),
        * заполняются поля экземпляра,
        * перезаписывается :attr:`edit_db.studio.PROJECT_SETTING`
        
        Parameters
        ----------
        new_name : str
            новое имя отдела.
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или  (*False, comment*)
        
        """
        pass
        if not new_name:
            return(False, 'Not Name!')
        ud = {'name': new_name}
        wh = {'name': self.name}
        bool_, rdata = database().update('studio', self, self.projects_t, self.projects_keys, update_data=ud, where=wh, table_root=self.projects_db)
        if not bool_:
            return(bool_, rdata)
        
        self.name = new_name
        #
        self._write_settings()
        return(True, 'Ok!')

    def remove_project(self): # v2
        """
        * удаляет проект из БД (не удаляя файловую структуру),
        * приводит экземпляр к сосотоянию *empty* (все поля по :attr:`edit_db.studio.projects_keys` = *False*).
  
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        
        """
        pass
        # edit DB
        wh = {'name': self.name}
        bool_, return_data = database().delete('studio', self, self.projects_t, where=wh, table_root=self.projects_db)
        
        # to empty
        for key in self.projects_keys:
            setattr(self, key, False)
        #
        return(True, 'Ok!')

    def edit_status(self, status): # v2
        """
        Изменение статуса проекта.
        
        Parameters
        ----------
        status : str
            присваиваемый статус, должен быть из списка :attr:`edit_db.studio.PROJECTS_STATUSES`
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        
        pass
        if not status in self.PROJECTS_STATUSES:
            return(False, 'Wrong status - "%s", must be from the list - %s' % (status, str(self.PROJECTS_STATUSES)))
        # database
        ud = {'status': status}
        wh = {'name': self.name}
        bool_, return_data = database().update('studio', self, self.projects_t, self.projects_keys, update_data=ud, where=wh, table_root=self.projects_db)
        if not bool_:
            return(bool_, return_data)
        
        self.status = status
        #
        self._write_settings()
        return(True, 'Ok')

    def change_fps(self, fps):
        """
        * Изменение *fps* проекта, предполагается автоматическое назначение этого параметра в сценах.
        * Перезаписывается :attr:`edit_db.studio.PROJECT_SETTING`
        
        Parameters
        ----------
        fps :float
            fps
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        
        pass
        try:
            fps = float(fps)
        except:
            return(False, 'invalid value for FPS: "%s"' % str(fps))
        
        # database
        ud = {'fps': fps}
        wh = {'name': self.name}
        bool_, return_data = database().update('studio', self, self.projects_t, self.projects_keys, update_data=ud, where=wh, table_root=self.projects_db)
        if not bool_:
            return(bool_, return_data)
        
        self.fps = fps
        #
        self._write_settings()
        return(True, 'Ok')

    def change_units(self, units):
        """
        * Изменение юнитов проекта, параметр для 3d сцен (предполагается автоматическое назначение этого параметра в сценах).
        * Перезаписывается :attr:`edit_db.studio.PROJECT_SETTING`
  
        Parameters
        ----------
        units : str
            юниты для 3d сцен, значение из :attr:`edit_db.studio.projects_units`
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        
        if not units in self.projects_units:
            return(False, 'invalid value for Units: "%s"' % str(units))
        pass

        # database
        ud = {'units': units}
        wh = {'name': self.name}
        bool_, return_data = database().update('studio', self, self.projects_t, self.projects_keys, update_data=ud, where=wh, table_root=self.projects_db)
        if not bool_:
            return(bool_, return_data)

        self.units = units
        #
        self._write_settings()
        return(True, 'Ok')
        
    def __make_folders(self, root): # v2
        for f in self.folders:
            path = os.path.join(root, self.folders[f])
            if not os.path.exists(path):
                os.mkdir(path)
                #print '\n****** Created'
            else:
                return False, '\n****** studio.project.make_folders -> No Created'

    def _write_settings(self):
        pass
        # 1 - get data
        # 2 - write data

        ignoring_keys = ['path', 'list_active_projects', 'list_projects', 'dict_projects']

        # (1)
        data = {}
        for key in self.projects_keys:
            if key in ignoring_keys:
                continue
            data[key] = getattr(self, key)
        
        # (2)
        path = NormPath(os.path.join(self.path, self.PROJECT_SETTING))
        with open(path, 'w') as f:
            jsn = json.dump(data, f, sort_keys=True, indent=4)
            
        return(True, 'Ok')

    def _read_settings(self):
        pass

        #
        path = NormPath(os.path.join(self.path, self.PROJECT_SETTING))
        if not os.path.exists(path):
            return(None)
        #
        with open(path, 'r') as f:
            data = json.load(f)
            
        return data

class asset(studio):
    '''
    **level** = 'project'
    
    .. rubric:: Данные хранимые в БД (имя столбца : тип данных) :attr:`edit_db.studio.asset_keys`:

    .. code-block:: python

        asset_keys = {
        'name': 'text',
        'group': 'text',
        'type': 'text',
        'loading_type': 'text', # способ загрузки ассета object в анимационную сцену, значения из studio.loading_types
        'season': 'text',
        'priority': 'integer',
        'description': 'text',
        'content': 'text',
        'id': 'text',
        'status': 'text',
        'parent': 'json' # {'name':asset_name, 'id': asset_id} - возможно не нужно
        }
    
    Examples
    --------
    Создание экземпляра класса:

    .. code-block:: python

        import edit_db as db
        
        project = db.project()
        asset = db.asset(project) # экземпляр project - обязательный параметр при создании экземпляра asset
        # доступ ко всем параметрам и методам принимаемого экземпляра project через asset.project
    
    Attributes
    ----------
    name : str
        Имя ассета (уникально)
    group : str
        *id* группы
    type : str
        Тип ассета из :attr:`edit_db.studio.asset_types`
    loading_type : str
        Тип загрузки в анимационную сцену, варианты: **mesh** - загрузка меша из активити ``model``, **group** - загрузка группы из активити ``model``, **rig** - загрузка группы рига из активити ``rig``.
    season : str
        *id* сезона ``?`` (возможно устарело)
    priority : int
        [0 - inf]
    description : str
        Описание
    content : str
        ``?``
    id : str
        *uuid*
    status : str
        Варианты из [``active``, ``none``]
    parent : dict
        ``?``
    project : :obj:`edit_db.project`
        Экземпляр класса :class:`edit_db.project` принимаемый при создании экземпляра класса, содержит все атрибуты и методы :obj:`edit_db.project`.
    path : str
        Путь к директории ассета на сервере ``?`` (заполняется при инициализации экземпляра).

    '''
    
    # CONSTANTS
    ACTIVITY_FOLDER = {
    'film':{
        'storyboard':'storyboard',
        'specification':'specification',
        'animatic':'animatic',
        'film':'film'
    },
    'object':{
        'sketch':'sketch',
        'face_blend':'10_face_blend',
        'sculpt':'sculpt',
        'model':'03_model',
        'rig':'08_rig',
        #'rig_face':'09_rig_face',
        #'rig_face_crowd':'09_rig_face_crowd',
        #'rig_hik':'08_rig_hik',
        #'rig_hik_face':'09_ri_hik_face',
        #'rig_low':'08_rig_low',
        'def_rig':'def_rig',
        'din_rig':'din_rig',
        'textures':'05_textures',
        'cache':'cache',
        'test_animation': 'test_animation', # тестовая анимация для проверки рига
    },
    'location' : {
        'sketch':'sketch',
        'specification':'specification',
        'location_anim':'location_anim',
        'location':'location'
    },
    'shot_animation' : {
        'animatic':'animatic',
        'shot_animation':'shot_animation',
        'camera':'camera',
        'pleyblast_sequence':'pleyblast_sequence',
        'tech_anim': 'tech_anim',
        'simulation_din':'simulation_din',
        'render':'render',
        'composition':'composition',
        'cache':'cache',
        'actions':'actions',
        #'din_simulation':'din_simulation',
        #'fluid_simulation':'fluid_simulation',
    },
    'camera' : {'camera':'camera'},
    'shot_render' : {'shot_render':'shot_render'},
    'shot_composition' : {'shot_composition':'shot_composition'},
    'light' : {'light':'light'},
    }
    """dict : Наброр активити в ассетах (по типам ассетов). 
    
    .. rubric:: Структура словаря:
    
    .. code-block:: python
        
        { asset_type_name: {
            activiti_folder_name : description,
            },
        ...
        }
    
    """
    
    ADDITIONAL_FOLDERS = {
    'meta_data':'00_common',
    }
    """dict : Общие активити для всех типов ассетов. 
    
    .. rubric:: Структура словаря:
    
    .. code-block:: python
        
        { activiti_folder_name : description,
        ...
        }
    """
    
    UNCHANGEABLE_KEYS = ['id', 'type', 'path']
    """list : Заголовки неизменяемых данных ассетов. """
    
    COPIED_ASSET = {
        'object':['object'],
        }
    """dict : Типы ассетов, которые подлежат копированию.
    
    .. rubric:: Структура словаря:
    
    .. code-block:: python
        
        { asset_type_name : [список типов ассетов, в которые может быть скопирован данный],
        ...
        }
    """
    
    COPIED_WITH_TASK = ['object']
    """list : Список типов ассетов, которые копируются с задачами ``?`` """

    def __init__(self, project_ob):
        if not isinstance(project_ob, project):
            raise Exception('in asset.__init__() - Object is not the right type "%s", must be "project"' % project_ob.__class__.__name__)
        # objects
        self.project = project_ob
        
        self.task_list = False # task lists from this asset
        self.activity_path = False # директория какого либо активити по запросу, заполняется в get_activity_path()
        
        #base fields
        for key in self.asset_keys:
            exec('self.%s = False' % key)

    def init(self, asset_name, new = True):
        """Инициализация по имени, возвращает новый, или инициализирует текущий экземпляр.
        
        Parameters
        ----------
        asset_name : str
            Имя ассета.
        new : bool
            Если *True* - возвращает новый инициализированный экземпляр, если *False* то инициализирует текущий экземпляр.
            
        Returns
        -------
        :obj:`edit_db.asset`, tuple
            * если new= *True* - экземпляр класса :obj:`edit_db.asset`,
            * если new= *False* - (*True,  'Ok!'*) или (*False, comment*)
        """
        pass
        # 1 - чтение БД
        where = {'name': asset_name}
        asset_data = False
        for asset_type in self.asset_types:
            b, r = database().read('project', self.project, asset_type, self.asset_keys, where=where, table_root=self.assets_db)
            if not b:
                print(r)
                continue
            if r:
                asset_data = r[0]
        
        if not asset_data:
            return(False, 'An asset with that name(%s) was not found!' % asset_name)
                
        return(self.init_by_keys(asset_data, new=new))
        
    def init_by_keys(self, keys, new = True):
        """Инициализация по словарю (без чтения БД), возвращает новый, или инициализирует текущий экземпляр.
        
        Parameters
        ----------
        keys : dict
            словарь по :attr:`edit_db.studio.asset_keys`
        new : bool, optional
            если *True* - возвращает новый инициализированный экземпляр, если *False* то инициализирует текущий.
        
        Returns
        -------
        :obj:`edit_db.asset`, tuple
            * если new= *True* - экземпляр класса :obj:`edit_db.asset`,
            * если new= *False* - (*True,  'Ok!'*) или (*False, comment*)
        """
        pass
        if new:
            r_ob = asset(self.project)
        else:
            r_ob = self
            
        for key in self.asset_keys:
            setattr(r_ob, key, keys.get(key))
            r_ob.path = NormPath(os.path.join(self.project.path, self.project.folders['assets'],keys['type'], keys['name']))
            
        if new:
            return r_ob
        else:
            return(True, 'Ok!')
        
    def create(self, asset_type, list_keys):  # v2
        """Создание ассетов по списку.
        
        Parameters
        ----------
        asset_type : str
            Тип создаваемых ассетов, значение из списка :attr:`edit_db.studio.asset_types`
        list_keys : list
            Список словарей по ключам :attr:`edit_db.studio.asset_keys`, обязательные значения: ``name``, ``group`` (*id*). Важный параметр - ``set_of_tasks`` - имя набора задач, без этого параметра будут созданы только основные сервисные задачи ассетов.
        
        Returns
        -------
        tuple
            (*True*, {*make_assets* - словарь объектов с ключами по именам}) или (*False*, comment)
        """
        pass
        # 1 - проверка типа ассета
        # 2 - проверка типа list_keys
        # 3 - список ассетов данного типа для проверки наличия
        # 4 - создание таблицы если нет
        # 5 - проверка на совпадение имени ассета
        # 6 - создание ассетов - проверки:
        # --6.1 - наличие name, group(id), season
        # --6.2 - изменение имени
        # --6.3 - добавление значений (type, status, priority) в словарь ассета
        # --6.4 - создание id с проверкой на совпадение.
        # --6.5 - создание директорий
        # --6.6 - создание ассета в БД
        
        # (1) test valid asset_type
        if not asset_type in self.asset_types:
            return(False, 'Asset_Type (%s) is Not Valid!' % asset_type)
        # (2) test valid type of list_keys
        if list_keys.__class__.__name__!= 'list':
            return(False, 'The type of "list_keys" (%s) is Not Valid! There must be a "list"' % list_keys.__class__.__name__)
        # start data
        make_assets = {}
        # get list assets
        assets = []
        ids = []
        result = self.get_list_by_all_types()
        if result[0]:
            for row in result[1]:
                assets.append(row.name)
                ids.append(row.id)
        else:
            print('#'*5)
            print(result[1])
            
        # (4) cteate table
        bool_, return_data = database().create_table('project', self.project, asset_type, self.asset_keys, table_root = self.assets_db)
        if not bool_:
            return(bool_, return_data)
        
        #
        if not list_keys:
            return(False, 'No data to create an Asset!')
        # (5) test exists name
        for keys in list_keys:
            if keys['name'] in assets:
                return(False, 'The name "%s" already exists!' % keys['name'])
        # (6) create assets
        b, r = set_of_tasks().get_dict_by_all_types()
        if not b:
            return(b, r)
        else:
            set_of_tasks_dict = r
        for keys in list_keys:
            # (6.1)
            # test name
            if not keys.get('name'):
                return(False,('No name!'))
            # test group(id)
            if not keys.get('group'):
                return(False, 'In the asset "%s" does not specify a group!' % keys['name'])
            # test season
            '''
            if asset_type in self.asset_types_with_season and not keys.get('season'):
                return(False, 'In the asset "%s" does not specify a season' % keys['name'])
            elif not asset_type in self.asset_types_with_season and not keys.get('season'):
                keys['season'] = ''
            '''
            # (6.2) edit name
            if asset_type in ['shot_animation']:
                keys['name'] = keys['name'].replace(' ', '_')
            else:
                keys['name'] = keys['name'].replace(' ', '_').replace('.', '_')
            # (6.3) make keys
            keys['type'] = asset_type
            keys['status'] = 'active'
            if not keys.get('priority'):
                keys['priority'] = 0
            # -- loading_type
            if keys['type']=='object' and keys.get('set_of_tasks'):
                if set_of_tasks_dict.get('object') and keys.get('set_of_tasks') in set_of_tasks_dict['object']:
                    keys['loading_type'] = set_of_tasks_dict['object'][keys.get('set_of_tasks')].loading_type
            
            # (6.4) get id
            keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
            while keys['id'] in ids:
                keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')

            # (6.5) create Folders
            group_dir = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset_type))
            asset_path = NormPath(os.path.join(group_dir, keys['name']))
            # -- create group folder
            if not os.path.exists(group_dir):
                try:
                    os.mkdir(group_dir)
                except Exception as e:
                    print('#'*5, 'In asset.create() -- create group folder')
                    print(e)
                    return(False, 'Exception in asset.create() look the terminal!')
            # -- create root folder
            if not os.path.exists(asset_path):
                try:
                    os.mkdir(asset_path)
                except Exception as e:
                    print('#'*5, 'In asset.create() -- create root folder')
                    print(e)
                    return(False, 'Exception in asset.create() look the terminal!')
            
            # -- create activity folders
            for activity in self.ACTIVITY_FOLDER[asset_type]:
                folder_path = NormPath(os.path.join(asset_path, activity))
                if not os.path.exists(folder_path):
                    os.mkdir(folder_path)
                    
            # -- create additional folders  self.ADDITIONAL_FOLDERS
            for activity in self.ADDITIONAL_FOLDERS:
                folder_path = NormPath(os.path.join(asset_path, activity))
                if not os.path.exists(folder_path):
                    os.mkdir(folder_path)
            
            # (6.6) create in DB init
            bool_, return_data = database().insert('project', self.project, asset_type, self.asset_keys, keys, table_root=self.assets_db)
            if not bool_:
                return(bool_, return_data)
            
            ########### make task data
            
            this_asset_tasks = []
            # add service tasks ("final")
            final = {
                'asset_name':keys['name'],
                'asset_id': keys['id'],
                'asset_type': asset_type,
                'task_name': (keys['name'] + ':final'),
                #'season': keys['season'],
                'status':'null',
                'task_type':'service',
                'input':[],
                'output': [],
            }
            # create service tasks ("all_input")
            all_input = {
                'asset_name':keys['name'],
                'asset_id': keys['id'],
                'asset_type': asset_type,
                'task_name': (keys['name'] + ':all_input'),
                #'season': keys['season'],
                'status':'done',
                'task_type':'service',
                'input':[],
                'output': [],
            }
            this_asset_tasks.append(all_input)
            
            # get list from set_of_tasks
            result = set_of_tasks().get(keys.get('set_of_tasks'))
            if result[0]:
                print('**** by set of tasks: %s' % keys.get('set_of_tasks'))
                set_tasks = result[1].sets
                
                outputs = {}
                for task_ in set_tasks:
                    # name
                    name = task_['task_name']
                    task_['task_name'] = keys['name'] + ':' + name
                    
                    # output
                    #task_['output'] = json.dumps([final['task_name']])
                    task_['output'] = [final['task_name']]
                    
                    # input
                    input_ = task_['input']
                    if  input_ == 'all':
                        task_['input'] = all_input['task_name']
                        # status
                        task_['status'] = 'ready'
                        # add to output all_input
                        #all_outputs = json.loads(all_input['output'])
                        all_outputs = all_input['output']
                        all_outputs.append(task_['task_name'])
                        #all_input['output'] = json.dumps(all_outputs)
                        all_input['output'] = all_outputs
                        
                    elif input_ == 'pre':
                        task_['input'] = keys['name'] + ':pre_input:' + name
                        # status
                        task_['status'] = 'ready'
                        # add service tasks ("pre_input" )
                        pre_input = {
                            'asset_name':keys['name'],
                            'asset_id': keys['id'],
                            'asset_type': asset_type,
                            'task_name': task_['input'],
                            #'season': keys['season'],
                            'status':'done',
                            'task_type':'service',
                            'input':'',
                            #'output': json.dumps([final['task_name'], task_['task_name']])
                            #'output': json.dumps([task_['task_name']])
                            'output': [task_['task_name']]
                        }
                        this_asset_tasks.append(pre_input)
                    elif input_:
                        task_['input'] = keys['name'] + ':' + input_
                        # status
                        task_['status'] = 'null'
                        
                        # outputs
                        if task_['input'] in outputs.keys():
                            outputs[task_['input']].append(task_['task_name'])
                        else:
                            outputs[task_['input']] = [task_['task_name'],]
                        
                    else:
                        # status
                        task_['status'] = 'ready'
                        
                    # price
                    task_['price'] = task_['cost']
                        
                    # asset
                    #task_['asset_name'] = keys['name']
                    #task_['asset_id'] = keys['id']
                    #task_['asset_type'] = asset_type
                    
                    # season
                    #task_['season'] = keys['season']
                    
                    # readers
                    task_['readers'] = {}
                    
                    # append task
                    this_asset_tasks.append(task_)
                    
                for task_ in this_asset_tasks:
                    if task_['task_name'] in outputs:
                        if task_['output']:
                            #task_outputs = json.loads(task_['output'])
                            task_outputs = task_['output']
                            task_outputs = task_outputs + outputs[task_['task_name']]
                            #task_['output'] = json.dumps(task_outputs)
                            task_['output'] = task_outputs
                        else:
                            #task_['output'] = json.dumps(outputs['task_name'])
                            task_['output'] = outputs['task_name']
            else:
                print('**** without sets')
            
            # set input of "final"
            final_input = []
            for task_ in this_asset_tasks:
                final_input.append(task_['task_name'])
            #final['input'] = json.dumps(final_input)
            final['input'] = final_input
            
            # append final to task list
            this_asset_tasks.append(final)
            
            #print(this_asset_tasks)
            
            ########### create tasks (by task data)
            #c = json.dumps(this_asset_tasks, sort_keys=True, indent=4)
            #print(c)
            new_asset = self.init_by_keys(keys)
            result = task(new_asset).create_tasks_from_list(this_asset_tasks)
            if not result[0]:
                return(False, result[1])
            
            ########### make return data
            # path
            keys['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],keys['type'], keys['name']))
            #
            make_assets[keys['name']] = self.init_by_keys(keys)
        
        return(True, make_assets)

    def remove(self): # v2
        """Перемещение текущего ассета в корзину, снятие задач с исполниетлей, изменение статуса и приоритета, разрыв исходящих связей ассета. Физически файлы ассета не удаляются.
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        pass
        # 1 - получение id recycle_bin
        # 2 - замена группы ассета на recycle_bin, обнуление priority, status.
        # 3 - список задач ассета
        # 4 - перезапись задачь ассета, обнуление: status, artist, readers, priority.
        # 5 - разрывы исходящих связей в другие ассеты.
        
        # (1)
        # -- get recycle bin  data
        result = group(self.project).get_by_keys({'type': 'recycle_bin'})
        if not result[0]:
            return(False, ('in asset().remove' + result[1]))
        recycle_bin = result[1][0]
        
        # (2)
        update_data = {'group': recycle_bin.id, 'priority': 0, 'status':'none'}
        where = {'id': self.id}
        bool_, return_data = database().update('project', self.project, self.type, self.asset_keys, update_data, where, table_root=self.assets_db)
        if not bool_:
            return(bool_, return_data)
                
        # (3)
        bool_, task_list = task(self).get_list()
        if not bool_:
            return(bool_, task_list)
        
        output_tasks = []
        output_tasks_name_list = []
        table = '"%s:%s"' % (self.id, self.tasks_t)
        # (4)
        for row in task_list:
            if row.task_type == 'service':
                continue
            if row.output:
                for task_name in row.output:
                    if task_name.split(':')[0] != row.asset.name:
                        output_tasks.append((row, task_name))
                        output_tasks_name_list.append(task_name)
            # -- -- get status
            new_status = 'null'
            if not row.input:
                new_status = 'ready'
            
            update_data = {'artist':'', 'status': new_status, 'readers': [], 'priority':0}
            where = {'task_name': row.task_name}
            bool_, r_data = database().update('project', self.project, table, self.tasks_keys, update_data, where, table_root=self.tasks_db)
            if not bool_:
                bool_, r_data
        
        # (5)
        # ******** DISCONNECT OUTPUTS
        # -- get output tasks dict
        result = task(self).get_tasks_by_name_list(output_tasks_name_list)
        if not result[0]:
            return(False, ('in asset().remove - %s' % result[1]))
        output_tasks_data_dict = result[1]
        
        for key in output_tasks:
            if not key[1]:
                continue
            if output_tasks_data_dict[key[1]].task_type == 'service':
                b,r = output_tasks_data_dict[key[1]]._service_remove_task_from_input([key[0]])
                if not b:
                    return(b,r)
            else:
                print((output_tasks_data_dict[key[1]].task_name + ' not service!'))
                continue
        
        return(True, 'Ok!')

    def copy_of_asset(self, new_group_name, new_asset_name, new_asset_type, set_of_tasks): # v2
        """Копирование текущего ассета.
        
        Parameters
        ----------
        new_group_name : str
            Имя группы для создаваемого ассета.
        new_asset_name : str
            Имя создаваемого ассета.
        new_asset_type : str
            Тип создаваемого ассета, значение из списка :attr:`edit_db.studio.asset_types`.
        set_of_tasks : str
            Имя набора задач.
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        
        pass
        # 0 - test work_dir
        # 1 - приведение имени нового ассета к стандарту
        # 2 - получение id группы по имени
        # 3 - заполнение словаря на создание ассета(new_keys) - по данным self и новым данным
        # 4 - 
        # 5 - создание ассета
        # 6 - копирование директорий
        # 6.1 - метадата
        # 6.2 - рабочие активити
        # 7 - copy preview images
        
        # (0)
        if not self.work_folder:
            return(False, 'Working directory not defined!')
        
        # (1) edit name
        if not new_asset_name:
            return(False, 'New asset name is not specified!')
        elif not new_group_name:
            return(False, 'New group name is not specified!')
        elif not new_asset_type:
            return(False, 'New type of asset is not specified!')
        elif not set_of_tasks:
            return(False, '"Set of tasks" is not specified!')
        
        #
        if new_asset_type in ['shot_animation']:
            new_asset_name = new_asset_name.replace(' ', '_')
        else:
            new_asset_name = new_asset_name.replace(' ', '_').replace('.', '_')
        
        # (2) get group id
        result = group(self.project).get_by_name(new_group_name)
        if not result[0]:
            return(False, result[1])
        new_group_id = result[1].id
        
        # (3)
        new_keys={}
        asset_list_keys = list(self.asset_keys.keys()) + ['path']
        for key in asset_list_keys:
            if key in dir(self):
                new_keys[key] = getattr(self, key)
            else:
                new_keys[key] = None
        #
        new_keys['set_of_tasks'] = set_of_tasks
        new_keys['type'] = new_asset_type
        new_keys['group'] = new_group_id
        new_keys['name'] = new_asset_name
        new_keys['path'] = ''
        #
        list_keys = [new_keys]
        
        #print(json.dumps(list_keys, sort_keys = True, indent = 4))
        
        # (5) make asset
        result = self.create(new_asset_type, list_keys)
        if not result[0]:
            return(False, result[1])
        new_asset = result[1][new_asset_name]
            
        # (6) copy activity files
        # (6.1) copy meta data
        for key in self.ADDITIONAL_FOLDERS:
            pass
            #src_activity_path = NormPath(os.path.join(self.path, self.ADDITIONAL_FOLDERS[key]))
            src_activity_path = NormPath(os.path.join(self.path, key))
            #dst_activity_path = NormPath(os.path.join(new_asset.path, self.ADDITIONAL_FOLDERS[key]))
            dst_activity_path = NormPath(os.path.join(new_asset.path, key))
            for obj in os.listdir(src_activity_path):
                src = NormPath(os.path.join(src_activity_path, obj))
                dst = NormPath(os.path.join(dst_activity_path, obj.replace(self.name, new_asset_name))) # + replace name
                #print('*'*50)
                #print('src', src)
                #print('dst', dst)
                if os.path.isfile(src):
                    shutil.copyfile(src, dst)
                elif os.path.isdir(src):
                    shutil.copytree(src, dst)
        
        # (6.2) copy activity version
        # -- get task_list of old asset
        b, old_tasks = task(self).get_list()
        if not b:
            return(b, old_tasks)
        # -- get task_list of new asset
        b, new_tasks = task(new_asset).get_list()
        if not b:
            return(b, new_tasks)
        #
        used_activites = list()
        #
        for new_tsk in new_tasks:
            pass
            if new_tsk.activity in used_activites:
                continue
            elif new_tsk.task_type=='service':
                continue
            # -- get tasks
            old_tsk=None
            for old_tsk in old_tasks:
                if old_tsk.activity == new_tsk.activity:
                    used_activites.append(new_tsk.activity)
                    break
            if not old_tsk:
                print('*** There is no task in the source asset with this activity: %s' % new_tsk.activity)
                continue
            # -- get final push file path
            b, r = old_tsk.get_final_push_file_path()
            if not b:
                print('### %s in %s' % (r, old_tsk.task_name))
                #return(b,r)
                continue
            #
            description = 'copy asset from "%s"' % self.name
            #
            if new_tsk.task_type in self.multi_publish_task_types:
                for branch, source_path in r[0]['push_path'].items():
                    new_tsk.open_time = datetime.datetime.now()
                    new_tsk.commit(source_path, description, branch=branch)
                new_tsk.push(description)
            else:
                source_path = r[0]
                new_tsk.open_time = datetime.datetime.now()
                new_tsk.commit(source_path, description)
                new_tsk.push(description)

        # (7) copy preview image
        img_folder_path = NormPath(os.path.join(self.project.path, self.project.folders['preview_images']))
        old_img_path = NormPath(os.path.join(img_folder_path, (self.name + self.preview_extension)))
        old_img_icon_path = NormPath(os.path.join(img_folder_path, (self.name + '_icon%s' % self.preview_extension)))
        new_img_path = NormPath(os.path.join(img_folder_path, (new_asset_name + self.preview_extension)))
        new_img_icon_path = NormPath(os.path.join(img_folder_path, (new_asset_name + '_icon%s' % self.preview_extension)))
        
        if os.path.exists(old_img_path):
            shutil.copyfile(old_img_path, new_img_path)
        if os.path.exists(old_img_icon_path):
            shutil.copyfile(old_img_icon_path, new_img_icon_path)
        
        return(True, 'Ok!')

    def get_list_by_type(self, asset_type=False): # v2
        """Возвращает ассеты (экземпляры) по типу. Если не указывать тип ассета, вернёт ассеты по всем типам.
        
        Parameters
        ----------
        asset_type : str, optional
            Тип ассета, значение из списка :attr:`edit_db.studio.asset_types`. Если не передавать, то возвращается список ассетов по всем типам.
            
        Returns
        -------
        tuple
            (*True*, [экземпляры :obj:`edit_db.asset`]) или (*False, comment*)
        """
        pass
        #
        
        where = False
        assets_list = []
        r_data = []
        if not asset_type:
            for asset_type in self.asset_types:
                b, r = database().read('project', self.project, asset_type, self.asset_keys, where = where, table_root=self.assets_db)
                if not b:
                    print('#'*5, r)
                    continue
                else:
                    assets_list = assets_list + r
        else:
            b, r = database().read('project', self.project, asset_type, self.asset_keys, where = where, table_root=self.assets_db)
            if not b:
                print('#'*5, r)
                return(True, [])
            else:
                assets_list = r
                
        for asset in assets_list:
            r_data.append(self.init_by_keys(asset))
        return(True, r_data)

    def get_list_by_all_types(self): # v2
        """Возвращает ассеты (экземпляры) по всем типам. Обёртка на :func:`edit_db.asset.get_list_by_type`
        
        Returns
        -------
        tuple
            (*True*, [экземпляры :obj:`edit_db.asset`]) или (*False, comment*)
        """
        b, r = self.get_list_by_type()
        return(b, r)

    def get_list_by_group(self, group_ob): # v2
        """Возвращает список ассетов группы.
        
        Parameters
        ----------
        group_ob : :obj:`edit_db.group`
            Группа - экземпляр.
        
        Returns
        -------
        tuple
            (*True*, [экземпляры :obj:`edit_db.asset`]) или (*False, comment*)
        """
        pass
        # 1 - тест типа переменной group
        # 2 - чтение БД
        
        # (1)
        if not isinstance(group_ob, group):
            return(False, 'asset.get_list_by_group(): the data type of the variable passed to this procedure must be a "group", passed type: "%s"' % group_ob.__class__.__name__)
        
        # (2)
        assets = []
        where = {'group': group_ob.id}
        if group_ob.type == 'recycle_bin':
            for asset_type in self.asset_types:
                b, r = database().read('project', group_ob.project, asset_type, self.asset_keys, where = where, table_root=self.assets_db)
                if not b:
                    print('#'*5, r)
                    continue
                else:
                    assets = assets + r
        else:
            bool_, assets = database().read('project', group_ob.project, group_ob.type, self.asset_keys, where = where, table_root=self.assets_db)
            if not bool_:
                print('#'*5, assets)
                return(True, [])
        
        r_data = []
        for asset in assets:
            #asset['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset['type'], asset['name']))
            r_data.append(self.init_by_keys(asset))
        return(True, r_data)
    
    # Нигде не используется
    def get_id_name_dict_by_type(self, asset_type): # v2
        bool_, return_data = database().read('project', self.project, asset_type, self.asset_keys, table_root=self.assets_db)
        if not bool_:
            return(bool_, return_data)
        asset_id_name_dict = {}
        for row in return_data:
            #row['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],row['type'], row['name']))
            asset_id_name_dict[row['id']] = row['name']
        return(True, asset_id_name_dict)
    
    def get_dict_by_name_by_all_types(self): # v2
        """Возвращает словарь ассетов (экземпляры) по именам, по всем типам.
        
        Returns
        -------
        tuple
            (*True*, {'asset_name' : экземпляр (:obj:`edit_db.asset`), ... }) или (*False, comment*)
        """
        asset_list = []
        for asset_type in self.asset_types:
            bool_, return_data = database().read('project', self.project, asset_type, self.asset_keys, table_root=self.assets_db)
            if not bool_:
                print(return_data)
                continue
            asset_list = asset_list + return_data
        # make dict
        assets_dict = {}
        for asset in asset_list:
            asset['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset['type'], asset['name']))
            assets_dict[asset['name']] = self.init_by_keys(asset)
        return(True, assets_dict)
            
    def get_by_id(self, asset_id): # v2
        """Возвращает экземпляр ассета по его *id*.
        
        Parameters
        ----------
        asset_id : str
            *id* ассета.
        
        Returns
        -------
        tuple
            (*True*, :obj:`edit_db.asset`) или (*False, comment*)
        """
        where = {'id': asset_id}
        asset_data = False
        for asset_type in self.asset_types:
            bool_, return_data = database().read('project', self.project, asset_type, self.asset_keys, where=where, table_root=self.assets_db)
            if not bool_:
                print(return_data)
                continue
            if return_data:
                asset_data = return_data[0]
                #asset_data['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset_data['type'], asset_data['name']))
                return(True, self.init_by_keys(asset_data, new=True))
        if not asset_data:
            return(False, 'No Asset With This id(%s)!' % asset_id)

    # не используетя
    # keys - словарь по asset_keys, 
    # -- *name - для идентификации ассета
    # -- *type - для идентификации таблицы
    # -- не меняемые значения 'name', 'type', 'id', 'path'
    def edit_asset_data_by_name(self, keys): # v2
        pass
        # test Name Type
        if not 'name' in keys:
            return(False, 'Name not specified!')
        elif not 'type' in keys:
            return(False, 'Type not specified!')
        
        where = {'name': keys['name']}
        table_name = keys['type']
        # cleaning keys
        del keys['name']
        for key in self.UNCHANGEABLE_KEYS:
            if key in keys:
                del keys[key]
        # update
        bool_, return_data = database().update('project', self.project, table_name, self.asset_keys, keys, where, table_root=self.assets_db)
        if not bool_:
            return(bool_, return_data)
        
        return(True, 'Ok!')

    # не используетя
    # keys - словарь по asset_keys, 
    # -- *id - для идентификации ассета
    # -- *type - для идентификации таблицы
    # -- не меняемые значения: 'name', 'type', 'id', 'path'
    def edit_asset_data_by_id(self, keys): # v2
        pass
        # test Name Type
        if not 'id' in keys:
            return(False, 'Id not specified!')
        elif not 'type' in keys:
            return(False, 'Type not specified!')
        
        where = {'id': keys['id']}
        table_name = keys['type']
        # cleaning keys
        for key in self.UNCHANGEABLE_KEYS:
            if key in keys:
                del keys[key]
        # update
        bool_, return_data = database().update('project', self.project, table_name, self.asset_keys, keys, where, table_root=self.assets_db)
        if not bool_:
            return(bool_, return_data)
        
        return(True, 'Ok!')
    
    def change_group(self, group_id): # v2
        """Изменение группы ассета.
        
        Parameters
        ----------
        group_id : str
            *id* новой группы.
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        where = {'name': self.name}
        keys={'group': group_id}
        
        # update
        table_name = self.type
        b, r = database().update('project', self.project, table_name, self.asset_keys, keys, where, table_root=self.assets_db)
        if not b:
            return(b, r)
        
        self.group = group_id
        return(True, 'Ok!')

    def change_priority(self, priority):
        """Изменение приоритета ассета.
        
        Parameters
        ----------
        priority : int
            Новый приоритет.
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        pass
        where = {'name': self.name}
        keys={'priority': priority}
        
        # update
        table_name = self.type
        b, r = database().update('project', self.project, table_name, self.asset_keys, keys, where, table_root=self.assets_db)
        if not b:
            return(b, r)
        
        self.priority = priority
        return(True, 'Ok!')

    def change_description(self, description):
        """Изменение описания текущего ассета.
        
        Parameters
        ----------
        description : str
            Новое описание.
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        pass
        where = {'name': self.name}
        keys={'description': description}
        
        # update
        table_name = self.type
        b, r = database().update('project', self.project, table_name, self.asset_keys, keys, where, table_root=self.assets_db)
        if not b:
            return(b, r)
        
        self.description = description
        return(True, 'Ok!')

    def change_loading_type(self, loading_type):
        """Смена типа загрузки ассета, для типа ``object``.
        
        Parameters
        ----------
        loading_type : str
            Тип загрузки, значение из :attr:`edit_db.studio.loading_types`.
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        pass
        if self.type not in ['object']:
            return(False, 'For an asset with this type "%s", the "loading_type" parameter cannot be changed' % self.type)
        if not loading_type in self.loading_types:
            return(False, 'Wrong loading_type: "%s"' % loading_type)
        #
        where = {'name': self.name}
        keys={'loading_type': loading_type}
        
        # update
        table_name = self.type
        b, r = database().update('project', self.project, table_name, self.asset_keys, keys, where, table_root=self.assets_db)
        if not b:
            return(b, r)
        
        self.loading_type = loading_type
        return(True, 'Ok!')
            
    def rename_asset(self, asset_type, old_name, new_name): # v2 ???????? ассет нельзя переименовывать!!!!!!!!!!!!!!!!!
        pass
        # get id by name
        result = self.get_by_name(asset_type, old_name)
        if not result[0]:
            return(False, result[1])
        
        # rename
        keys = {
        'name': new_name,
        'type': asset_type,
        'id': result[1]['id'],
        }
        
        result = self.edit_asset_data_by_id(keys)
        if not result[0]:
            return(False, result[1])
        else:
            return(True, 'Ok!')

class task(studio):
    '''
    **level** = 'project'
    
    Данные хранимые в БД (имя столбца : тип данных) :attr:`edit_db.studio.tasks_keys`:

    .. code-block:: python

        tasks_keys = {
        'activity': 'text',
        'task_name': 'text',
        'task_type': 'text',
        'source': 'json',
        'input': 'json',
        'status': 'text',
        'outsource': 'integer',
        'artist': 'text',           # nik_name
        'level': 'text',            # пользовательский уровень сложности задачи.
        'planned_time': 'real',
        'price': 'real',
        'time': 'json',             # словарь: ключи - nik_name, значения - ссумарное время атриста по этой задаче (ед. измерения - секунда).
        'full_time': 'real',        # ссумарное время всех атристов по этой задаче (ед. измерения - секунда).
        'deadline': 'timestamp',    # расчётная дата окончания работ.
        'start': 'timestamp',
        'end': 'timestamp',
        'specification': 'text',
        'chat_local': 'json',
        'web_chat': 'text',
        'supervisor': 'text',
        'readers': 'json',          # словарь: ключ - nik_name, значение - 0 или 1 (статус проверки),  плюс одна запись: ключ - 'first_reader', значение - nik_name - это первый проверяющий - пока он не проверит даннаня задача не будет видна у других проверяющих в списке на проверку.
        'output': 'json',
        'priority':'integer',
        'extension': 'text',
        'description': 'text',      # описание задачи
        }
        
    Examples
    --------
    Создание экземпляра класса:

    .. code-block:: python
    
        import edit_db as db
  
        project = db.project()
        asset = db.asset(project)
        
        task = db.task(asset) # asset - обязательный параметр при создании экземпляра task
        # доступ ко всем параметрам и методам принимаемого экземпляра asset - через task.asset
        
    Attributes
    ----------
    activity : str
        Активити из :attr:`edit_db.asset.ACTIVITY_FOLDER` [asset_type]
    task_name : str
        Имя задачи, структура имени: ``asset_name:task_name``
    task_type : str
        Тип задачи из :attr:`edit_db.studio.task_types` + ``service``
    source : list
        Имена задач, объекты из активити которых используются как исходники.
    input : str, list
        Для сервисной задачи (``task_type`` = ``service``) - это список имён входящих задач. для не сервисной задачи - это имя входящей задачи.
    status : str
        Cтатус задачи из :attr:`edit_db.studio.task_status`
    outsource : int
        Значение из ``[0, 1]`` если = ``1`` - задача на аутсорсе.
    artist : str
        ``nik_name`` исполнителя.
    level : text
        Пользовательский уровень сложности задачи.
    planned_time : float
        Планируемое время (ед. измерения - час).
    price : float
        Стоимость работ по задаче (ед. измерения - юнит).
    time : dict
        Словарь: ключи - ``nik_name``, значения - ссумарное время атриста по этой задаче (ед. измерения - секунда).
    full_time : real
        Ссумарное время всех атристов по этой задаче (ед. измерения - секунда).
    deadline : timestamp
        Расчётная дата окончания работ.
    start : timestamp
        Дата и время взятия задачи в работу.
    end : timestamp
        Дата и время приёма задачи.
    specification : str
        Ссылка на техническое задание.
    chat_local : str
        ``?``
    web_chat : str
        ``?``
    supervisor : str
        ``?``
    readers : dict
        Словарь: ключ - ``nik_name``, значение - ``0`` или ``1`` (статус проверки),  \
        плюс одна запись: ключ - ``first_reader``, значение - ``nik_name`` - это первый проверяющий - пока он не проверит даннаня задача не будет видна у других проверяющих в списке на проверку.
    output : list
        Список имён исходящих задач.
    priority : int
        Приоритет.
    extension : str
        Расширение файла для работы над данной задачей, начинается с точки, например: ``.blend``
    approved_date : ``timestamp``
        Дата планируемого окончания работ (вычисляется при создании экземпляра)
    asset : :obj:`edit_db.asset`
        Экземпляр ``asset`` принимаемый при создании экземпляра класса, содержит все атрибуты и методы :class:`edit_db.asset` .
    description : text
        Описание задачи
    branches : list
        ``атрибут класса`` - список веток активити задачи. Заполняется при выполнении метода :func:`edit_db.task._set_branches`
    
    '''
    
    branches = list()
    
    VARIABLE_STATUSES = ('ready', 'ready_to_send', 'work', 'work_to_outsorce')
    """tuple: ``?`` """
    
    CHANGE_BY_OUTSOURCE_STATUSES = {
        'to_outsource':{'ready':'ready_to_send', 'work':'ready_to_send'},
        'to_studio':{'ready_to_send':'ready', 'work_to_outsorce':'ready'},
    }
    """dict: Описание того как менять некоторые статусы задач, при изменении статуса исполнителя на аутсорс, или наоборот с аутсорса в студию.
    
    .. rubric:: Структура словаря:
    
    .. code-block:: python
        
        {
        'to_outsource': {
                status_name_from : status_name_to,
                ...
                },
        'to_studio': {
                status_name_from : status_name_to,
                ...
                },
        }
    
    """

    def __init__(self, asset_ob):
        if not isinstance(asset_ob, asset):
            raise Exception('in task.__init__() - Object is not the right type "%s", must be "asset"' % asset_ob.__class__.__name__)
        self.asset = asset_ob
        
        for key in self.tasks_keys:
            setattr(self, key, False)
        
        #self.db_workroom = workroom() # ??????? как всегда под вопросом
        #self.publish = lineyka_publish.publish()
        
        self.publish = publish(NormPath) # ??????? как всегда под вопросом
        
    @classmethod
    def _set_branches(self, branches):
        """Заполнение ``атрибута класса`` :attr:`edit_db.task.branches`
        
        Parameters
        ----------
        branches : list
            Список веток получаемый при выполнении :func:`edit_db.log.read_log`
            
        Returns
        -------
        None
            *None*
        """
        self.branches = branches
    
    def init(self, task_name, new = True):
        """Инициализация по имени, возвращает новый, или инициализирует текущий экземпляр.
        
        Parameters
        ----------
        task_name : str
            Имя задачи
        new : bool
            Если *True* - возвращает новый инициализированный экземпляр, если *False* то инициализирует текущий экземпляр.
            
        Returns
        -------
        :obj:`edit_db.task`, tuple
            * если new= *True* - экземпляр класса :obj:`edit_db.task`,
            * если new= *False* - (*True,  'Ok!'*) или (*False, comment*)
        """
        pass
        # get keys
        b, r = self._read_task(task_name)
        if not b:
            return(b, r)
        
        return(self.init_by_keys(r[0], new=new, new_asset=r[1]))
    
    def init_by_keys(self, keys, new = True, new_asset=False):
        """Инициализация по словарю (без чтения БД), возвращает новый, или инициализирует текущий экземпляр.
        
        Parameters
        ----------
        keys : dict
            словарь по :attr:`edit_db.studio.tasks_keys`
        new : bool, optional
            если *True* - возвращает новый инициализированный экземпляр, если *False* то инициализирует текущий.
        new_asset : :obj:`edit_db.asset`, optional
            Новый экземпляр ассета, если надо его поменять, либо определить.
        
        Returns
        -------
        :obj:`edit_db.task`, tuple
            * если new= *True* - экземпляр класса :obj:`edit_db.task`,
            * если new= *False* - (*True,  'Ok!'*) или (*False, comment*)
        """
        
        pass
        if new:
            if new_asset:
                r_ob = task(new_asset)
            else:
                r_ob = task(self.asset)
        else:
            r_ob = self
            if new_asset:
                self.asset = new_asset
            
        for key in self.tasks_keys:
            setattr(r_ob, key, keys.get(key))
        
        # approved_date
        r_ob.approved_date = ''
            
        if new:
            return(r_ob)
        else:
            return(True, 'Ok')
        
    # ************************ CHANGE STATUS ******************************** start

    @staticmethod
    def _input_to_end(task_ob): # v2
        if task_ob.status == 'close':
            return(False)
        
        autsource = bool(task_ob.outsource)
                
        if autsource:
            return('ready_to_send')
        else:
            return('ready')

    def _service_input_to_end(self, assets): # v2 *** не тестилось.
        """Изменение статуса текущей сервисной задачи, по проверке статусов входящих задач. и далее задач по цепочке.
        
        Parameters
        ----------
        assets : dict
            Словарь всех ассетов по всем типам (ключи - имена, значения - ассеты (экземпляры)) - результат функции :func:`edit_db.asset.get_dict_by_name_by_all_types`
            
        Returns
        -------
        tuple
            (*True*, ``new_status``) или (*False, comment*)
        """
        new_status = False
        
        # (1) get input_list
        input_list = self.input
        if not input_list:
            return(True, new_status)
        
        # get status
        bool_statuses = []
        # --------------- fill end_statuses -------------
        for task_name in input_list:
            # (2) asse id
            asset_name = task_name.split(':')[0]
            asset_ob = assets.get(asset_name)
            if not asset_ob:
                print('in task._service_input_to_end() incorrect asset_name  "%s"' % asset_name)
                continue
            # (3) get task data
            task_ob = task(asset_ob).init(task_name)
            
            # (4) make status
            if task_ob.status in self.end_statuses:
                bool_statuses.append(True)
            else:
                bool_statuses.append(False)
        
        #conn.close()
        
        if False in bool_statuses:
            new_status = 'null'
        else:
            new_status = 'done'
            #self._this_change_to_end(self, project_name, task_data)
            
        return(True, new_status)

    def _from_input_status(self, input_task, this_task=False):  # v2 no test
        """Возвращает новый статус задачи (текущей или ``this_task``) на основе входящей задачи, не меняя статуса данной задачи.
        
        Parameters
        ----------
        input_task : :obj:`edit_db.task`
            Входящая задача
        this_task : :obj:`edit_db.task`, optional
            Задача для которой определяется статус, если не передавать, то статус будет определятся для текущей задачи.
            
        Returns
        -------
        str
            Новый статус, значение из :attr:`edit_db.studio.task_status`
        
        """
        pass
        if not this_task:
            this_task=self
        # get task_outsource
        task_outsource = bool(this_task.outsource)
        
        new_status = 'null'
        # change status
        if input_task:
            if input_task.status in self.end_statuses:
                if not task_outsource:
                    if this_task.status == 'null':
                        new_status = 'ready'
                else:
                    if this_task.status == 'null':
                        new_status = 'ready_to_send'
            else:
                if this_task.status != 'close':
                    new_status = 'null'
        else:
            if not this_task.status in self.end_statuses:
                if task_outsource:
                    new_status = 'ready_to_send'
                else:
                    new_status = 'ready'
        return(new_status)
    
    def _this_change_from_end(self, this_task=False, assets = False): # v2 *** no test
        """Замена статусов исходящих задач при изменении статуса текущей задачи с ``done`` или с ``close``.
        
        Parameters
        ----------
        this_task : :obj:`edit_db.task`, optional
            Задача относительно которой будут менятся статусы, если не передавать, то статусы будут менятся относительно текущей задачи.
        assets : dict, optional
            Словарь всех ассетов по всем типам (ключи - имена, значения - ассеты (экземпляры)) - результат функции :func:`edit_db.asset.get_dict_by_name_by_all_types`
            
        Returns
        -------
        tuple
            (*True,  'Ok!'*) или (*False, comment*)
        """
        pass
        # 0 - задаём объект текущей задачи
        # 1 - список исходящих задачь
        # 2 - получение списка всех ассетов
        # 3 - цикл по списку исходящих задачь (output_list)
        # - 4 - получение ассета
        # - 5 - чтение таска
        # - 6 - определение нового статуса
        # - 7 - изменения в readers
        # - 8 - запись таск
        # 9 - отправка далее в себя же - _this_change_from_end() - по списку from_end_list
        
        # (0)
        if not this_task:
            this_task=self
        
        #
        from_end_list = []
        this_asset_type = this_task.asset.type
        
        # (1)
        output_list = this_task.output
        if not output_list:
            return(True, 'Ok!')
        # (2)
        if not assets:
            # get assets dict
            result = self.asset.get_dict_by_name_by_all_types()
            if not result[0]:
                return(False, result[1])
            assets = result[1]
        
        # (3) ****** change status
        for task_name in output_list:
            # (4)
            asset_name = task_name.split(':')[0]
            asset_ob = assets.get(asset_name)
            if not asset_ob:
                print('in task._this_change_from_end() incorrect asset_name  "%s"' % asset_name)
                continue
            # (5) get task data
            task_ob = task(asset_ob).init(task_name)
            
            # (6) make new status char и obj не отключают локацию и аним шот, а локация отключает аним шот. ??????
            if task_ob.status == 'close':
                continue
            elif task_ob.asset.type in ['location', 'shot_animation'] and this_asset_type not in ['location', 'shot_animation']:
                continue
            elif task_ob.status == 'done':
                from_end_list.append(task_ob)
                
            new_status = 'null'
            # (7) edit readers
            readers = {}
            try:
                readers = task_ob.readers
            except:
                pass
            if readers:
                for key in readers:
                    readers[key] = 0
                #string = 'UPDATE ' +  table + ' SET  readers = ?, status  = ? WHERE task_name = ?'
                #data = (json.dumps(readers), new_status, task_name)
                update_data = {'readers': readers, 'status': new_status}
            else:
                #string = 'UPDATE ' +  table + ' SET  status  = ? WHERE task_name = ?'
                #data = (new_status, task_name)
                update_data = {'status': new_status}
            # (8)
            #c.execute(string, data)
            table_name = '"%s:%s"' % (task_ob.asset.id, self.tasks_t)
            where = {'task_name': task_name}
            bool_, return_data = database().update('project', task_ob.asset.project, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
            if not bool_:
                return(bool_, return_data)
        '''
        conn.commit()
        conn.close()
        '''
        
        # (9) ****** edit from_end_list
        if from_end_list:
            for t_ob in from_end_list:
                t_ob._this_change_from_end(assets = assets)
        
        
        return(True, 'Ok!')
    
    def _this_change_to_end(self, assets = False): # v2 *** no test
        """Замена статусов исходящих задач при изменении статуса текущей задачи на ``done`` или ``close``.
        
        Parameters
        ----------
        assets : dict, optional
            Словарь всех ассетов по всем типам (ключи - имена, значения - ассеты (экземпляры)) - результат функции :func:`edit_db.asset.get_dict_by_name_by_all_types`.
            
        Returns
        -------
        tuple
            (*True,  'Ok!'*) или (*False*, comment)        
        """
        pass
        # 1 - список исходящих задачь
        # 2 - получение списка всех ассетов
        # 3 - цикл по списку исходящих задачь (output_list)
        # - 4 - получение id ассета
        # - 5 - чтение таск даты
        # - 6 - определение нового статуса
        # - 7 - запись таск
        # 8 - отправка далее в себя же - _this_change_to_end() - по списку service_to_done
        
        # (1)
        output_list = self.output
        if not output_list:
            return(True, 'Ok!')
        # (2)
        if not assets:
            # get assets dict
            result = self.asset.get_dict_by_name_by_all_types()
            if not result[0]:
                return(False, result[1])
            assets = result[1]
        '''
        # ****** connect to db
        conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        '''
        service_to_done = []
        # ****** change status
        for task_name in output_list:
            # (4) asse id
            asset_id = assets[task_name.split(':')[0]].id
            if not asset_id:
                print('in _this_change_to_end incorrect key "id" in  "%s"' % task_name.split(':')[0])
                continue
            '''
            table = '\"' + asset_id + ':' + self.tasks_t + '\"'
            string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
            try:
                c.execute(string)
                task_data_ = c.fetchone()
            except:
                conn.close()
                return(False, ('in _this_change_to_end can not read ', string))
            '''
            # (5) get task data
            table_name = '"%s:%s"' % (asset_id, self.tasks_t)
            read_ob = self.asset.project
            where = {'task_name': task_name}
            bool_, return_data = database().read('project', read_ob, table_name, self.tasks_keys, where=where, table_root=self.tasks_db)
            if not bool_:
                return(bool_, return_data)
            elif return_data:
                task_data_ = self.init_by_keys(return_data[0])
            else:
                return(False, 'Task Data Not Found! Task_name - "%s"' % task_name)
            
            # (6) make new status
            if task_data_.task_type == 'service':
                #result = self._service_input_to_end(task_data_, assets)
                result = task_data_._service_input_to_end(assets)
                if not result[0]:
                    return(False, result[1])
                new_status = result[1]
                if new_status == 'done':
                    service_to_done.append(task_data_)
            else:
                new_status = self._input_to_end(task_data_)
                
            if not new_status:
                continue
            '''
            string = 'UPDATE ' +  table + ' SET  status  = ? WHERE task_name = ?'
            data = (new_status, task_name)
            c.execute(string, data)
            '''
            # (7)
            update_data = {'status': new_status}
            where = {'task_name': task_name}
            bool_, return_data = database().update('project', read_ob, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
            if not bool_:
                return(bool_, return_data)
        #conn.commit()
        #conn.close()
        # (8)
        if service_to_done:
            for task_ob in service_to_done:
                task_ob._this_change_to_end(assets = assets)
        
        return(True, 'Ok!')
    
    '''	
    def from_service_remove_input_tasks(self, project_name, task_data, removed_tasks_list):
        # get input_list
        input_list = json.loads(task_data['input'])
        for task in removed_tasks_list:
            input_list.remove(task['task_name'])
            
        if not input_list:
            return(True, 'done')
            
        # get assets dict
        result = self.get_dict_by_name_by_all_types(project_name)
        if not result[0]:
            return(False, result[1])
        assets = result[1]
        
        bool_statuses = []
        # --------------- fill end_statuses -------------
        
        # ****** connect to db
        conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        for task_name in input_list:
            try:
                asset_id = assets[task_name.split(':')[0]]['id']
            except:
                print(('in from_service_remove_input_tasks incorrect key: ' + task_name.split(':')[0] + ' in ' + task_name))
                continue
            
            table = '\"' + asset_id + ':' + self.tasks_t + '\"'
            
            string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
            try:
                c.execute(string)
                task_data = c.fetchone()
            except:
                conn.close()
                return(False, ('in from_service_remove_input_tasks can not read ', string))
                
            if task_data['status'] in self.end_statuses:
                bool_statuses.append(True)
            else:
                bool_statuses.append(False)
        
        conn.close()
        
        if False in bool_statuses:
            new_status = 'null'
        else:
            new_status = 'done'
            
        return(True, new_status)
    '''
    # **************************** Task() File Path ************************************************

    # Work пути

    def get_final_work_file_path(self, current_artist=False): # v2
        """Возвращает путь и версию последнего рабочего файла, для взятия в работу. Логика тут :ref:`task-specification-page`.
        
        Parameters
        ----------
        current_artist : :obj:`edit_db.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`
        
        Returns
        -------
        tuple
            (*True*, (``path``, ``version``)) или (*False, comment*), если нет ни одного лога вернёт (*True*, (``''``, ``''``)).
        """
        
        pass
        # 0 - current_artist
                
        # (0) artist
        if not current_artist:
            current_artist = artist()
            b, r = current_artist.get_user()
            if not b:
                return(b,r)
        #
        if not current_artist.outsource:
            pass
            # (1) загрузка push + commit + pull списков без учёта пользователя.
            # (2) если последняя запись commit - то берём по этой версии.
            # 	# если файл этой версии не в work директории данного пользователя, то будет предложено сделать push.
            # (3) если последняя запись push:
            #	# (4) не скетч - если commit версия этого push находится в work директории данного пользователя - то эта commit версия, 
            #   # (5) иначе - push.
            #   # (6) скетч
            #   # (6.1) - выбираем последний номер версии из log.source
            #   # (6.2) - если данный файл есть в рабочей директории данного пользователя - то это он
            #   # (6.3) - если его нет - то предлагается сделать pull
            # return - (path, номер версии)
            
            # (1)
            b, r = log(self).read_log(action=['commit', 'push', 'pull'])
            if not b:
                return(b, r)
            log_list = r[0]
            #
            if not log_list:
                return(True, ('',''))
            #
            end_log = log_list[-1:][0]
            # (2)
            if end_log['action'] in ['commit','pull']:
                b, version_path = self._template_get_work_path(self, version=end_log['version'])
                if not b:
                    return(b, version_path)
                if not os.path.exists(version_path):
                    return(False, 'the latest "%s" version is not in your working directory, this user: "%s" needs to "push"' % (end_log['action'], end_log['artist']))
                else:
                    return(True, (version_path, end_log['version']))
            # (3)
            elif end_log['action'] == 'push':
                if self.task_type not in self.multi_publish_task_types:
                    pass
                    # (4)
                    b, version_path = self._template_get_work_path(self, version=end_log['source'])
                    if not b:
                        return(b, version_path)
                    if os.path.exists(version_path):
                        return(True, (version_path, end_log['version']))
                    # (5)
                    else:
                        push_version_path = self._template_get_push_path(self, end_log['version'])
                        if not os.path.exists(push_version_path):
                            return(False, 'Path of the push version "%s" not found!')
                        else:
                            return(True, (push_version_path, end_log['version']))
                # (6) sketch
                else:
                    # (6.1)
                    version = int(end_log['source'][0])
                    for v in end_log['source']:
                        if int(v)>version:
                            version=v
                    # (6.2)
                    b, version_path = self._template_get_work_path(self, version=version)
                    if not b:
                        return(b, version_path)
                    #
                    if os.path.exists(version_path):
                        return(True, (version_path, version))
                    else:
                        # (6.3)
                        return(False, 'Need to execute the "Pull"!')
        #
        else:
            pass # outsource
            # 7 - загрузка списков commit + push + pull данного артиста.
            # 8 - если последняя запись commit или pull - то эта версия.
            # 8.1 - если файл отсутствует в рабочей директории - то предложение сделать push тем артистом, кто делал последний коммит или пул.
            # 9 - если последняя запись push
            # 9.1 - если не скетч - проверка наличия исходника пуша в ворк директории
            # 9.2 - если исходника пуша нет в ворк директории - предлагается чтобы менеджер сделал выгрузку пуш версии в облако и потом сделать пул.
            # 10 - если скетч - получаем последнюю версию рабочего файла исходника - если он есть в рабочей директории - то это он
            # 10.1 - если его нет - то предлагается чтобы менеджер сделал выгрузку пуш версии в облако и потом сделать пул.
            
            # (7)
            b, r = log(self).read_log(action=['commit', 'push', 'pull'])
            if not b:
                return(b, r)
            log_list = r[0]
            #
            if not log_list:
                return(True, ('',''))
            
            # (8)
            end_log = log_list[-1:][0]
            if end_log['action'] in ['commit','pull']:
                version_path = self._template_get_work_path(self, version=end_log['version'])
                if os.path.exists(version_path):
                    return(True, (version_path, end_log['version']))
                # (8.1)
                else:
                    return(False, 'the latest "%s" version is not in your working directory,\nthis user: "%s" needs to "push"' % (end_log['action'], end_log['artist']))
            # (9)
            elif end_log['action'] == 'push':
                # (9.1)
                if self.task_type != 'sketch':
                    version_path = self._template_get_work_path(self, version=end_log['source'])
                    if os.path.exists(version_path):
                        return(True, (version_path, end_log['source']))
                    else:
                        # (9.2)
                        return(False, 'the source of the "push" version "%s" is not in your working directory.\nAsk the manager to upload the latest version to the cloud,\n and make "pull."' % end_log['version'])
                else:
                    # (10)
                    version = int(end_log['source'][0])
                    for v in end_log['source']:
                        if int(v)>version:
                            version=v
                    version_path = self._template_get_work_path(self, version=version)
                    if os.path.exists(version_path):
                        return(True, (version_path, version))
                    else:
                        # (10.1)
                        return(False, 'the source of the "push" version "%s" is not in your working directory.\nAsk the manager to upload the latest version to the cloud,\n and make "pull."' % end_log['version'])

    def get_version_work_file_path(self, version):
        """Возвращает путь до указанной версии рабочего файла. (обёртка на :func:`edit_db.studio._template_get_work_path`)
        
        Parameters
        ----------
        version : str, int
            Номер версии
            
        Returns
        -------
        tuple
            (*True*, path) или (*False*, comment)
        """
        
        b, r = self._template_get_work_path(self, version)
        if not b:
            return(b, r)
        else:
            #print(r)
            if not os.path.exists(r):
                return(False, 'The path "%s" not exists!' % r)
            else:
                return(True, r)

    def get_new_work_file_path(self):
        """Создание пути для новой ``commit`` или ``pull`` версии файла.
        
        Returns
        -------
        tuple
            (*True*, (``path``, ``version``)) или (*False, comment*)        
        """
        
        pass
        # 1 - чтение commit + pull логов
        # 2 - новый номер версии
        # 3 - шаблонный путь

        # (1)
        b, r = log(self).read_log(action=['commit', 'pull'])
        if not b:
            return(b, r)
        
        # (2)
        if r[0]:
            log_list = r[0]
            end_log = log_list[-1:][0]
            version = int(end_log['version']) + 1
        else:
            b, version = self._template_version_num(0)
            if not b:
                return(b, version)
        
        # (3)
        b, r = self._template_get_work_path(self, version=version)
        if not b:
            return(b, r)
        else:
            return(True, (r, version))
        
    # Push пути
    
    def get_final_push_file_path(self, current_artist=False):
        """Возвращает путь и версию финальной ``push`` версии файла (на локальном сервере студии).
        
        Parameters
        ----------
        current_artist : :obj:`edit_db.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`
        
        Returns
        -------
        tuple
            * для задач с типом из :attr:`edit_db.studio.multi_publish_task_types` - (*True*, (``{path_data}`` [1]_, ``version``)) или (*False*, comment)
            * для остальных - (*True*, (``path``, ``version``)) - или (*False*, comment)
            
            .. [1] Структура словаря ``{path_data}`` :
            
                ::
                
                    {
                    'look_path': {
                        branch_name : path,
                        ...
                        },
                    'push_path': {
                        branch_name : path,
                        ...
                        },
                    }
        """
        
        pass
        # 0 - current_artist
        # 1 - игнор аутсорс
        # 2 - чтение пуш лога
        # 3 - получение путей
                
        # (0) artist
        if not current_artist:
            current_artist = artist()
            b, r = current_artist.get_user()
            if not b:
                return(b,r)
        
        # (1)
        if current_artist.outsource:
            return(False, 'This function is not available on outsourcing!')
        
        # (2)
        b, r = log(self).read_log(action='push')
        if not b:
            return(b, r)
        log_list = r[0]
        if log_list:
            end_log = log_list[-1:][0]
        else:
            return(False, 'Push versions not found!')
        
        # (3)
        if end_log:
            version = end_log['version']
            if self.task_type in self.multi_publish_task_types:
                pass
                r_data = dict()
                # -- push path
                b, r_push = self._template_get_push_path(self, version=version, branches=end_log['branch'], look=False)
                if not b:
                    return(b,r_push)
                # -- look path
                b, r_look = self._template_get_push_path(self, version=version, branches=end_log['branch'], look=True)
                if not b:
                    return(b,r_look)
                #
                r_data['push_path'] = r_push
                if self.task_type == 'sketch':
                    r_data['look_path'] = r_look
                else:
                    r_data['look_path'] = r_push
                '''
                for branch in end_log['branch']:
                    branch_dict = dict()
                    branch_dict['push_path'] = r_push[branch]
                    if self.task_type == 'sketch':
                        branch_dict['look_path'] = r_look[branch]
                    else:
                        branch_dict['look_path'] = r_push[branch]
                    r_data[branch] = branch_dict
                '''
            else:
                b, r = self._template_get_push_path(self, version=version)
                if not b:
                    return(b,r)
                r_data = r
        else:
            return(False, 'Push version missing!')
        
        return(True, (r_data, version))
    
    def get_version_push_file_path(self, version, current_artist=False):
        """Возвращает путь к указанной ``push`` версии файла (на локальном сервере студии).
        
        Parameters
        ----------
        version : str, int
            Номер версии
        current_artist : :obj:`edit_db.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`
        
        Returns
        -------
        tuple
            * для задач с типом из :attr:`edit_db.studio.multi_publish_task_types` - (*True*, ``{path_data}`` [2]_) или (*False*, comment)
            * для остальных - (*True*, ``path``) - или (*False*, comment)
            
            .. [2] Структура словаря ``{path_data}`` :
            
                ::
                
                    {
                    'look_path': {
                        branch_name : path,
                        ...
                        },
                    'push_path': {
                        branch_name : path,
                        ...
                        },
                    }
        """
        
        pass
        # 0 - current_artist
        # 1 - игнор аутсорс
        # 2 - получение push лога этой версии
        # 3 - получение путей
        
        # (0) artist
        if not current_artist:
            current_artist = artist()
            b, r = current_artist.get_user()
            if not b:
                return(b,r)
        
        # (1)
        if current_artist.outsource:
            return(False, 'This function is not available on outsourcing!')
        
        # (2)
        b, r = log(self).read_log(action='push')
        if not b:
            return(b, r)
        version_log = False
        for item in r[0]: # r[0] - это лог лист
            if int(item['version']) == int(version):
                version_log = item
        if not version_log:
            return(False, 'The push log of this version "%s" was not found' % version)
        
        # (3)
        if self.task_type in self.multi_publish_task_types:
            pass
            r_data = dict()
            # -- push path
            b, r_push = self._template_get_push_path(self, version=version, branches=version_log['branch'], look=False)
            if not b:
                return(b,r_push)
            # -- look path
            b, r_look = self._template_get_push_path(self, version=version, branches=version_log['branch'], look=True)
            if not b:
                return(b,r_look)
            #
            r_data['push_path'] = r_push
            if self.task_type in self.multi_publish_task_types:
                r_data['look_path'] = r_look
            else:
                r_data['look_path'] = r_push
            '''
            for branch in version_log['branch']:
                branch_dict = dict()
                branch_dict['push_path'] = r_push[branch]
                if self.task_type == 'sketch':
                    branch_dict['look_path'] = r_look[branch]
                else:
                    branch_dict['look_path'] = r_push[branch]
                r_data[branch] = branch_dict
            '''
        else:
            b, r = self._template_get_push_path(self, version=version)
            if not b:
                return(b,r)
            r_data = r
        
        return(True, r_data)

    def get_new_push_file_path(self, version=False, current_artist=False):
        """Возвращает как новые пути и версию для операции ``push``, так и пути и версии исходников из ``work`` директории.
        
        Parameters
        ----------
        version : str, int, optional
            Коммит версия исходника (не для задач с типом из :attr:`edit_db.studio.multi_publish_task_types`, для задач с этим типом делается ``push`` только последних версий каждой ветки).
        current_artist : :obj:`edit_db.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`
            
        Returns
        -------
        tuple
            * для задач с типом из :attr:`edit_db.studio.multi_publish_task_types` - (*True*, (``{path_data}`` [3]_, ``new_version``)) или (*False*, comment)
            * для остальных - (*True*, (``source_path``, ``source_version``, ``source_branch``, ``new_path``, ``new_version``)) - или (*False*, comment)
            
            .. [3] Структура словаря ``{path_data}`` :
            
                ::
                
                    {
                    'source_path': {
                        branch_name : path,
                        ...
                        },
                    'source_versions': {
                        branch_name : version,
                        ...
                        },
                    'push_path': {
                        branch_name : path,
                        ...
                        },
                    'look_path': {
                        branch_name : path,
                        ...
                        },
                    }
        
        """
        pass
        # 0 - test artist
        # 1 - чтение push лога
        # 2 - новый номер версии
        # 2.0 - чтение pull-commit лога
        # 3 - шаблонный путь для sketch
        # 3.1 - пути к источникам (для каждой ветки)
        # 3.2 - проверка на совпадение версий коммитов в последнем пуше с версиями источника.
        # 3.3 - составление новых push путей.
        # 4 - для не скетч
        # 4.1 - путь к источнику
        # 4.2 - проверка на совпадение версии коммита в последнем пуше с версией источника.
        # 4.3 - путь до нового push

        # (0) artist
        if not current_artist:
            current_artist = artist()
            b, r = current_artist.get_user()
            if not b:
                return(b,r)
        #
        if current_artist.outsource:
            return(False, 'This function is not available on outsourcing!')

        # (1)
        b, r = log(self).read_log(action=['push'])
        if not b:
            return(b, r)
        log_list = r[0]
        
        # (2)
        if log_list:
            end_push_log = log_list[-1:][0]
            new_version = int(end_push_log['version']) + 1
        else:
            end_push_log = dict()
            new_version = 0
        b, str_new_version = self._template_version_num(new_version)
        if not b:
            return(b, str_new_version)
        
        # (2.0)
        b, r = log(self).read_log(action=['commit', 'pull'])
        if not b:
            return(b, r)
        work_log_list = r[0]
        #
        if not work_log_list:
            return(False, 'Not "commit" or "pull" version!')
        end_work_log = work_log_list[-1:][0]
        
        # (3)
        if self.task_type in self.multi_publish_task_types:
            pass
            # (3.1)
            # -- clean branches
            branches = list()
            for branch in r[1]:
                if not '#' in branch:
                    branches.append(branch)
            # -- get source path
            source_path = dict()
            source_versions = dict()
            for branch in branches:
                for i in sorted(range(0, len(work_log_list)), reverse=True):
                    log_=work_log_list[-(i+1):][0]
                    if log_['branch']!=branch:
                        continue
                    b,r = self.get_version_work_file_path(log_['version'])
                    if not b:
                        return(b, r)
                    source_path[branch] = r
                    source_versions[branch] = log_['version']
            # (3.2)
            if end_push_log:
                if sorted(end_push_log['branch'])==sorted(branches):
                    overlap = list()
                    for i , branch in enumerate(end_push_log['branch']):
                        #print('*'*5, end_push_log['source'][i], source_versions[branch])
                        if end_push_log['source'][i] == source_versions[branch]:
                            overlap.append(True)
                        else:
                            overlap.append(False)
                    if not False in overlap:
                        return(False, 'Latest commit version matches the latest push version!')
            # (3.3)
            b ,r = self._template_get_push_path(self, version=new_version, branches=branches, look=False)
            if not b:
                return(b, r)
            push_path = r
            b ,r = self._template_get_push_path(self, version=new_version, branches=branches, look=True)
            if not b:
                return(b, r)
            look_path = r
            #
            r_data = dict()
            r_data['source_path']=source_path
            r_data['source_versions']=source_versions
            r_data['push_path']=push_path
            r_data['look_path']=look_path
            return(True, (r_data, str_new_version))
        # (4)
        else:
            pass
            # (4.1)
            if version:
                b, r = self._template_version_num(version)
                if not b:
                    return(b, r)
                else:
                    version=r
                b, r = self.get_version_work_file_path(version)
                if not b:
                    return(b, r)
                source_path = r
                source_version = version
            else:
                #end_work_log = work_log_list[-1:][0]
                b, r = self.get_version_work_file_path(end_work_log['version'])
                if not b:
                    return(b, r)
                source_path = r
                source_version = end_work_log['version']
            # (4.2)
            b, str_source_version = self._template_version_num(source_version)
            if not b:
                return (b, str_source_version)
            if end_push_log and str_source_version == end_push_log['source']:
                return(False, 'This commit version "%s" matches the latest push version!' % str_source_version)
            # (4.3)
            b, r = self._template_get_push_path(self, version=new_version)
            if not b:
                return(b, r)
            else:
                return(True, (source_path, str_source_version, end_work_log['branch'], r, str_new_version))

    def get_version_publish_file_path(self, version=False, branches=False, version_log=False):
        """Пути до файлов указанной ``publish`` версии (на локальном сервере студии).
        
        Parameters
        ----------
        version : str, int, optional
            Номер ``publish`` версии.
        branches : list, optional
            Список веток данного паблиша, для мультипаблиша.
        version_log : dict
            Словарь лога данной версии, если его передавать, то ``branches`` и ``version`` не имеют смысла.
            
        Returns
        -------
        tuple
            * для задач с типом из :attr:`edit_db.studio.multi_publish_task_types` - (*True*, ``{path_data}`` [4]_) или (*False*, comment)
            * для остальных - (*True*, ``path``) - или (*False*, comment)
            
            .. [4] Структура словаря ``{path_data}`` :
            
                ::
                
                    {
                    'look_path': {
                        branch_name : path,
                        ...
                        },
                    'publish_path': {
                        branch_name : path,
                        ...
                        },
                    }
        """
        pass
        # (1)
        if version_log:
            version = version_log['version']
            branches = version_log['branch']
        elif (version is False or version is None):
            return(False, 'No version specified!')
        else:
            if not branches:
                b, publish_logs = log(self).read_log(action='publish')
                if not b:
                    return(b, publish_logs)
                #
                if not publish_logs[0]:
                    return(False, 'No exists publish version!')
                #
                for log_ in publish_logs[0]:
                    if int(log_['version']) == int(version):
                        branches = log_['branch']
                if not branches:
                    return(False, 'No exists publish version - "%s" !' % version)

        # (2)
        if self.task_type in self.multi_publish_task_types:
            pass
            r_dict = dict()
            #
            b, publish_path = self._template_get_publish_path(self, version=version, branches=branches)
            if not b:
                return(b, publish_path)
            r_dict['publish_path'] = publish_path
            #
            b, look_path = self._template_get_publish_path(self, version=version, branches=branches, look=True)
            if not b:
                return(b, look_path)
            r_dict['look_path'] = look_path
            return(True, r_dict)
        else:
            pass
            b, r = self._template_get_publish_path(self, version)
            if not b:
                return(b, r)
            else:
                if not os.path.exists(r):
                    return(False, 'The path "%s" not exists!' % r)
                else:
                    return(b, r)

    def get_final_publish_file_path(self):
        """Пути к ``top`` версии паблиш файлов (на локальном сервере студии).
        
        Returns
        -------
        tuple
            * для задач с типом из :attr:`edit_db.studio.multi_publish_task_types` - (*True*, ``{path_data}`` [5]_) или (*False*, comment)
            * для остальных - (*True*, ``path``) - или (*False*, comment)
            
            .. [5] Структура словаря ``{path_data}`` :
            
                ::
                
                    {
                    'look_path': {
                        branch_name : path,
                        ...
                        },
                    'publish_path': {
                        branch_name : path,
                        ...
                        },
                    }
        """
        pass
        # 1 - read the final publish log, get final publish version
        # 2 - get template path
        
        # (1)
        b, publish_logs = log(self).read_log(action='publish')
        if not b:
            return(b, publish_logs)
        
        if publish_logs[0]:
            end_log = publish_logs[0][-1:][0]
        else:
            return(False, 'No exists publish version!')
        
        # (2)
        if self.task_type in self.multi_publish_task_types:
            pass
            branches = end_log['branch']
            r_dict = dict()
            #
            b, publish_path = self._template_get_publish_path(self, branches=branches)
            if not b:
                return(b, publish_path)
            r_dict['publish_path'] = publish_path
            #
            b, look_path = self._template_get_publish_path(self, branches=branches, look=True)
            if not b:
                return(b, look_path)
            r_dict['look_path'] = look_path
            #
            return(True, (r_dict, end_log['version']))
        else:
            pass
            b, r = self._template_get_publish_path(self)
            if not b:
                return(b, r)
            else:
                if not os.path.exists(r):
                    return(False, 'The path "%s" not exists!' % r)
                else:
                    return(b, (r, end_log['version']))

    def get_new_publish_file_path(self, republish=False, source_log=False, source_version=False):
        """Пути до файлов новой ``publish`` версии (и ``top``, и версию, на локальном сервере студии). 
        
        Parameters
        ----------
        republish : bool, optional
            Репаблиш или нет.
        source_log : dict, optional
            лог источника для паблиша (``push`` или ``publish``), при наличие этого лога версия ``source_version`` передавать не имеет смысла.
        source_version : int, str, optional
            Версия исходника (``push`` или ``publish``) если *False* - последняя версия.
        
        Returns
        -------
        tuple
            * для задач с типом из :attr:`edit_db.studio.multi_publish_task_types` - (*True*, (``{path_data}`` [6]_, ``new_version``, ``source`` [7]_, ``branches`` [8]_)) или (*False*, comment)
            * для остальных - (*True*, (``{path_data}`` [9]_, ``new_version``, ``source`` [7]_)) или (*False*, comment)
            
            .. [6] Структура словаря ``{path_data}`` :
            
                ::
                
                    {
                    'top_path': {
                        branch_name : path,
                        ...
                        },
                    'top_look_path': {
                        branch_name : path,
                        ...
                        },
                    'version_path': {
                        branch_name : path,
                        ...
                        },
                    'version_look_path': {
                        branch_name : path,
                        ...
                        },
                    'source_path': {
                        branch_name : path,
                        ...
                        },
                    'source_look_path': {
                        branch_name : path,
                        ...
                        },
                    }
            
            
            .. [7] Версия ``push`` или ``publish``, откуда делается паблиш.
            
            .. [8] Список веток которые паблишатся.
            
            .. [9] Структура словаря ``{path_data}`` :
            
                ::
                
                    {
                    'top_path': path,
                    'version_path': path,
                    'source_path': path,
                    }
        """
        pass
        # 1 - read the final publish log, get final publish version
        # 2 - получение branches и путей исходника.
        # 3 - соурс пути
        # 4 - новые пути
        
        # (1)
        old_source = False
        b, publish_logs = log(self).read_log(action='publish')
        if not b:
            return(b, publish_logs)
        
        if publish_logs[0]:
            end_log = publish_logs[0][-1:][0]
            version = int(end_log['version']) + 1
            old_source = int(end_log['source'])
        else:
            version=0
            
        # (2)
        # -- branches - получаем не разделяя тип задачи, он в любом случае будет.
        if source_log:
            branches = source_log['branch']
            source_version = source_log['version']
            if republish:
                source = source_log['source']
            else:
                source = source_log['version']
        else:
            branches = list()
            source = str()
            if republish:
                pass
                if publish_logs[0]:
                    #
                    for log_ in publish_logs[0]:
                        if int(log_['version']) == int(source_version):
                            branches = log_['branch']
                            source = log_['source']
                            #source = source_version
                else:
                    return(False, 'No exists pulish version!')
            else:
                pass
                # -- read push logs
                b, push_logs = log(self).read_log(action='push')
                if not b:
                    return(b, push_logs)
                #
                if push_logs[0]:
                    if not source_version is False and not source_version is None:
                        for log_ in push_logs[0]:
                            if int(log_['version']) == int(source_version):
                                branches = log_['branch']
                                #source = log_['source']
                                source = source_version
                    else:
                        branches = push_logs[0][-1:][0]['branch']
                        source = push_logs[0][-1:][0]['version']
                else:
                    return(False, 'No exists push version!')
            #
            if self.task_type in self.multi_publish_task_types and not branches:
                return(False, 'No exists source (push or pulish version)!')
            if source is False or source is None:
                return(False, 'No exists source (push or pulish version)!')
            
        if not old_source is False and old_source==int(source):
            print('source: %s, old_source: %s' % (str(source), str(old_source)))
            return(False, 'Source of past publishers coincides with new source of publishers!')
            
        # (3)
        source_look_path = False
        source_path = False
        if republish:
            b, source_path = self.get_version_publish_file_path(version=source_version, branches=branches)
            if not b:
                return(b, source_path)
            if self.task_type in self.multi_publish_task_types:
                source_look_path = source_path['look_path']
                source_path = source_path['publish_path']
        else:
            if not source_version is False and not source_version is None:
                b, source_path = self.get_version_push_file_path(source_version)
            else:
                b, source_path = self.get_final_push_file_path()
                source_path = source_path[0]
            if not b:
                return(b, source_path)
            if self.task_type in self.multi_publish_task_types:
                source_look_path = source_path['look_path']
                source_path = source_path['push_path']
        # (4)
        if self.task_type in self.multi_publish_task_types:
            pass
            #
            b, r_top = self._template_get_publish_path(self, branches=branches)
            if not b:
                return(b, r_top)
            #
            b, look_top = self._template_get_publish_path(self, branches=branches, look=True)
            if not b:
                return(b, look_top)
            #
            b, r_version = self._template_get_publish_path(self, version, branches=branches)
            if not b:
                return(b, r_version)
            #
            b, look_version = self._template_get_publish_path(self, version, branches=branches, look=True)
            if not b:
                return(b, look_version)
            #
            return(True, ({'top_path': r_top, 'top_look_path': look_top, 'version_path': r_version, 'version_look_path': look_version, 'source_look_path':source_look_path, 'source_path':source_path}, version, source, branches))
        else:
            pass
            b, r_top = self._template_get_publish_path(self)
            if not b:
                return(b, r_top)
            b, r_version = self._template_get_publish_path(self, version)
            if not b:
                return(b, r_version)
            #
            return(True, ({'top_path': r_top, 'version_path': r_version, 'source_path': source_path}, version, source))

    # old

    # task - должен быть инициализирован
    def get_final_file_path(self, current_artist=False): # УСТАРЕЛО!!!!!!!!!!!!!
        pass
        activity_path = NormPath(os.path.join(self.asset.path, self.activity))
        
        if not os.path.exists(activity_path):
            try:
                os.mkdir(activity_path)
            except:
                print(activity_path)
                return(False, 'in task().get_final_file_path() Can not create activity dir!')
        
        # - get folder list
        folders_16 = os.listdir(activity_path)
        folders = []
        
        if len(folders_16)==0:
            return(True, None, self.asset.path)
        
        # - 16 to 10
        for obj_ in folders_16:
            folders.append(int(obj_, 16))
        
        i = max(folders)
        while i > -1:
            hex_ = hex(i).replace('0x', '')
            num = 4 - len(hex_)
            hex_num = '0'*num + hex_
            
            final_file = NormPath(os.path.join(activity_path, hex_num, '%s%s' % (self.asset.name, self.extension)))
            if os.path.exists(final_file):
                return(True, final_file, self.asset.path)
            i = i-1
        
        return(True, None, self.asset.path)

    # asset - должен быит инициализирован
    # task_data (dict) - требуется если не инициализирован task
    # version (str) - hex 4 символа
    def get_version_file_path(self, version, task_data=False): # УСТАРЕЛО!!!!!!!!!!!!!
        asset_path = self.asset.path
        if not task_data:
            asset_type = self.asset.type
            activity = self.activity
            asset = self.asset.name
            extension = self.extension
        else:
            asset_type = task_data['asset_type']
            activity = task_data['activity']
            asset = task_data['asset_name']
            extension = task_data['extension']
                
        activity_path = NormPath(os.path.join(asset_path, activity))
        
        version_file = NormPath(os.path.join(activity_path, version, '%s%s' % (asset, extension)))
        
        if os.path.exists(version_file):
            return(True, version_file)
        else:
            return(False, 'Not Exists File!')

    # asset - должен быит инициализирован
    # task_data (dict) - требуется если не инициализирован task
    def get_new_file_path(self, task_data=False): # УСТАРЕЛО!!!!!!!!!!!!!
        pass
        if not task_data:
            asset_type = self.asset.type
            activity = self.activity
            asset = self.asset.name
            extension = self.extension
        else:
            asset_type = task_data['asset_type']
            activity = task_data['activity']
            asset = task_data['asset_name']
            extension = task_data['extension']
        # get final file
        result = self.get_final_file_path(task_data)
        #final_file = None
        if not result[0]:
            return(False, result[1])
            
        final_file = result[1]
        asset_path = result[2]
        
        # get activity path
        activity_path = NormPath(os.path.join(asset_path, activity))
        # make activity folder
        if not os.path.exists(activity_path):
            os.mkdir(activity_path)
        
        if final_file == None:
            new_dir_path = NormPath(os.path.join(activity_path, '0000'))
            new_file_path = NormPath(os.path.join(new_dir_path, '%s%s' % (asset, extension)))
            
        else:
            ff_split = final_file.replace('\\','/').split('/')
            new_num_dec = int(ff_split[len(ff_split) - 2], 16) + 1
            new_num_hex = hex(new_num_dec).replace('0x', '')
            if len(new_num_hex)<4:
                for i in range(0, (4 - len(new_num_hex))):
                    new_num_hex = '0' + new_num_hex
            
            new_dir_path = NormPath(os.path.join(activity_path, new_num_hex))
            new_file_path = NormPath(os.path.join(new_dir_path, '%s%s' % (asset, extension)))
        
        return(True, (new_dir_path, new_file_path))

    # asset - должен быит инициализирован
    # activity (str)
    def get_publish_file_path(self, activity): # УСТАРЕЛО!!!!!!!!!!!!!
        pass
        # get task_data
        result = self.get_list(asset_id=self.asset.id)
        if not result[0]:
            return(False, result[1])
            
        task_data = None
        for td in result[1]:
            if td['activity'] == activity:
                task_data = td
                break
                
        if not task_data:
            return(False, 'No Found Task with this activity: "%s"!' % activity)
        
        # -- -- get publish dir
        publish_dir = NormPath(os.path.join(self.asset.path, self.publish_folder_name))
        if not os.path.exists(publish_dir):
            return(False, 'in task.get_publish_file_path() - Not Publish Folder! (%s)' % publish_dir)
        # -- -- get activity_dir
        activity_dir = NormPath(os.path.join(publish_dir, task_data['activity']))
        if not os.path.exists(activity_dir):
            return(False, 'in task.get_publish_file_path() - Not Publish/Activity Folder! (%s)' % activity_dir)
        # -- -- get file_path
        file_path = NormPath(os.path.join(activity_dir, '%s%s' % (self.asset.name, task_data['extension'])))
        if not os.path.exists(file_path):
            print('#'*5, file_path)
            return(False, 'Publish/File Not Found!')
            
        return(True, file_path)

    def _pre_commit(self, work_path, save_path):
        """Вызов одноимённого хука. Вызывается из :func:`edit_db.task.commit`
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        return(True, 'Ok!')

    def _post_commit(self, work_path, save_path):
        """Вызов одноимённого хука. Вызывается из :func:`edit_db.task.commit`
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        return(True, 'Ok!')

    def commit(self, work_path, description, branch=False, artist_ob=False):
        """Запись новой рабочей версии в ``work`` директорию пользователя (:attr:`edit_db.studio.work_folder`).
        
        Parameters
        ----------
        work_path : str
            Путь к текущему рабочему файлу.
        description : str
            Описание.
        branch : str, optional
            Наименование ветки, если не передавать - то будет использован ``master``.
        artist_ob : :obj:`edit_db.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`.
        
        Returns
        -------
        tuple
            (*True*, ``path`` - путь до сохранённого файла) или (*False, comment*)
        """
        pass
        # 0 - input data
        # 1 - get save_path
        # 2 - pre_commit
        # 3 - make dirs
        # 4 - copy file
        # 5 - write log
        # 6 - post_commit
        
        # (0)
        if not description:
            return(False, 'No description!')
        if not branch:
            branch = 'master'
        if not artist_ob:
            artist_ob = artist()
            bool_, r_data = artist_ob.get_user()
            if not bool_:
                return(bool_, r_data)
        
        # (1)
        b, r = self.get_new_work_file_path()
        if not b:
            return(b, r)
        save_path = r[0]
        version = r[1]
        
        # (2)
        b, r = self._pre_commit(work_path, save_path)
        if not b:
            return(b, r)
        
        # (3)
        version_dir_path = os.path.dirname(save_path)
        if not os.path.exists(version_dir_path):
            os.makedirs(version_dir_path)
            
        # (4)
        # (4.1)
        if not os.path.exists(work_path):
            return('The source path "%s" not exists!' % work_path)
        # (4.2)
        try:
            extension = '.%s' % work_path.split('.')[-1:][0]
        except:
            return(False, 'Source file "%s" missing extension' % work_path)
        # (4.3)
        if extension != self.extension:
            return(False, 'Source file extension(%s) does not match task extension(%s)' % (extension, self.extension))
        # (4.4)
        shutil.copyfile(work_path, save_path)
        
        # (5)
        # (5.0)
        commit_time = datetime.datetime.now()
        delta = commit_time - self.open_time
        self.open_time = commit_time
        
        # (5.1)
        delta_seconds = float(delta.total_seconds())
        logs_keys = {
        'action': 'commit',
        'description': description,
        'branch': branch,
        'version': version,
        'time': delta_seconds,
        }
        # (5.2)
        result = log(self).write_log(logs_keys,  artist_ob=artist_ob)
        if not result[0]:
            return(False, result[1])
        # (5.3)
        if not self.time:
            self.time = {artist_ob.nik_name:delta_seconds}
        elif not artist_ob.nik_name in self.time:
            self.time[artist_ob.nik_name] = delta_seconds
        else:
            old_time = self.time[artist_ob.nik_name]
            self.time[artist_ob.nik_name] = old_time + delta_seconds
        b, r = self.changes_without_a_change_of_status('time', self.time)
        if not b:
            return(b, r)
        # (5.4)
        if not self.full_time:
            self.full_time = delta_seconds
        else:
            self.full_time = self.full_time + delta_seconds
        b, r = self.changes_without_a_change_of_status('full_time', self.full_time)
        if not b:
            return(b, r)
        # (5.5)
        b, r = log(self).artist_add_full_time(delta_seconds)
        if not b:
            return(b, r)
        
        # (6)
        b, r = self._post_commit(work_path, save_path)
        if not b:
            return(b, r)
        
        return(True, save_path)

    def run_file(self, path, viewer=False):
        """Запуск файлов редактором или вьювером, создание ``tmp`` копии файла.
        
        Parameters
        ----------
        path : str
            Путь до оригинального файла.
        viewer : bool, optional
            Если *True* - открытие вьювером по оригинальному пути (``tmp`` копии не создаётся).
        
        Returns
        -------
        tuple
            (*True*, ``path`` [10]_) или (*False, comment*)
            
            .. [10] ``path`` - путь до открываемого файла, оригинальный или ``tmp``.
        """
        if viewer:
            soft = {'Linux':'xdg-open',
                'Windows':'explorer',
                'Darwin':'open'}[platform.system()]
            if soft:
                # run from tmp_path
                try:
                    subprocess.run([soft, path])
                except Exception as e:
                    print('*'*5)
                    print(e)
                    try:
                        subprocess.call([soft, path])
                    except Exception as e:
                        return(False, str(e))
                return(True, path)
            else:
                return(False, 'System not defined!')
        else:
            # get soft
            soft = self.soft_data.get(self.extension)
            if not soft:
                return(False, 'No application found for this extension "%s"' % self.extension)
            
            # get tmp_path
            if not os.path.exists(self.tmp_folder):
                return(False, 'Tmp directory is not defined!')
            new_name = '%s_%s%s' % (os.path.basename(path).split('.')[0], uuid.uuid4().hex, self.extension)
            tmp_path = NormPath(os.path.join(self.tmp_folder, new_name))
            
            # copy to tmp_path
            shutil.copyfile(path, tmp_path)
            
            # run from tmp_path
            try:
                subprocess.run([soft, tmp_path])
            except Exception as e:
                print('*'*5)
                print(e)
                try:
                    subprocess.call([soft, tmp_path])
                except Exception as e:
                    return(False, str(e))
            return(True, tmp_path)

    def look(self, action='push', version=False, launch=True):
        """Просмотр какой-либо версии файла для менеджеров (``push``, ``publish`` версии).
        
        .. note:: Если тип задачи из :attr:`edit_db.studio.multi_publish_task_types` (например ``sketch``) то запуска не будет, но будут возвращены пути.
        
        Parameters
        ----------
        action : str, optional
            Экшен из [``push``, ``publish``]
        version : int, str, optional
            Версия, если *False* - то открывается последняя.
        launch : bool, optional
            Если *False* - возвращает только путь, иначе запуск редактором по расширению.
            
        Returns
        -------
        tuple
            Возвращаемые данные аналогичны тому что возвращается при выполнении функций:
            
            * :func:`edit_db.task.get_version_push_file_path`
            * :func:`edit_db.task.get_final_push_file_path`
            * :func:`edit_db.task.get_version_publish_file_path`
            * :func:`edit_db.task.get_final_publish_file_path`
        """
        pass
        # 1 - получение пути / запуск
        # 2 - открытие или возврат пути
        
        # (1)
        if action == 'push':
            pass
            if not version is False:
                b, r = self.get_version_push_file_path(version)
            else:
                b, r = self.get_final_push_file_path()
            if not b:
                return(b, r)
        elif action == 'publish':
            pass
            if not version is False:
                b, r = self.get_version_publish_file_path(version=version)
            else:
                b, r = self.get_final_publish_file_path()
            if not b:
                return(b, r)
        
        # (2)
        if self.task_type in self.multi_publish_task_types or not launch:
            pass
            return(True, r)
        else:
            pass
            if not version is False:
                path = r
            else:
                path = r[0]
            b, r = self.run_file(path)
            if not b:
                return(b, r)
            else:
                return(True, path)

    def open_file(self, look=False, current_artist=False, tasks=False, input_task=False, open_path=False, version=False, launch=True):
        """Откроет файл в приложении - согласно расширению.
        
        .. note:: заполнение: :attr:`edit_db.task.time`, :attr:`edit_db.task.full_time`, ``artist_log.full_time``
        
        Parameters
        ----------
        look : bool, optional
            Если *True* - то статусы меняться не будут, если *False* - то статусы меняться будут.
        current_artist : :obj:`edit_db.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`
        tasks : dict, optional
            Словарь задач данного артиста по именам (результат функции :func:`edit_db.artist.get_working_tasks`). - нужен для случая когда ``look`` = *False*, при отсутствии будет считан - лишнее обращение к БД.
        input_task : :obj:`edit_db.task`, optional
            Входящая задача - для ``open_from_input`` (если передавать - то имеется ввиду открытие из активити входящей задачи).
        open_path : str, optional
            Путь к файлу - указывается для ``open_from_file`` (открытие из указанного файла).
        version : str, int, optional
            Версия рабочего файла активити - если указать то будет открытие рабочего файла этой версии.
        launch : bool, optional
            * Если *True* - то будет произведён запуск приложением, которое установлено в соответствии с данным расширением файла \
            (для универсальной юзерской панели и для менеджерской панели, при открытии на проверку),
            * если *False* - то запуска не будет, но все смены статусов произойдут и будет возвращён путь к файлу - для запуска из плагина.
            
        Returns
        -------
        tuple
            (*True*, ``file_path`` - куда открывается файл) или (*False, coment*).
        """
        pass
        
        # (1) ***** CHANGE STATUS
        if not look:
            if not current_artist:
                current_artist = artist()
                b, r = current_artist.get_user()
                if not b:
                    return(b,r)
            if not tasks:
                b, r = current_artist.get_working_tasks(self.asset.project, statuses = self.working_statuses)
                if not b:
                    return(b,r)
                tasks = r
            if self.status != 'work':
                pass
                # statuses
                change_statuses = [(self, 'work'),]
                for task_name in tasks:
                    if tasks[task_name].status == 'work':
                        change_statuses.append((tasks[task_name], 'pause',))
            
                result = self.change_work_statuses(change_statuses)
                if not result[0]:
                    return(False, result[1])
                else:
                    pass
                
                # readers
                if self.readers:
                    for nik_name in self.readers:
                        if nik_name == 'first_reader':
                            continue
                        else:
                            self.readers[nik_name] = 0
                    
                    # edit db	
                    table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
                    read_ob = self.asset.project
                    update_data = {'readers': self.readers}
                    where = {'task_name': self.task_name}
                    bool_, return_data = database().update('project', read_ob, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
                    if not bool_:
                        return(bool_, return_data)
            # (1.1) time log
            self.open_time = datetime.datetime.now()
            # start
            if not self.start:
                # task.start
                b, r = self.changes_without_a_change_of_status('start', self.open_time)
                if not b:
                    return(b, r)
                self.start = self.open_time
                # artist_log - start
                log(self).artist_start_log(artist_ob=current_artist)
        
        # (2) ope path
        task_ob = self
        if input_task:
            if input_task.extension == self.extension:
                task_ob = input_task
            else:
                return(False, 'Incorrect extension of incoming task!')
        
        if not open_path:
            if version:
                #result = task_ob.get_version_file_path(version)
                b, r = task_ob.get_version_work_file_path(version)
                if not b:
                    return(b, r)
                else:
                    open_path = r
                    #print('*** %s %s' % (version, open_path))
            else:
                #result = task_ob.get_final_file_path()
                b, r = task_ob.get_final_work_file_path()
                if not b:
                    return(b, r)
                else:
                    open_path = r[0]
            #if not result[0]:
                #return(False, result[1])
            #open_path = result[1]
        
            if not open_path:
                '''
                if task_ob.extension in self.NOT_USED_EXTENSIONS:
                    empty_root = os.path.dirname(__file__)
                    open_path = os.path.join(empty_root, 'empty_files', 'empty%s' % task_ob.extension)
                else:
                    return(False, 'No found saved version!')
                '''
                global_empty_path = NormPath(os.path.join(os.path.dirname(__file__), self.EMPTY_FILES_DIR_NAME, 'empty%s' % task_ob.extension))
                user_empty_path = NormPath(os.path.join(os.path.expanduser('~'), self.init_folder, self.EMPTY_FILES_DIR_NAME, 'empty%s' % task_ob.extension))
                print('*'*5, global_empty_path, os.path.exists(global_empty_path))
                print('*'*5, user_empty_path, os.path.exists(user_empty_path))
                #
                for path in [user_empty_path, global_empty_path]:
                    if not os.path.exists(path):
                        continue
                    else:
                        open_path = path
                        break
                #
                if not open_path:
                    return(False, 'No found saved version!')
                    
        # get tmp_file_path
        tmp_file_name = '%s_%s%s' % (task_ob.task_name.replace(':','_', 2), hex(random.randint(0, 1000000000)).replace('0x', ''), task_ob.extension)
        tmp_file_path = os.path.join(self.tmp_folder, tmp_file_name)
        # copy file to tmp
        #print(open_path)
        #print(tmp_file_path)
        #return(True, 'Ok')
        shutil.copyfile(open_path, tmp_file_path)
        
        # (3) open file
        if launch:
            soft = self.soft_data.get(task_ob.extension)
            if not soft:
                return(False, 'No application found for this extension "%s"' % task_ob.extension)
            cmd = '"%s" "%s"' % (soft, tmp_file_path)
            subprocess.Popen(cmd, shell = True)
            
        return(True, tmp_file_path)

    def _pre_push(self):
        """Вызов одноимённого хука. Вызывается из :func:`edit_db.task.push`
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        return(True, 'Ok!')

    def _post_push(self):
        """Вызов одноимённого хука. Вызывается из :func:`edit_db.task.push`
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        return(True, 'Ok!')

    def push(self, description, version=False, current_artist=False):
        """Создание новой ``push`` версии на сервере студии, или выгрузка архива в облако для создания ``push`` версии на сервере студии (для аутсорса).
        
        .. Attention:: Для аутсорса пока не сделано, только для работников студии.
        
        Parameters
        ----------
        description : str
            Краткое описание.
        version : str, int, optional
            ``work`` версия из которой делается ``push``, не имеет смысла для задач с типом из :attr:`edit_db.studio.multi_publish_task_types`, там только из последней версии.
        current_artist : :obj:`edit_db.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`
            
        Returns
        -------
        tuple
            (*True, message*) или (*False, comment*)
        """
        pass
        # 0 - input data
        # 0.1 - получение путей 
        # 1 - studio
        # 2 - sketch
        # 2.0 - создание директории версии
        # 2.1 - копирование файлов
        # 2.2 - лук версия
        # 2.3 - запись лога
        # 3 - не sketch
        # 4 - аутсорс
        # 5 - sketch
        # 6 - не sketch
        
        # (0)
        if not description:
            return(False, 'Missing description!')
        if not current_artist:
            current_artist = artist()
            b, r = current_artist.get_user()
            if not b:
                return(b,r)
        # (0.1)
        b, r = self.get_new_push_file_path(version=version, current_artist=current_artist)
        if not b:
            return(b, r)
        #
        #for k in r[0]:
            #print('*** %s - %s' % (k, str(r[0][k])))
        #print(r[1])
        
        # (1)
        b,r_data = self._pre_push()
        if not b:
            return(b, r_data)
        
        if not current_artist.outsource:
            # (2)
            if self.task_type in self.multi_publish_task_types:
                pass
                branches = list()
                source_versions = list()
                new_version = r[1]
                for branch in r[0]['source_path']:
                    pass
                    # (2.0)
                    source_path = r[0]['source_path'][branch]
                    push_path = r[0]['push_path'][branch]
                    look_path = r[0]['look_path'][branch]
                    version_dir_path = os.path.dirname(push_path)
                    #print(version_dir_path)
                    if not os.path.exists(version_dir_path):
                        os.makedirs(version_dir_path)
                    # (2.1)
                    shutil.copyfile(source_path, push_path)
                    # (2.2)
                    cmd = '%s %s %s' % (os.path.normpath(self.convert_exe), push_path, look_path)
                    cmd2 = '\"%s\" \"%s\" \"%s\"' % (os.path.normpath(self.convert_exe), push_path, look_path)
                    try:
                        os.system(cmd)
                    except Exception as e:
                        print(e)
                        try:
                            os.system(cmd2)
                        except Exception as e:
                            print(e)
                    branches.append(branch)
                    source_versions.append(r[0]['source_versions'][branch])
                # (2.3)
                log_data = dict()
                log_data['branch'] = branches
                log_data['source'] = source_versions
                log_data['action'] = 'push'
                log_data['description'] = description
                log_data['version'] = r[1]
                b, r = log(self).write_log(log_data, artist_ob=current_artist)
                if not b:
                    return(b,r)
            # (3)
            else:
                pass
                # (3.0)
                source_path = r[0]
                source_version = r[1]
                source_branch = r[2]
                push_path = r[3]
                new_version = r[4]
                #return(False, 'source - %s\npush - %s' % (source_path, push_path))
                version_dir_path = os.path.dirname(push_path)
                if not os.path.exists(version_dir_path):
                    os.makedirs(version_dir_path)
                # (3.1)
                shutil.copyfile(source_path, push_path)
                # (3.3)
                log_data = dict()
                log_data['branch'] = source_branch
                log_data['source'] = source_version
                log_data['action'] = 'push'
                log_data['description'] = description
                log_data['version'] = new_version
                b, r = log(self).write_log(log_data, artist_ob=current_artist)
                if not b:
                    return(b,r)
                
        # (4)
        else:
            # (5)
            if self.task_type in self.multi_publish_task_types:
                pass
            # (6)
            else:
                pass
            
        b,r_data = self._post_push()
        if not b:
            return(b, r_data)
        
        return(True, 'Created a new Push version with number: %s' % new_version)

    def _pre_publish(self):
        """Вызов одноимённого хука. Вызывается из :func:`edit_db.task.publish_task`
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        return(True, 'Ok!')

    def _post_publish(self):
        """Вызов одноимённого хука. Вызывается из :func:`edit_db.task.publish_task`
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        return(True, 'Ok!')

    def publish_task(self, description=False, republish=False, source_version=False, source_log=False, current_artist=False):
        """Перекладывание паблиш версии файлов (в том числе ``top`` версии), запись лога.
        
        Parameters
        ----------
        description : str, optional
            Краткое описание, не обязательный параметр, при отсутствии составляется автоматически - техническое описание: что, откуда, куда.
        republish : bool, optional
            Если *True* - то делается *репаблиш*, а именно перезапись в финал и в ``top``, какой-либо указанной *паблиш* версии.
        source_version : str, int, optional
            Версия ``push`` или ``publish`` (при *репаблише*), если *False* при *паблише* - то *паблиш* из последней *пуш* версии.
        source_log : dict, optional
            Лог версии источника, при его наличии ``source_version`` не имеет смысла.
        current_artist : :obj:`edit_db.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`
            
        Returns
        -------
        tuple
            (*True, message*) или (*False, comment*).
        """
        pass
        # 0 - input data
        # 1 - получение путей
        # 1.1 - сосотавление description
        # 2 - pre_publish
        # 3 - publish
        # 3.1 - удаление прошлой top версии
        # 3.2 - копирование файлов
        # 3,3 - запись лога
        # 4 - post_publish
        
        # (0)
        # (0.1)
        if not current_artist:
            current_artist = artist()
            b, r = current_artist.get_user()
            if not b:
                return(b,r)
        # (0.2)
        if current_artist.outsource:
            return(False, 'This procedure is not performed on outsourcing!')
        
        # (1)
        b, r = self.get_new_publish_file_path(republish=republish, source_version=source_version, source_log=source_log)
        if not b:
            return(b, r)
        
        #for i in r:
            #print(i)
            
        # (1.1)
        if not description:
            if republish:
                description = 'republish from %s' % str(r[2])
            else:
                description = 'publish from %s' % str(r[2])
        
        print(description)
        
        # --
        pass
        
        # (2)
        b, r_data = self._pre_publish()
        if not b:
            return(b, r_data)
        
        # (3)
        # (3.1)
        pass
        if self.task_type in self.multi_publish_task_types:
            publish_dir = os.path.dirname(r[0]['top_path'][r[0]['top_path'].keys()[0]])
        else:
            publish_dir = os.path.dirname(r[0]['top_path'])
        #
        if os.path.exists(publish_dir):
            for name in os.listdir(publish_dir):
                path_file = os.path.join(publish_dir, name)
                if os.path.isfile(path_file):
                    os.remove(path_file)
        
        # (3.2)
        # -- mk dir
        if self.task_type in self.multi_publish_task_types:
            version_dir = os.path.dirname(r[0]['version_path'][r[0]['version_path'].keys()[0]])
        else:
            version_dir = os.path.dirname(r[0]['version_path'])
        if not os.path.exists(version_dir):
            os.makedirs(version_dir)
        # -- copy files
        if self.task_type in self.multi_publish_task_types:
            for branch in r[0]['source_path']:
                shutil.copyfile(r[0]['source_path'][branch], r[0]['top_path'][branch])
                shutil.copyfile(r[0]['source_path'][branch], r[0]['version_path'][branch])
                shutil.copyfile(r[0]['source_look_path'][branch], r[0]['top_look_path'][branch])
                shutil.copyfile(r[0]['source_look_path'][branch], r[0]['version_look_path'][branch])
        else:
            #print(r[0])
            #return(0,'epte!')
            shutil.copyfile(r[0]['source_path'], r[0]['top_path'])
            shutil.copyfile(r[0]['source_path'], r[0]['version_path'])
            
        # (3.3)
        # -- write log
        new_log_keys = dict()
        new_log_keys['action'] = 'publish'
        new_log_keys['version'] = r[1]
        new_log_keys['description']=description
        if self.task_type in self.multi_publish_task_types:
            new_log_keys['branch']=r[3]
        new_log_keys['source']=r[2]
        #print(new_log_keys)
        
        b, r_data = log(self).write_log(new_log_keys, artist_ob=current_artist)
        if not b:
            return(b, r_data)
        
        # (4)
        b, r_data = self._post_publish()
        if not b:
            return(b, r_data)
        
        return(True, 'Created a new Publish version with number: %s' % r[1])
        
    # локальная запись новой рабочей версии файла
    # description (str) - комментарий к версии
    # current_file (unicode/str) - текущее местоположение рабочего файла (как правило в темп)
    # current_artist (artist) - если не передавать, то будет выполняться get_user() - лишнее обращение к БД.
    # return(True, new_file_path) или (False, comment)
    def push_file(self, description, current_file, current_artist=False): # УСТАРЕЛО!!!!!!!!!!!!! 
        pass
        
        # (1) test data
        if not current_artist:
            current_artist = artist()
            b, r = current_artist.get_user()
            if not b:
                return(b,r)
        # -- 
        if not os.path.exists(current_file):
            return(False, 'Current file not found: %s' % current_file)
        
        #return(False, current_file)

        # (2) COPY to ACtTIVITY
        result = self.get_new_file_path()
        if not result[0]:
            return(False, result[1])
        
        new_dir_path, new_file_path = result[1]
        
        # -- make version folder
        if not os.path.exists(new_dir_path):
            os.mkdir(new_dir_path)
        
        # copy file
        shutil.copyfile(current_file, new_file_path)
        
        #print('#'*25, new_file_path)
        
        # (3) ****** LOG
        logs_keys = {
        'action': 'push',
        'description': description,
        'version': os.path.basename(new_dir_path),
        }
        
        #print(logs_keys, current_artist.nik_name)
        
        result = log(self).write_log(logs_keys, current_artist)
        if not result[0]:
            return(False, result[1])
        
        #print('%'*25)
        
        return(True, new_file_path)
        

    # **************************** CACHE  ( file path ) ****************************
    def get_versions_list_of_cache_by_object(self, ob_name, activity = 'cache', extension = '.pc2', task_data=False): # v2 *** без тестов
        """Список версий кеша для *меш* объекта.
        
        Parameters
        ----------
        ob_name : str
            Имя 3d объекта.
        activity : str, optional
            По умолчанию ``'cache'`` (для *blender*) - для других программ может быть другим, например ``'maya_cache'``.
        extension : str, optional
            Расширение файла кеша.
        task_data : dict
            Не использовать. Работа с текущим объектом.
            
        Returns
        -------
        tuple
            (*True*, ``cache_versions_list`` [11]_) или (*False, comment*)
            
            .. [11] Структура ``cache_versions_list`` (список кортежей):
            
                ::
                
                    [
                        (num_version '''str''', ob_name,  path),
                        ...
                    ]
        """
        pass
        # 1 - получение task_data
        # (1)
        if not task_data:
            task_data={}
            for key in self.tasks_keys:
                exec('task_data["%s"] = self.%s' % (key, key))
        
        asset_path = task_data['asset_path']
        
        folder_name = activity
        activity_path = NormPath(os.path.join(asset_path, folder_name))
        activity_path = NormPath(activity_path)
        cache_dir_path = NormPath(os.path.join(asset_path, folder_name, ob_name))
        
        if not os.path.exists(cache_dir_path):
            return(False, 'No Found Cache Directory!')
            
        # - get folders list
        folders_16 = os.listdir(cache_dir_path)
        dec_nums = []
        tech_anim_cache_versions_list = []
        
        if not folders_16:
            return(False, 'No Found Cache Versions!')
            
        for num in folders_16:
            dec_nums.append(int(num, 16))
            
        dec_nums.sort()
        
        for i in dec_nums:
            number = None
            for num in folders_16:
                if i == int(num, 16):
                    number = num
                    break
            path = os.path.join(cache_dir_path, number, (ob_name + extension))
            path = NormPath(path)
            if number:
                if os.path.exists(path):
                    tech_anim_cache_versions_list.append((str(i), ob_name, path))
                else:
                    continue
                
        if tech_anim_cache_versions_list:
            return(True, tech_anim_cache_versions_list)
        else:
            return(False, 'No Found Cache Versions! *')

    def get_final_cache_file_path(self, cache_dir_name, activity = 'cache', extension = '.pc2', task_data=False): # v2 *** без тестов
        """Путь к последней версии кеша для меш объекта.
        
        Parameters
        ----------
        cache_dir_name : str
            Имя директории состоиит из имени ассета и имени меш объекта, через нижнее подчёркивание: ``asset_name`` + ``'_'`` + ``ob_name``.
        activity : str, optional
            По умолчанию ``'cache'`` (для *blender*) - для других программ может быть другим, например ``'maya_cache'``.
        extension : str, optional
            Расширение файла кеша.
        task_data : dict
            Не использовать. Работа с текущим объектом.
            
        Returns
        -------
        tuple
            (*True*, ``path``) или (*False, comment*)
        """
        pass
        # 1 - получение task_data
        # (1)
        if not task_data:
            task_data={}
            for key in self.tasks_keys:
                exec('task_data["%s"] = self.%s' % (key, key))
        
        asset_path = task_data['asset_path']
        
        folder_name = activity
        activity_path = NormPath(os.path.join(asset_path, folder_name))
        activity_path = NormPath(activity_path)
        cache_dir_path = NormPath(os.path.join(asset_path, folder_name, cache_dir_name))
        cache_dir_path = NormPath(cache_dir_path)
        
        #print(cache_dir_path)
        
        if not os.path.exists(activity_path):
            os.mkdir(activity_path)
        if not os.path.exists(cache_dir_path):
            os.mkdir(cache_dir_path)
        
        # - get folder list
        folders_16 = os.listdir(cache_dir_path)
        folders = []
        
        if len(folders_16)==0:
            return(False, 'No Found Chache! *1')
        
        # - 16 to 10
        for obj_ in folders_16:
            folders.append(int(obj_, 16))
        
        i = max(folders)
        while i > -1:
            hex_ = hex(i).replace('0x', '')
            num = 4 - len(hex_)
            hex_num = '0'*num + hex_
            
            final_file = NormPath(os.path.join(cache_dir_path, hex_num, (cache_dir_name + extension)))
            if os.path.exists(final_file):
                return(True, final_file)
            i = i-1
        
        return(False, 'No Found Chache! *2')

    def get_new_cache_file_path(self, cache_dir_name, activity = 'cache', extension = '.pc2', task_data=False): # v2 *** без тестов
        """Путь к новой версии кеша для меш объекта.
        
        Parameters
        ----------
        cache_dir_name : str
            Имя директории состоиит из имени ассета и имени меш объекта, через нижнее подчёркивание: ``asset_name`` + ``'_'`` + ``ob_name``.
        activity : str, optional
            По умолчанию ``'cache'`` (для *blender*) - для других программ может быть другим, например ``'maya_cache'``.
        extension : str, optional
            Расширение файла кеша.
        task_data : dict
            Не использовать. Работа с текущим объектом.
            
        Returns
        -------
        tuple
            (*True*, (``new_dir_path``, ``new_file_path``)) или (*False, comment*)
        """
        pass
        # 1 - получение task_data
        # (1)
        if not task_data:
            task_data={}
            for key in self.tasks_keys:
                exec('task_data["%s"] = self.%s' % (key, key))
        
        # get final file
        result = self.get_final_cache_file_path(cache_dir_name, activity = activity, extension = extension, task_data=task_data)
        #final_file = None
        if not result[0]:
            if result[1] == 'No Found Chache! *1' or result[1] == 'No Found Chache! *2':
                final_file = None
            else:
                return(False, result[1])
        else:
            final_file = result[1]
        asset_path = task_data['asset_path']
        
        # get activity path
        folder_name = activity
        activity_path = NormPath(os.path.join(asset_path, folder_name, cache_dir_name))
        
        # make activity folder
        if not os.path.exists(activity_path):
            os.mkdir(activity_path)
        
        if final_file == None:
            new_dir_path = NormPath(os.path.join(activity_path, '0000'))
            new_file_path = NormPath(os.path.join(new_dir_path, (cache_dir_name + extension)))
            
        else:
            ff_split = final_file.replace('\\','/').split('/')
            new_num_dec = int(ff_split[len(ff_split) - 2], 16) + 1
            new_num_hex = hex(new_num_dec).replace('0x', '')
            if len(new_num_hex)<4:
                for i in range(0, (4 - len(new_num_hex))):
                    new_num_hex = '0' + new_num_hex
            
            new_dir_path = NormPath(os.path.join(activity_path, new_num_hex))
            new_file_path = NormPath(os.path.join(new_dir_path, (cache_dir_name + extension)))
        
        
        # make version dir
        if not os.path.exists(new_dir_path):
            os.mkdir(new_dir_path)
        
                    
        return(True, (new_dir_path, new_file_path))

    def get_version_cache_file_path(self, version, cache_dir_name, activity = 'cache', extension = '.pc2', task_data=False): # v2 *** без тестов
        """Путь к определённой версии файла кеша меш объекта.
        
        Parameters
        ----------
        version : str
            Версия ``hex`` 4 символа ``?``.
        cache_dir_name : str
            Имя директории состоиит из имени ассета и имени меш объекта, через нижнее подчёркивание: ``asset_name`` + ``'_'`` + ``ob_name``.
        activity : str, optional
            По умолчанию ``'cache'`` (для *blender*) - для других программ может быть другим, например ``'maya_cache'``.
        extension : str, optional
            Расширение файла кеша.
        task_data : dict
            Не использовать. Работа с текущим объектом.
            
        Returns
        -------
        tuple
            (*True*, ``path``) или (*False, comment*)
        """
        pass
        # 1 - получение task_data
        # (1)
        if not task_data:
            task_data={}
            for key in self.tasks_keys:
                exec('task_data["%s"] = self.%s' % (key, key))
        
        asset_path = task_data['asset_path']
        
        folder_name = activity
        activity_path = NormPath(os.path.join(asset_path, folder_name, cache_dir_name))
        
        version_file = NormPath(os.path.join(activity_path, version, (cache_dir_name + extension)))
        
        if os.path.exists(version_file):
            return(True, version_file)
        else:
            return(False, 'Not Exists File!')
        
    # ************************ CHANGE STATUS ******************************** end
        
    def add_task(self, project_name, task_key_data): # УСТАРЕЛО!!!!!!!!!!!!! 
        pass
        # other errors test
        result = self.get_project(project_name)
        if not result[0]:
            return(False, result[1])
            
        # test exists ASSET  self.assets_list
        asset_name = task_key_data['asset']
        if not asset_name in self.assets_list:
            # self.print_log('')
            return False, 'not_asset'
            
        # test required parameters
        for i in range(0, 3):
            try:
                data = task_key_data[self.tasks_keys[i][0]]
            except:
                return False, 'required'
        #########		
        # get Autsource status
        # -- get artist
        outsource = None
        artist_name = task_key_data['artist']
        if artist_name:
            artist_data = artist().read_artist({'nik_name':artist_name})
            if artist_data[0]:
                if artist_data[1][0]['outsource'] == '1':
                    outsource = True
        #########
                
        # set STATUS
        try:
            if task_key_data['input'] == '':
                ######
                if outsource:
                    task_key_data['status'] = "ready_to_send"
                else:
                    task_key_data['status'] = "ready"
                ######
            else:
                input_task_data = self._read_task(project_name, task_key_data['input'], ('status',))
                if input_task_data[0]:
                    if input_task_data[1]['status'] == 'done':
                        ######
                        if outsource:
                            task_key_data['status'] = "ready_to_send"
                        else:
                            task_key_data['status'] = "ready"
                        ######
                    else:
                        task_key_data['status'] = "null"
                else:
                    #'not_task_name'
                    task_key_data['status'] = "null"
        except:
            ######
            if outsource:
                task_key_data['status'] = "ready_to_send"
            else:
                task_key_data['status'] = "ready"
            ######
                
        #
        table = '\"' + asset_name + ':' + self.tasks_t + '\"'
        string = "insert into " + table + " values"
        values = '('
        data = []
        for i, key in enumerate(self.tasks_keys):
            if i< (len(self.tasks_keys) - 1):
                values = values + '?, '
            else:
                values = values + '?'
            if key[0] in task_key_data:
                data.append(task_key_data[key[0]])
            else:
                if key[1] == 'real':
                    data.append(0.0)
                elif key[1] == 'timestamp':
                    data.append(None)
                else:
                    data.append('')
                    
        values = values + ')'
        data = tuple(data)
        string = string + values
        
        # write task to db
        conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # exists table
        try:
            str_ = 'select * from ' + table
            c.execute(str_)
            # unicum task_name test
            r = c.fetchall()
            for row in r:
                if row['task_name'] == task_key_data['task_name']:
                    conn.close()
                    return False, 'overlap'
        except:
            string2 = "CREATE TABLE " + table + " ("
            for i,key in enumerate(self.tasks_keys):
                if i == 0:
                    string2 = string2 + key[0] + ' ' + key[1]
                else:
                    string2 = string2 + ', ' + key[0] + ' ' + key[1]
            string2 = string2 + ')'
            #print(string2)
            c.execute(string2)
        
        # add task
        c.execute(string, data)
        conn.commit()
        conn.close()
        return True, 'ok'

    def edit_task(self, project_name, task_key_data): # УСТАРЕЛО!!!!!!!!!!!!! 
        pass
        # other errors test
        result = self.get_project(project_name)
        if not result[0]:
            return(False, result[1])
            
        # test exists ASSET  asset
        asset_name = task_key_data['task_name'].split(':')[0]
        if not asset_name in self.assets_list:
            # self.print_log('')
            return False, 'not_asset'
        
        # test task_name
        try:
            task_name = (task_key_data['task_name'],)
        except:
            return False, 'not task_name'
            
        ######     ==  COONNECT DATA BASE
        conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        table = '\"' + asset_name + ':' + self.tasks_t + '\"'
            
        ######     == get current data
        command =  'SELECT * FROM ' + table + ' WHERE task_name = ?'
        c.execute(command, task_name)
        current_task_data = c.fetchone()
        #print('***** current name: ', current_task_data['artist'], 'new name:', task_key_data['artist'])
        
        #conn.close()
        #return
        ######
            
        #########	 == get Autsource Status	
        # -- get artist
        outsource = None
        artist_name = None
        try:
            artist_name = task_key_data['artist']
        except:
            artist_name = current_task_data['artist']
        if artist_name:
            artist_data = artist().read_artist({'nik_name':artist_name})
            if artist_data[0]:
                if artist_data[1][0]['outsource'] == 1:
                    outsource = True
        #########
        
        #########   == get Input Status
        input_status = None
        input_task_name = ''
        try:
            input_task_name = task_key_data['input']
        except:
            input_task_name = current_task_data['input']
        input_task_data = self._read_task(project_name, input_task_name, ['status'])
        if input_task_data[0]:
            input_status = input_task_data[1]['status']
        elif not input_task_data[0] and input_task_data[1] == 'not_task_name':
            input_status = 'done'
            
        
        ######### self.working_statuses self.end_statuses
        
        # CHANGE STATUS
        try:
            task_key_data['status']
        except:
            pass
        else:
            if not (input_status in self.end_statuses):
                task_key_data['status'] = "null"
            elif task_key_data['status'] == "ready" and outsource:
                task_key_data['status'] = "ready_to_send"
            elif task_key_data['status'] == "work" and outsource:
                task_key_data['status'] = "work_to_outsorce"
            elif task_key_data['status'] == "work_to_outsorce" and not outsource:
                task_key_data['status'] = "work"
            elif task_key_data['status'] == "null" and (input_status in self.end_statuses) and outsource:
                task_key_data['status'] = "ready_to_send"
            elif task_key_data['status'] == "null" and (input_status in self.end_statuses) and (not outsource):
                task_key_data['status'] = "ready"
            # SET OUTPUT STATUS
            elif task_key_data['status'] in self.end_statuses:
                #print('w'*25, task_key_data['status'])
                self.edit_status_to_output(project_name, task_key_data['task_name'])
            
            if (current_task_data['status'] in self.end_statuses) and (task_key_data['status'] not in self.end_statuses):
                self.edit_status_to_output(project_name, task_key_data['task_name'], new_status = task_key_data['status'])
            
        # write task to db
        '''
        conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        c = conn.cursor()
        table = '\"' + asset_name + ':' + self.tasks_t + '\"'
        '''
        # edit db
        data_from_input_task = (False,)
        string = 'UPDATE ' +  table + ' SET '
        for key in task_key_data:
            if not key == 'task_name' or key == 'asset' or key == 'sctivity':
                if key == 'price':
                    string = string + ' ' + key + ' = ' + str(task_key_data[key]) + ','
                else:
                    if task_key_data[key] == None:
                        string = string + ' ' + key + ' = null,'
                    else:
                        string = string + ' ' + key + ' = \"' + task_key_data[key] + '\",'
                '''
                elif key == 'status' and task_key_data['status'] == 'done':
                    ######
                    continue
                    self.edit_status_to_output(project_name, task_key_data['task_name'])
                    string = string + ' ' + key + ' = \"' + task_key_data[key] + '\",'
                elif key == 'input':
                    ######
                    continue
                    data_from_input_task = self._read_task(project_name, task_key_data['input'], ('status',))
                    string = string + ' ' + key + ' = \"' + task_key_data[key] + '\",'
                
                else:
                    if task_key_data[key] == None:
                        string = string + ' ' + key + ' = null,'
                    else:
                        string = string + ' ' + key + ' = \"' + task_key_data[key] + '\",'
                '''		
        ######   == exchange key 'status'	from exchange input task
        '''
        if data_from_input_task[0]:
            if (data_from_input_task[1]['status'] == 'done') and (this_status == 'null'):
                string = string + ' status = \"ready\",'
            elif data_from_input_task[1]['status'] != 'done':
                string = string + ' status = \"null\",'
        '''
        ######
        
        # -- >>
        string = string + ' WHERE task_name = \"' + task_key_data['task_name'] + '\"'
        string = string.replace(', WHERE', ' WHERE')
        #print(string)
        
        c.execute(string)
        conn.commit()
        conn.close()
        
        return(True, 'ok')

    def edit_status_to_output(self, project_name, task_name, new_status = None): # УСТАРЕЛО!!!!!!!!!!!!! 
        asset_name = task_name.split(':')[0]
        table = '\"' + asset_name + ':' + self.tasks_t + '\"'
        data = (task_name,)
        string = 'SELECT * FROM ' + table + ' WHERE input = ?'
        
        try:
            conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        except:
            return(False, 'studio.project.asset.task.edit_status_to_output() -> the database can not be read!')
                
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute(string, data)
        rows = c.fetchall()
        
        for row in rows:
            #print row['task_name']
            # get artist_status
            '''
            if int(artist().read_artist({'nik_name':row['artist']})[1][0]['outsource']):
                print '###########################################', row['artist']
            '''
            if not new_status:
                if row['status'] == 'null':
                    if artist().read_artist({'nik_name':row['artist']})[1][0]['outsource'] == 1:
                        string2 = 'UPDATE ' +  table + ' SET status = \"ready_to_send\" WHERE task_name = \"' + row['task_name'] + '\"'
                    else:	
                        string2 = 'UPDATE ' +  table + ' SET status = \"ready\" WHERE task_name = \"' + row['task_name'] + '\"'
                    c.execute(string2)
            elif new_status not in self.end_statuses and row['status'] != 'close':
                string2 = 'UPDATE ' +  table + ' SET status = \"null\" WHERE task_name = \"' + row['task_name'] + '\"'
                c.execute(string2)
            
        conn.commit()
        conn.close()
        
        return True, 'ok'
    '''
    def _read_task(self, project_name, task_name, keys):
        if keys == 'all':
            new_keys = []
            for key in self.tasks_keys:
                new_keys.append(key[0])
            keys = new_keys
            
        # other errors test
        result = self.get_project(project_name)
        if not result[0]:
            return(False, result[1])
        
        # read tasks
        conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        asset_name = task_name.split(':')[0]
        table = '\"' + asset_name + ':' + self.tasks_t + '\"'
        string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
        
        try:
            c.execute(string)
            row = c.fetchone()
        except:
            conn.close()
            #return(False, ('can_not_read_asset', string))
            return(False, string)
        conn.close()
        
        if not row:
            return(False, 'not_task_name')
                
        data = {}
        for key in keys:
            data[key] = row[key]
            
        return(True, data)
    '''
        
    '''	
    def change_status_by_open_task(self, project_name, task_name, artist):
        self.edit_task(self, project_name, {'task_name': task_name, 'status': 'work'})
    '''


    # **************** Task NEW  METODS ******************

    def create_tasks_from_list(self, list_of_tasks): #v2
        """Создание задач ассета по списку.
        
        Parameters
        ----------
        list_of_tasks : list
            Список задач (словари по :attr:`edit_db.studio.tasks_keys`, обязательные параметры: ``task_name``)
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        asset_name = self.asset.name #asset_data['name']
        asset_id = self.asset.id #asset_data['id']
        #asset_path = self.asset.path #asset_data['path']
        
        # 1-создаём таблицу если нет
        # 2-читаем список имён существующих задач в exists_tasks
        # 3-пробегаем по списку list_of_tasks - если есть имена из exists_tasks - записываем их в conflicting_names
        # --3.1 если conflicting_names не пустой - то (return False, 'Matching names, look at the terminal!'); print(conflicting_names)
        # --3.2 если task_name или activity вообще остутсвуют - ошибка
        # 4-создаём задачи
        # --4.1 заполняем недостающие поля: outsource=0, priority
        # --4.2 запись базы данных.
        
        table_name = '"%s:%s"' % ( asset_id, self.tasks_t)
        # 1
        bool_, return_data = database().create_table('project', self.asset.project, table_name, self.tasks_keys, table_root = self.tasks_db)
        if not bool_:
            return(bool_, return_data)
        # 2
        exists_tasks = []
        bool_, return_data = database().read('project', self.asset.project, table_name, self.tasks_keys, table_root=self.tasks_db)
        if not bool_:
            return(bool_, return_data)
        for task_ in return_data:
            exists_tasks.append(task_['task_name'])
        # 3
        conflicting_names = []
        for task_ in list_of_tasks:
            if task_.get('task_name') in exists_tasks:
                conflicting_names.append(task_['task_name'])
            # 3.2
            elif not task_.get('task_name'):
                print('#'*5, task_)
                return(False, 'in create_tasks_from_list() \n The task does not specify the "name"! Look the terminal')
            elif not task_.get('activity') and task_.get('task_type') != 'service':
                print('#'*5, task_)
                return(False, 'in create_tasks_from_list() \n The task does not specify the "activity"! Look the terminal')
        # 3.1
        if conflicting_names:
            print('#'*5, 'in create_tasks_from_list()')
            print('#'*5, 'Matching names: ', conflicting_names)
            return(False, 'in create_tasks_from_list() \n Matching names found! Look the terminal')
        
        # 4
        for task_keys in list_of_tasks:
            # 4.1
            if not task_keys.get('priority'):
                if not self.asset.priority:
                    task_keys['priority'] = 0
                else:
                    task_keys['priority'] = self.asset.priority
            task_keys['outsource'] = 0
            # 4.2
            bool_, return_data = database().insert('project', self.asset.project, table_name, self.tasks_keys, task_keys, table_root=self.tasks_db)
            if not bool_:
                return(bool_, return_data)
        '''
        # Other errors test
        result = self.get_project(project_name)
        if not result[0]:
            return(False, result[1])
            
        # Connect to db
        conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Exists table
        table = '\"' + asset_id + ':' + self.tasks_t + '\"'
        try:
            str_ = 'select * from ' + table
            c.execute(str_)
            
        except:
            string2 = "CREATE TABLE " + table + " ("
            for i,key in enumerate(self.tasks_keys):
                if i == 0:
                    string2 = string2 + key[0] + ' ' + key[1]
                else:
                    string2 = string2 + ', ' + key[0] + ' ' + key[1]
            string2 = string2 + ')'
            #print(string2)
            c.execute(string2)
            
        # Get exists_tasks
        exists_tasks = []
        str_ = 'select * from ' + table
        c.execute(str_)
        for row in c.fetchall():
            exists_tasks.append(row['task_name'])
        
        # Crete Tasks
        for task_keys in list_of_tasks:
            # ***************** tests *************
            try:
                if not task_keys['asset']:
                    task_keys['asset'] = asset_name
                if not task_keys['asset_id']:
                    task_keys['asset_id'] = asset_id
                if not task_keys['asset_path']:
                    task_keys['asset_path'] = asset_path
            except:
                task_keys['asset'] = asset_name
                task_keys['asset_id'] = asset_id
                task_keys['asset_path'] = asset_path
                
            # task autsource
            task_keys['outsource'] = '0'
                
            # test task['Task_Name']
            try:
                if not task_keys['task_name']:
                    conn.close()
                    return(False, 'Not Task_Name!')
                else:
                    if task_keys['task_name'] in exists_tasks:
                        conn.close()
                        return(False, (task_keys['task_name'] + ' already exists!'))
            except:
                conn.close()
                return(False, 'Not Task_Name!')
                
            # test task['Activity']
            if task_keys['task_type'] != 'service':
                try:
                    if not task_keys['activity']:
                        conn.close()
                        return(False, 'activity!')
                except:
                    conn.close()
                    return(False, 'activity!')
            
            # ***************** tests end *************
            
            #
            string = "insert into " + table + " values"
            values = '('
            data = []
            for i, key in enumerate(self.tasks_keys):
                if i< (len(self.tasks_keys) - 1):
                    values = values + '?, '
                else:
                    values = values + '?'
                if key[0] in task_keys:
                    data.append(task_keys[key[0]])
                else:
                    if key[1] == 'real':
                        data.append(0.0)
                    elif key[1] == 'timestamp':
                        data.append(None)
                    else:
                        data.append('')
                        
            values = values + ')'
            data = tuple(data)
            string = string + values
            
            # add task
            c.execute(string, data)
            
        conn.commit()
        conn.close()
        '''
        return(True, 'ok')

    def add_single_task(self, task_data): # asset_id=False # v2
        """Создание одной задачи.
        
        Parameters
        ----------
        task_data : dict
            Словарь по :attr:`edit_db.studio.tasks_keys`, обязательные поля: ``activity``, ``task_name``, ``task_type``, ``extension``.\
            Если передать поля ``input``, ``output`` - то будут установлены соединения и призведены проверки, и смены статусов.
        
        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*)
        """
        pass
        # 0 - проверка обязательных полей.
        # 1 - проверка уникальности имени.
        # 2 - назначение данных из ассета.
        # 3 - создание задачи. insert
        # 4 - внесение данной задачи в список output входящей задачи. change_input()
        # 5 - внесение данной задачи в список input исходящей задачи. change_input()
        
        # (0) required fields
        for field in ['activity','task_name','task_type', 'extension']:
            if not task_data.get('%s' % field):
                return(False, 'Not specified the "%s"!' % field)
            
        # (1)
        for td in self.get_list()[1]:
            if td.task_name == task_data['task_name']:
                return(False, 'Task with this name: "%s" already exists!' % task_data['task_name'])
            
        # (2)
        # -- priority
        if not task_data.get('priority'):
            task_data['priority'] = self.asset.priority
        # -- output
        output_task_name = False
        if task_data.get('output'):
            output_task_name = task_data.get('output')[0]
            task_data['output'].append('%s:final' % self.asset.name)
        else:
            task_data['output'] = ['%s:final' % self.asset.name]
        # -- input
        input_task_name = False
        if task_data.get('input'):
            input_task_name = task_data.get('input')
            #task_data['input']= ''
        else:
            task_data['input'] = ''
        #
        #other_fields = [
            #'artist',
            #'planned_time',
            #'time',
            #'supervisor',
            #'price',
            #'specification',
            #]
        #
        task_data['status'] = 'ready'
        task_data['outsource'] = 0
        task_data['season'] = self.asset.season
        #task_data['asset_name'] = self.asset.name
        #task_data['asset_id'] = self.asset.id
        #task_data['asset_type'] = self.asset.type
        
        # (3)
        table_name = '"%s:%s"' % ( self.asset.id, self.tasks_t)
        bool_, return_data = database().insert('project', self.asset.project, table_name, self.tasks_keys, task_data, table_root=self.tasks_db)
        if not bool_:
            return(bool_, return_data)
        
        new_task = self.init_by_keys(task_data, new=True)
        
        # (4)
        if input_task_name:
            bool_, return_data = new_task.change_input(input_task_name)
            if not bool_:
                return(bool_, return_data)
        
        # (5)
        if output_task_name:
            output_task = self.init(output_task_name)
            
            # --
            bool_, return_data = output_task.change_input(new_task.task_name)
            if not bool_:
                return(bool_, return_data)
        
        '''
        # get table
        table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
            
        # Connect to db
        conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # ***************** get current task_status
        if not task_data['input']:
            task_data['status'] = 'ready'
        else:
            #get_input_string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
            get_input_string = 'SELECT * FROM ' + table
            #data = (task_data['input'],)
            #c.execute(get_input_string, data)
            c.execute(get_input_string)
            row = None
            #names = []
            for row_ in c.fetchall():
                #names.append(row_['task_name'])
                #print(row_)
                if task_data['task_name'] == row_['task_name']:
                    conn.close()
                    return(False, 'Thi Task_Name Already Exists!')
                if row_['task_name'] == task_data['input']:
                    row = row_
            #print(row['status'])
            if row['status'] in self.end_statuses:
                task_data['status'] = 'ready'
            else:
                task_data['status'] = 'null'
                
            # ***************** add this task to output to input task
            input_task_data = dict(row)
            new_output_list = json.loads(input_task_data['output'])
            new_output_list.append(task_data['task_name'])
            input_task_data['output'] = json.dumps(new_output_list)
            #print(input_task_data['output'])
            
            new_output_string = string = 'UPDATE ' +  table + ' SET  output  = ? WHERE task_name = ?'
            data = (input_task_data['output'],input_task_data['task_name'])
            c.execute(new_output_string, data)
            
        # ***************** insert TASK_
        insert_string = "insert into " + table + " values"
        values = '('
        data = []
        for i, key in enumerate(self.tasks_keys):
            if i< (len(self.tasks_keys) - 1):
                values = values + '?, '
            else:
                values = values + '?'
            if key[0] in task_data:
                data.append(task_data[key[0]])
            else:
                if key[1] == 'real':
                    data.append(0.0)
                elif key[1] == 'timestamp':
                    data.append(None)
                else:
                    data.append('')
            #print '>>> ', key[0], data[len(data) - 1]
                    
        values = values + ')'
        data = tuple(data)
        insert_string = insert_string + values
        c.execute(insert_string, data)
        
        # ***************** To OUTPUTS 
        old_status = None
        output_row = None
        old_input = None
        if output_task_name:
            # get output_task_data
            get_output_string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
            data = (output_task_name,)
            c.execute(get_output_string, data)
            output_row = c.fetchone()
            old_status = output_row['status']
            old_input = output_row['input']
                        
            # edit input,status to output_task
            string = 'UPDATE ' +  table + ' SET  input  = ?, status = ? WHERE task_name = ?'
            data = (task_data['task_name'],'null', output_task_name)
            c.execute(string, data)
            
            
            # edit output_list to old_input
            if old_input:
                old_input_row = None
                string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
                data = (old_input,)
                c.execute(string, data)
                old_input_row = c.fetchone()
                old_input_output = json.loads(old_input_row['output'])
                old_input_output.remove(output_task_name)
                # -- update
                string = 'UPDATE ' +  table + ' SET  output  = ? WHERE task_name = ?'
                data = (json.dumps(old_input_output), old_input)
                c.execute(string, data)
            
        conn.commit()
        conn.close()
            
        if old_input:
            # change status to output
            if (old_status != 'close') and (old_status in self.end_statuses):
                #print('change status')
                self._this_change_from_end(project_name, dict(output_row))
        '''
                
        return(True, 'Ok')

    def get_list(self, asset_id=False, task_status = False, artist = False): # v2
        """Получение списка задач ассета (экземпляры).
        
        Parameters
        ----------
        asset_id : str, optional
            ``id`` ассета. Передаётся, если список задач требуется не для ассета данной задачи, который есть - :attr:`edit_db.task.asset`.
        task_status : str, optional
            Фильтр по статусам задач. Значение из :attr:`edit_db.studio.task_status`.
        artist : str
            Фильтр по ``nik_name`` артиста.
            
        Returns
        -------
        tuple
            (*True*, ``[список задач - экземпляры]``) или (*False, коммент*)
        """
        if asset_id:
            table_name = '"%s:%s"' % ( asset_id, self.tasks_t)
        else:
            table_name = '"%s:%s"' % ( self.asset.id, self.tasks_t)
        if task_status or artist:
            where = {}
            if task_status and task_status in self.task_status:
                #where = {'status': task_status.lower()}
                where['status'] = task_status.lower()
            elif task_status and not task_status in self.task_status:
                return(False, 'Wrong status "%s"' % task_status)
            if artist:
                where['artist'] = artist
        else:
            where = False
        bool_, return_data = database().read('project', self.asset.project, table_name, self.tasks_keys, where=where, table_root=self.tasks_db)
        
        if not bool_:
            return(bool_, return_data)
        
        tasks_ob = []
        for td in return_data:
            td['asset_path'] = self.asset.path
            tasks_ob.append(self.init_by_keys(td))
        
        return(True, tasks_ob)
        
    def get_tasks_by_name_list(self, task_name_list, assets_data = False): # v2
        """Возвращает задачи (экземпляры) по списку имён задач, из различных ассетов данного проекта.
        
        Parameters
        ----------
        task_name_list : list
            Список имён задач.
        assets_data : dict, optional
            Словарь всех ассетов проекта (экземпляры) с ключами по именам. Результат выполнения функции :func:`edit_db.asset.get_dict_by_name_by_all_types`. Если не передавать - будет произведено чтение БД.
            
        Returns
        -------
        tuple
            (*True*, ``dikt_of_tasks`` [12]_) или (*False*, comment)
            
            .. [12] Структура ``dikt_of_tasks``:
            
                ::
                
                    {
                        task_name : task_ob (экземпляр задачи),
                        ...
                    }
        """
        pass
        # (1) получение assets_data
        if not assets_data:
            result = self.asset.get_dict_by_name_by_all_types()
            if not result[0]:
                return(False, 'in task.get_tasks_by_name_list():\n%s' % result[1])
            else:
                assets_data = result[1]
        # (2) чтение БД
        level = 'project'
        read_ob = self.asset.project
        table_root = self.tasks_db
        keys = self.tasks_keys
        task_data_dict = {}
        #
        for task_name in task_name_list:
            #
            asset_id = assets_data[task_name.split(':')[0]].id
            table_name = '"%s:%s"' % (asset_id, self.tasks_t)
            where = {'task_name': task_name}
            #
            bool_, return_data = database().read(level, read_ob, table_name, keys, where=where, table_root=table_root)
            if not bool_:
                return(bool_, return_data)
            if return_data:
                return_data[0]['asset_path'] = assets_data[task_name.split(':')[0]].path
                r_task = task(assets_data[task_name.split(':')[0]])
                task_data_dict[task_name] = r_task.init_by_keys(return_data[0])
        
        return(True, task_data_dict)

    def change_activity(self, new_activity): # v2
        """Замена активити текущей задачи. Изменяемый параметр :attr:`edit_db.task.activity`
        
        Parameters
        ----------
        new_activity : str
            Новое активити для задачи, значение из :attr:`edit_db.asset.ACTIVITY_FOLDER`.
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        pass
        # (2) проверка валидации new_activity
        if not new_activity in self.asset.ACTIVITY_FOLDER[self.asset.type]:
            return(False, 'Incorrect activity: "%s"' % new_activity)
        # (3) запись БД
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        read_ob = self.asset.project
        update_data = {'activity':new_activity}
        where = {'task_name':self.task_name}
        #
        bool_, return_data = database().update('project', read_ob, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
        # запись нового активити в поле объекта, если он инициализирован
        if bool_ :
            self.activity = new_activity
        return(bool_, return_data)

    def change_price(self, new_price): # v2
        """Замена стоимости текущей задачи. Изменяемый параметр :attr:`edit_db.task.price`.
        
        Parameters
        ----------
        new_price : float
            Новое значение стоимости задачи.
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        pass
        #
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        read_ob = self.asset.project
        update_data = {'price': new_price}
        where = {'task_name':self.task_name}
        #
        bool_, return_data = database().update('project', read_ob, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
        # запись новой цены в поле объекта, если он инициализирован
        if bool_ :
            self.price = new_price
        return(bool_, return_data)
        
    def changes_without_a_change_of_status(self, key, new_data): # v2
        """Замена параметров задачи, которые не приводят к смене статуса.
        
        Parameters
        ----------
        key : str
            Заменяемый параметр. Допустимые на замену параметры:
            ``activity``,
            ``task_type``,
            ``season``,
            ``price``,
            ``specification``,
            ``extension``,
            ``start``,
            ``end``,
            ``time``,
            ``full_time``,
            ``deadline``,
            ``planned_time``,
            ``level``,
        new_data : тип зависит от параметра
            Новое значение для параметра.
        
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        changes_keys = [
        'activity',
        'task_type',
        'season',
        'price',
        'specification',
        'extension',
        'start',
        'end',
        'time',
        'full_time',
        'deadline',
        'planned_time',
        'level',
        ]
        if not key in changes_keys:
            return(False, 'This key invalid! You can only edit keys from this list: %s' % json.dumps(changes_keys))
        
        #
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        update_data = {key: new_data}
        where = {'task_name': self.task_name}
        bool_, r_data = database().update('project', read_ob, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, r_data)
        # запись новых данных в поле объекта, если он инициализирован
        setattr(self, key, new_data)

        return(True, 'Ok!')

    # принудительная перезапись какого либо поля в таблице базы данных текущей задачи, без каких либо изменений во взаимосвязях.
    # key (str) - изменяемое поле в таблице из studio.tasks_keys (имя колонки)
    # new_data (в зависимости от типа данных данной колонки) - новое значение.
    def __change_data(self, key, new_data): # v2
        pass
        #
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        update_data = {key: new_data}
        where = {'task_name': self.task_name}
        bool_, r_data = database().update('project', read_ob, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, r_data)
        
        # запись новых данных в поле объекта.
        setattr(self, key, new_data)
        
        return(True, 'Ok!')

    def add_readers(self, add_readers_list): # v2 *** тестилось без смены статуса.
        """Добавление проверяющих для текущей задачи.
        
        Parameters
        ----------
        add_readers_list : list
            Список никнеймов проверяющих.
            
        Returns
        -------
        tuple
            (*True*, ``readers`` - (слорварь в формате записи как :attr:`edit_db.task.readers`), ``change_status`` - (*bool*)) или (*False*, comment)
        """
        pass
        # ? - проверять ли актуальность списка читателей.
        # 2 - чтение словаря 'readers' и определение change_status
        # 3 - определение update_data
        # 4 - редактирование данного объекта задачи.
        # 5 - перезапись задачи
        # 6 - смена исходящих статусов если change_status=True
        # 7 - запись изменеий в artist.checking_tasks
        
        #
        if not isinstance(add_readers_list, list) and not isinstance(add_readers_list, tuple):
            return(False, '###\nin task.add_readers()\nInvalid type of "add_readers_list": "%s"' % add_readers_list.__class__.__name__)
        
        change_status = False
        readers_dict = {}
        
        # (2)
        readers_dict = self.readers
        if self.status == 'done':
            change_status = True
        
        for artist_name in add_readers_list:
            readers_dict[artist_name] = 0
            
        # (3)
        new_status = False
        if change_status:
            new_status = 'checking'
            update_data = {'status': new_status, 'readers': readers_dict}

        else:
            update_data = {'readers': readers_dict}
                    
        # (4)
        self.readers = readers_dict
        if new_status:
            self.status = new_status
        
        # (5)
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        keys = self.tasks_keys
        where = {'task_name': self.task_name}
        #
        bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, r_data)
        
        # (6) change output statuses
        if change_status:
            bool_, r_data = self._this_change_from_end()
            if not bool_:
                return(bool_, r_data)
            
        # (7)
        for artist_name in add_readers_list:
            artist_ob = artist().init(artist_name)
            if not artist_ob.checking_tasks:
                artist_ob.checking_tasks = {}
            if not self.asset.project.name in artist_ob.checking_tasks.keys():
                artist_ob.checking_tasks[self.asset.project.name] = []
            if not self.task_name in artist_ob.checking_tasks[self.asset.project.name]:
                artist_ob.checking_tasks[self.asset.project.name].append(self.task_name)
            b, r = artist_ob.edit_artist({'checking_tasks': artist_ob.checking_tasks}, current_user='force')
            if not b:
                print('*'*5, r)
                continue		
        
        return(True, readers_dict, change_status)

    def make_first_reader(self, nik_name): # v2
        """обозначение превого проверяющего, только после его проверки есть смысл проверять остальным проверяющим,\
        и только после его приёма данная задача появится в списке на проверку у остальных читателей.\
        Предполагается что это технический проверяющий от отдела, где идёт работа.
        
        Parameters
        ----------
        nik_name : str
            Никнейм.
        
        Returns
        -------
        tuple
            (*True*, ``readers`` - (слорварь в формате записи как :attr:`edit_db.task.readers`), ``change_status`` - (*bool*)) или (*False*, comment)
        """
        pass
        # ? - проверять ли актуальность читателя.
        
        # 2 - чтение словаря 'readers'
        # 3 - редактирование задачи в случае если она инициализирована.
        # 4 - перезапись задачи
        # 5 - редактирование artist.checking_tasks
        
        #
        # (1)
                
        # (2)
        readers_dict = self.readers
        readers_dict['first_reader'] = nik_name
        
        # (3)
        self.readers = readers_dict
            
        # (4)
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        keys = self.tasks_keys
        where = {'task_name': self.task_name}
        #
        update_data = {'readers': readers_dict}
        #
        bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, r_data)
        
        # (5)
        artist_ob = artist().init(nik_name)
        if not artist_ob.checking_tasks:
            artist_ob.checking_tasks = {}
        if not self.asset.project.name in artist_ob.checking_tasks.keys():
                artist_ob.checking_tasks[self.asset.project.name] = []
        if not self.task_name in artist_ob.checking_tasks[self.asset.project.name]:
                artist_ob.checking_tasks[self.asset.project.name].append(self.task_name)
        b, r = artist_ob.edit_artist({'checking_tasks': artist_ob.checking_tasks}, current_user='force')
        if not b:
            print('*'*5, r)
        
        return(True, readers_dict)

    def remove_readers(self, remove_readers_list): # v2
        """Удаляет проверяющего из списка проверяющих, а также удалит его как первого проверяющего, если он таковой.
        
        Parameters
        ----------
        remove_readers_list : list
            Список никнеймов удаляемых из списка проверяющих.
            
        Returns
        -------
        tuple
            (*True*, ``readers`` - (слорварь в формате записи как :attr:`edit_db.task.readers`), ``change_status`` - (*bool*)) или (*False*, comment)
        """
        pass
        # 1 - получение task_data
        # 2 - чтение БД - readers_dict
        # 3 - очистка списка читателей
        # 4 - определение изменения статуса
        # 5 - запись изменения readers в БД
        # 6 - в случае если данная задача инициализирована - внесение в неё изменений.
        # 7 - в случае изменения статуса - изменение статуса исходящих задачь.
        # 8 - редактирование artist.checking_tasks

        change_status = False
        readers_dict = {}
        
        # (1)
        
        # (2)
        readers_dict = self.readers
                
        # (3) remove artists
        for artist_name in remove_readers_list:
            try:
                del readers_dict[artist_name]
            except:
                pass
            if artist_name == readers_dict.get('first_reader'):
                del readers_dict['first_reader']
        
        # (4) get change status
        if self.status in ['checking']:
            change_status = True
        if not readers_dict:
            change_status = False
        else:
            for artist_name in readers_dict:
                if readers_dict[artist_name] == 0:
                    change_status = False
                    break
        
        # (5) edit db
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        keys = self.tasks_keys
        where = {'task_name': self.task_name}
        #
        new_status = False
        if change_status:
            new_status = 'done'
            update_data = {'status': new_status, 'readers': readers_dict}
        else:
            update_data = {'readers': readers_dict}
        bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, r_data)
        
        # (6)
        self.readers = readers_dict
        if new_status:
            self.status = new_status
        
        # (7) change output statuses
        if change_status:
            result = self._this_change_to_end()
            if not result[0]:
                return(False, result[1])
            
        # (8)
        for artist_name in remove_readers_list:
            artist_ob = artist().init(artist_name)
            if not artist_ob.checking_tasks or not artist_ob.checking_tasks.get(self.asset.project.name):
                continue
            if self.task_name in artist_ob.checking_tasks[self.asset.project.name]:
                artist_ob.checking_tasks[self.asset.project.name].remove(self.task_name)
            b, r = artist_ob.edit_artist({'checking_tasks': artist_ob.checking_tasks}, current_user='force')
            if not b:
                print('*'*5, r)
                continue
        
        return(True, readers_dict, change_status)
        
    def change_artist(self, new_artist): # v2  !!!!! возможно надо рассмотреть варианты когда меняется артист в завершённых статусах задачь.
        """Замена артиста и возможная замена при этом статуса. Изменяемый параметр :attr:`edit_db.task.artist`.
        
        Parameters
        ----------
        new_artist : str, :obj:`edit_db.artist`
            Новый артист никнейм или экземпляр, лучше передавать экземпляр для экономии запросов.
            
        Returns
        -------
        tuple
            (*True*, (``new_task_status``, :attr:`edit_db.artist.outsource`)) или (*False*, comment)
        """
        pass
        # 1 - получение task_data.
        # 2 - чтение нового и старого артиста и определение аутсорсер новый или нет.
        # 3 - чтение outsource - изменяемой задачи.
        # 4 - определение нового статуса задачи
        # 5 - внесение изменений в БД
        # 6 - если task инициализирована - внеси в неё изменения.
        # 7 - переписывание поля "working_tasks" артистов (нового и старого)
        
        #print('*** new artist: ', new_artist)
        
        # (1)
                
        #print('### task_data["outsource"].type = %s, value = %s' % (task_data["outsource"].__class__.__name__, str(task_data["outsource"])))
        
        # --------------- edit Status ------------
        new_status = None
                
        # (2) get artist outsource
        artist_outsource = False
        new_artist_ob = None
        old_artist_ob = None
        # -- old artist
        if self.artist:
            old_artist_ob = artist().init(self.artist)
        # -- new artist
        if new_artist and (isinstance(new_artist, str) or isinstance(new_artist, unicode)):
            result = artist().read_artist({'nik_name':new_artist})
            if not result[0]:
                return(False, result[1])
            else:
                new_artist_ob = result[1][0]
            if new_artist_ob.outsource:
                artist_outsource = new_artist_ob.outsource
        elif new_artist and isinstance(new_artist, artist):
            new_artist_ob = new_artist
            artist_outsource = new_artist_ob.outsource
            new_artist = new_artist_ob.nik_name
        else:
            new_artist = ''
        # тест на совпадение нового и старого артиста
        if old_artist_ob and new_artist_ob and old_artist_ob.nik_name == new_artist_ob.nik_name:
            return(False, 'This artist "%s" has already been assigned to this task.' % new_artist_ob.nik_name)
        
        # затыка
        if artist_outsource is None:
            artist_outsource = 0
        #print('*** artist_outsource: %s' % str(artist_outsource))
            
        # (3) get task_outsource
        task_outsource = self.outsource
                
        # (4) get new status
        if self.status in self.VARIABLE_STATUSES:
            #print('****** in variable')
            if not new_artist :
                new_status = 'ready'
            elif (not self.artist) or (not task_outsource):
                #print('****** start not outsource')
                if artist_outsource:
                    new_status = self.CHANGE_BY_OUTSOURCE_STATUSES['to_outsource'][self.status]
                else:
                    pass
                    #print('****** artist not outsource')
            elif task_outsource and (not artist_outsource):
                #print('****** to studio 1')
                new_status = self.CHANGE_BY_OUTSOURCE_STATUSES['to_studio'][self.status]
            else:
                #print('****** start outsource')
                if not artist_outsource:
                    new_status = self.CHANGE_BY_OUTSOURCE_STATUSES['to_studio'][self.status]
                else:
                    pass
                    #print('****** artist outsource')
        else:
            pass
            #print('****** not in variable')
        #print('*** new_status: %s' % str(new_status))
            
        # (5)
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        keys = self.tasks_keys
        where = {'task_name': self.task_name}
        if new_status:
            update_data = {'artist': new_artist, 'outsource': int(artist_outsource), 'status':new_status}
        else:
            update_data = {'artist': new_artist, 'outsource': int(artist_outsource)}
        bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
        
        #print('*'*25, update_data, bool_)
        
        if not bool_:
            return(bool_, r_data)
        
        # (6)
        if new_status:
            self.status = new_status
            self.outsource = int(artist_outsource)
            self.artist = new_artist
        else:
            self.outsource = int(artist_outsource)
            self.artist = new_artist
            
        # (7)
        #print(old_artist_ob, new_artist_ob)
        
        # -- old
        if old_artist_ob and  old_artist_ob.working_tasks.get(self.asset.project.name) and self.task_name in old_artist_ob.working_tasks[self.asset.project.name]:
            old_artist_ob.working_tasks[self.asset.project.name].remove(self.task_name)
            b, r = old_artist_ob.edit_artist({'working_tasks': old_artist_ob.working_tasks}, current_user='force')
            if not b:
                print('*'*5, r)
                #return(r)
        # -- new
        if new_artist:
            if not new_artist_ob.working_tasks:
                new_artist_ob.working_tasks = {}
            if not self.asset.project.name in new_artist_ob.working_tasks.keys():
                new_artist_ob.working_tasks[self.asset.project.name] = []
            if not self.task_name in new_artist_ob.working_tasks[self.asset.project.name]:
                new_artist_ob.working_tasks[self.asset.project.name].append(self.task_name)
            b, r = new_artist_ob.edit_artist({'working_tasks': new_artist_ob.working_tasks}, current_user='force')
            if not b:
                print('*'*5, r)
                #return(r)
            
        return(True, (new_status, int(artist_outsource)))
        
    def change_input(self, new_input): # v2 *** тестилось без смены статуса.
        """Изменение входа не сервисной задачи, с вытикающими изменениями статусов. Изменяемый параметр :attr:`edit_db.task.input`.
        
        Parameters
        ----------
        new_input : str
            Имя новой входящей задачи.
            
        Returns
        -------
        tuple
            (*True*, (``new_status``, ``old_input_task_data``, ``new_input_task_data``)) или (*False*, comment)
        """
        pass
        # 1 - получение task_data, task_outsource, old_input_task, new_input_task, new_status, list_output_old, list_output_new
        # 2 - перезапись БД
        # 3 - подготовка return_data
        
        # (1)
        if new_input:
            if self.output and new_input in self.output:
                return(False, 'Outgoing task cannot be added to input!')
        
        # get old inputs tasks data (task instance)
        old_input_task = None
        if self.input:
            old_input_task = self.init(self.input)
        
        # get new inputs task data (task instance)
        new_input_task = None
        if new_input:
            new_input_task = self.init(new_input)
        
        # ???
        # change status
        new_status = self._from_input_status(new_input_task)
        if self.status in self.end_statuses and not new_status in self.end_statuses:
            self._this_change_from_end()
                
        # change outputs
        # -- in old input
        list_output_old = None # output бывшей входящей задачи
        if old_input_task:
            list_output_old = old_input_task.output
            if self.task_name in list_output_old:
                list_output_old.remove(self.task_name)
            
        # -- in new input
        list_output_new = None
        if new_input_task:
            if not new_input_task.output:
                list_output_new = []
            else:
                list_output_new = new_input_task.output
            list_output_new.append(self.task_name)
            
        # prints
        #if new_input_task:
            #print('new input: %s' % new_input_task.task_name)
        #else:
            #print('new input: %s' % new_input_task)
        #if old_input_task:
            #print('old input: %s' % old_input_task.task_name)
        #print('new status: %s' % new_status)
        #print('list_output_old:' , list_output_old)
        #print('list_output_new:' , list_output_new)
        #return(True, 'Be!')
        
        # (2)
        # change data
        if new_input_task:
            if list_output_new:
                new_input_task.__change_data('output', list_output_new)
            self.__change_data('input', new_input_task.task_name)
        else:
            self.__change_data('input', '')
        #
        if old_input_task and list_output_old:
            old_input_task.__change_data('output', list_output_old)
        #
        if new_status:
            self.__change_data('status', new_status)
        
        # (3)
        return(True, (new_status, old_input_task, new_input_task))
        
    def accept_task(self): # v2
        """Приём задачи, статус на ``done`` (со всеми вытикающими сменами статусов), создание паблиш версии, заполнение ``artist_tasks_log`` (``finish``,``price``), выполнение хуков.
        
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        pass
        # 1 - получение task_data,
        # 2 - перезапись БД задачи
        # 3 - изменение статусов исходящих задачь
        # 4 - запись task лога
        # 5 - запись artist_task_log
        # 6 - внесение изменений в объект если он инициализирован
        
        # (1)
        
        '''
        # (-) publish
        #result = lineyka_publish.publish().publish(project_name, task_data)
        result = self.publish.publish(self) # ???????????????????????????????????????????????? переработать
        if not result[0]:
            return(False, result[1])
        '''
        
        # (2)
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        keys = self.tasks_keys
        update_data = {'readers':{}, 'status':'done'}
        where = {'task_name': self.task_name}
        bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, r_data)
        
        # (3) change output statuses
        result = self._this_change_to_end()
        if not result[0]:
            return(False, result[1])
        
        # (4)
        log_keys = {
        'description': 'accept',
        'action': 'done',
        }
        b, r = log(self).write_log(log_keys)
        if not b:
            return(b, r)
        
        # (5)
        artist_log_keys = {
        'price': self.price,
        'finish': datetime.datetime.now(),
        }
        b, r = log(self).artist_write_log(artist_log_keys)
        if not b:
            return(b, r)
        
        # (6)
        self.status = 'done'
        self.readers = {} # ???
            
        return(True, 'Ok!')

    def readers_accept_task(self, current_artist): # v2
        """приём задачи текущим проверяющим, изменение статуса в :attr:`edit_db.task.readers`, если он последний то смена статуса задачи на ``done`` (со всеми вытикающими сменами статусов).
        
        Parameters
        ----------
        current_artist : :obj:`edit_db.artist`
            Артист - экземпляр.
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        pass
        # 0 - проверка, чтобы current_artist был экземпляром класса artist
        # 1 - изменения в readers, определение change_status
        # 2 - запись лога
        # 3 - accept_task()
        # 4 - внесение изменений в объект.
        
        # (0)
        if not isinstance(current_artist, artist):
            return(False, 'in task.readers_accept_task() - "current_artist" must be an instance of "artist" class, and not "%s"' % current_artist.__class__.__name__)
        
        # (1)
        change_status = True
        readers = self.readers
        if current_artist.nik_name in readers:
            readers[current_artist.nik_name] = 1
        else:
            return(False, 'Current user is not a reader of this task!')
        #
        for key in readers:
            if key == 'first_reader':
                continue
            elif readers[key] == 0:
                change_status = False
                break
            
        # (2)
        log_keys = {
        'description': 'reader_accept',
        'action': 'reader_accept',
        }
        b, r = log(self).write_log(log_keys)
        if not b:
            return(b, r)
        
        # (3)
        if change_status:
            b ,r = self.accept_task()
            if not b:
                return(b, r)
        
        # (-) -- publish
        '''
        if change_status:
            result = self.publish.publish(self)
            if not result[0]:
                return(False, result[1])
                
        # (-)
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        keys = self.tasks_keys
        if change_status:
            update_data = {'readers':readers, 'status':'done'}
        else:
            update_data = {'readers':readers}
        where = {'task_name': self.task_name}
        bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, r_data)
        
        # (-) change output statuses
        if change_status:
            # -- change output statuses
            result = self._this_change_to_end()
            if not result[0]:
                return(False, result[1])
        '''
        # (4)
        self.readers = readers
        if change_status:
            self.status = 'done'
        
        return(True, 'Ok')

    def close_task(self): # v2
        """Закрытие задачи, смена статуса на ``close`` (со всеми вытикающими сменами статусов). Изменяемый параметр :attr:`edit_db.task.status`.
        
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        pass
        # 1 - получение task_data
        # 2 - запись изменений задачи в БД
        # 3 - изменение статусов исходящих задачь
        # 4 - запись лога
        # 5 - внесение изменений в объект если он инициализирован
        
        # (1)
                        
        # (2)
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        keys = self.tasks_keys
        update_data = {'status':'close'}
        where = {'task_name': self.task_name}
        bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, r_data)
                
        # (3) change output statuses
        result = self._this_change_to_end()
        if not result[0]:
            return(False, result[1])
        
        # (4)
        log_keys = {
        'description': 'close',
        'action': 'close',
        }
        b, r = log(self).write_log(log_keys)
        if not b:
            return(b, r)
        
        # (5)
        self.status = 'close'
            
        return(True, 'Ok!')

    def rework_task(self, current_user): # v2 ** продолжение возможно только после редактирования chat().read_the_chat()
        """Отправка задачи на переработку из статуса на проверке (``ready_to_send``), при этом проверяется наличие свежего (последние 30 минут) коментария от данного проверяющего (``current_user``). Изменяемый параметр :attr:`edit_db.task.status`.
        
        Parameters
        ----------
        current_user : :obj:`edit_db.artist`
            Экземпляр класса артист, должен быть инициализирован. Если передать *False* - то задача отправится на переделку без проверки чата (для тех нужд).
        
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        pass
        # 1 - get exists chat
        # 2 - edit readers
        # 3 - write db
        # 4 - запись лога
        # 5 - edit self.status
        
        # (1)
        if current_user:
            if not isinstance(current_user, artist):
                return(False, 'in task.rework_task() - "current_user" must be an instance of "artist" class, and not "%s"' % current_user.__class__.__name__)
            exists_chat = False
            result = chat(self).read_the_chat()
            if not result[0]:
                return(False, 'No chat messages! To send for rework, you must specify the reason in the chat.')
            
            delta = datetime.timedelta(minutes = 45)
            now_time = datetime.datetime.now()
            for topic in result[1]:
                if topic['author'] == current_user.nik_name:
                    if (now_time - topic['date_time']) <= delta:
                        exists_chat = True
                        break
                        
            if not exists_chat:
                return(False, 'No chat messages or no fresh (30 minutes) messages! To send for rework, you must specify the reason in the chat.')
        
        # (2)
        if self.readers:
            for nik_name in self.readers:
                if nik_name == 'first_reader':
                    continue
                self.readers[nik_name] = 0
        
        # (3)
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        keys = self.tasks_keys
        update_data = {'status':'recast', 'readers': self.readers}
        where = {'task_name': self.task_name}
        bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, r_data)
        
        # (4)
        log_keys = {
        'description': 'recast',
        'action': 'recast',
        }
        b, r = log(self).write_log(log_keys)
        if not b:
            return(b, r)
        
        # (5)
        self.status = 'recast'
        
        return(True, 'Ok!')

    def return_a_job_task(self): # v2
        """Возврат в работу задачи из завершённых статусов - :attr:`edit_db.studio.end_statuses`, со всеми вытекающими изменениями статусов исходящих задачь. Изменяемый параметр :attr:`edit_db.task.status`.
        
        Returns
        -------
        tuple
            (*True*, ``new_status``) или (*False*, comment)
        """
        pass
        # 1 - получение task_data,
        # 2 - чтение входящей задачи
        # 3 - получение статуса на основе статуса входящей задачи.
        # 4 - внесение изменений в БД
        # 5 - запись лога
        # 6 - изменение статусов исходящих задач
        
        # (2)
        input_task = False
        if self.input:
            input_task = self.init(self.input)
        
        # (3)
        self.status = 'null'
        new_status = self._from_input_status(input_task)
        #return(True, new_status)
        
        # (4)
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        keys = self.tasks_keys
        update_data = {'readers':{}, 'status':new_status}
        where = {'task_name': self.task_name}
        bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, r_data)
        
        # (5)
        log_keys = {
        'description': 'return a job',
        'action': 'return_a_job',
        }
        b, r = log(self).write_log(log_keys)
        if not b:
            return(b, r)
        
        # (6) change output statuses
        result = self._this_change_from_end()
        if not result[0]:
            return(False, result[1])
        else:
            return(True, new_status)
            
    def change_work_statuses(self, change_statuses): # v2
        """Тупо смена статусов в пределах рабочих, что не приводит к смене статусов исходящих задач. Изменяемый параметр :attr:`edit_db.task.status`. Применяется для списка задач.
        
        Parameters
        ----------
        change_statuses : list
            Список кортежей - (``task_ob``, ``new_status``)
        
        Returns
        -------
        tuple
            (*True*, {``task_name``: ``new_status``, ... }) или (*False*, comment)
        """
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        return_data_ = {}
        for data in change_statuses:
            task_ob = data[0]
            new_status = data[1]
            #
            if new_status not in (self.working_statuses + ['checking']):
                continue
            #
            update_data = {'status': new_status}
            where = {'task_name': task_ob.task_name}
            bool_, return_data = database().update('project', self.asset.project, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
            if not bool_:
                return(False, return_data)
            #
            task_ob.status = new_status
            #
            return_data_[task_ob.task_name] = new_status
            
        return(True, return_data_)

    def to_checking(self):
        """Отправка текущей задачи на проверку. Обёртка на :obj:`edit_db.task.change_work_statuses`. Изменение параметра :attr:`edit_db.task.status` на ``ready_to_send``.
        
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        b, r = self.change_work_statuses([(self, 'checking')])
        if not b:
            return(b, r)
        else:
            pass
            #
            log_keys = {
            'description': 'report',
            'action': 'report',
            }
            b, r = log(self).write_log(log_keys)
            if not b:
                return(b, r)
            #
            self.status = 'checking'
            return(True, 'Ok!')

    def _read_task(self, task_name): # v2
        """Возврат словаря задачи (по ключам из :attr:`edit_db.studio.tasks_keys` , чтение БД) по имени задачи. если нужен объект используем :func:`edit_db.task.init`.
        
        Parameters
        ----------
        task_name : str
            Имя задачи.
            
        Returns
        -------
        tuple
            (*True*, {``task_data``}) или (*False*, comment)
        """
        pass
        # 1 - get asset_id, other_asset
        # 2 - read task_data
        # 3 - return
        
        # (1)
        other_asset=False
        
        if self.asset.name == task_name.split(':')[0]: # задача из данного ассета
            asset_id = self.asset.id
        # asset_path
        else: # задача из другого ассета
            other_asset = self.asset.init(task_name.split(':')[0])
            asset_id = other_asset.id
        
        # (2) read task
        table_name = '"%s:%s"' % (asset_id, self.tasks_t)
        where={'task_name': task_name}
        
        # -- read
        bool_, return_data = database().read('project', self.asset.project, table_name, self.tasks_keys , where=where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, return_data)
        if not return_data:
            return(False, 'Not Found task whith name "%s"!' % task_name)
        
        task_data = return_data[0]
        
        # (3)
        return (True, (task_data, other_asset))
        '''
        if not other_asset:
            return(True, self.init_by_keys(task_data))
        else:
            task_ob = task(other_asset)
            task_ob.init_by_keys(task_data, new=False)
            return(True, task_ob)
        '''

    def _service_add_list_to_input(self, input_task_list): # v2
        """Добавление списка задач во входящие сервисной задаче, со всеми вытикающими изменениями статусов. Изменяется параметр :attr:`edit_db.task.input`, с возможными изменениями статусов, как данной, так и исходящих задач.
        
        Parameters
        ----------
        input_task_list : list
            Список задач (экземпляры).
        
        Returns
        -------
        tuple
            (*True*, (``new_ststus``, [``append_task_name_list``])) или (*False, comment*)
        """
        pass
        # 0 - получение task_data.
        # 1 - проверка на srvice
        # 2 - получение данных для перезаписи инпута данной задачи и аутпутов новых входящих задач.
        # 3 - изменение статуса данной задачи.
        # 4 - внесение изменений в БД по данной задаче.
        # 5 - внесение изменений в БД по входящим задачам.
        # 6 - внесение изменений в объект, если он инициализирован
        
        # (0)
                        
        # (1)
        if self.task_type != 'service':
            description = 'In task._service_add_list_to_input() - incorrect type!\nThe type of task to be changed must be "service".\nThis type: "%s"' % self.task_type
            return(False, description)
        
        # (2)
        # add input list
        # -- get_input_list
        overlap_list = []
        inputs = []
        done_statuses = []
        rebild_input_task_list = []
        for task_ob in input_task_list:
            # -- get inputs list
            if self.input:
                ex_inputs = []
                try:
                    ex_inputs = self.input
                except:
                    pass
                if task_ob.task_name in ex_inputs:
                    overlap_list.append(task_ob.task_name)
                    continue
            inputs.append(task_ob.task_name)
            # -- get done statuses
            done_statuses.append(task_ob.status in self.end_statuses)
            
            # edit outputs
            if task_ob.output:
                ex_outputs = []
                try:
                    ex_outputs = task_ob.output
                except:
                    pass
                ex_outputs.append(self.task_name)
                task_ob.output = ex_outputs
            else:
                this_outputs = []
                this_outputs.append(self.task_name)
                task_ob.output = this_outputs
                
            rebild_input_task_list.append(task_ob)
            
        if not self.input:
            self.input = inputs
        else:
            ex_inputs = []
            try:
                ex_inputs = self.input
            except:
                pass
            self.input = ex_inputs + inputs
        
        # (3) change status
        if self.status in self.end_statuses:
            if False in done_statuses:
                self.status = 'null'
                self._this_change_from_end()
                
        # (4)
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
        keys = self.tasks_keys
        update_data = {'input':self.input, 'status':self.status}
        where = {'task_name': self.task_name}
        bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, r_data)
        
        # (5)
        append_task_name_list = []
        for task_ob in rebild_input_task_list:
            if not task_ob.task_name in overlap_list:
                table_name = '"%s:%s"' % (task_ob.asset.id, self.tasks_t)
                update_data = {'output':task_ob.output}
                where = {'task_name': task_ob.task_name}
                append_task_name_list.append(task_ob.task_name)
                bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
                if not bool_:
                    return(bool_, r_data)
                
        # (6)
        #self.status = task_data['status']
        #self.input = task_data['input']
        
        return(True, (self.status, append_task_name_list))
    
    def _service_add_list_to_input_from_asset_list(self, asset_list): # v2
        """Добавление задач во входящие сервисной задаче из списка ассетов. Из списка задач ассета подсоединяется первая задача нужного активити. Изменяется параметр :attr:`edit_db.task.input`, с возможными изменениями статусов, как данной, так и исходящих задач.
        
        Parameters
        ----------
        asset_list : list
            Список подсоединяемых ассетов (словари, или экземпляры).
            
        Returns
        -------
        tuple
            (*True*, (``this_task_data``, ``append_task_name_list``)) ``?? пересмотреть``  или (*False, коммент*)
        """
        pass
        # 1 - получение task_data.
        # 2 - проверка на srvice
        # 3 - получение списка задачь для добавления в инпут
        
        # (1)
        #if not task_data:
        task_data=dict()
        for key in self.tasks_keys:
            exec('task_data["%s"] = self.%s' % (key, key))
                
        # (2)
        if task_data['task_type'] != 'service':
            description = 'In task._service_add_list_to_input_from_asset_list() - incorrect type!\nThe type of task to be changed must be "service".\nThis type: "%s"' % task_data['task_type']
            return(False, description)
        
        # (3)
        final_tasks_list = []
        #types = {'obj':'model', 'char':'rig'}
        types = {'mesh':'model', 'group':'model',  'rig':'rig'}
        for ast in asset_list:
            if isinstance(ast, dict):
                ast_ob = asset(self.asset.project)
                ast_ob.init_by_keys(ast, new=False)
            elif isinstance(ast, asset):
                ast_ob = ast
            else:
                continue
            tsk_ob = task(ast_ob)
            #if task_data['asset_type'] in ['location', 'shot_animation'] and ast_ob.type in types:
            if task_data['asset_type'] in ['location', 'shot_animation'] and ast_ob.type=='object':
                pass
                #activity = types[ast_ob.type]
                activity = types[ast_ob.loading_type]
                bool_, task_list = tsk_ob.get_list()
                if not bool_:
                    return(bool_, task_list)
                #
                td_dict = {}
                for td in task_list:
                    td_dict[td['task_name']] = td
                #
                for td in task_list:
                    if td.get('activity') == activity:
                        if not td.get('input') or td_dict[td['input']]['activity'] != activity:
                                final_tasks_list.append(td)
            else:
                task_name = (ast_ob.name + ':final')
                td = tsk_ob.init(task_name)
                final_tasks_list.append(td)
        '''
        # edit db
        # -- Connect to db
        conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # get task list
        final_tasks_list = []
        for asset in asset_list:
            if task_data['asset_type'] in ['location', 'shot_animation'] and asset['type'] in ['obj', 'char']:
                activity = None
                if asset['type'] == 'obj':
                    activity = 'model'
                elif asset['type'] == 'char':
                    activity = 'rig'
                
                # get all task data
                table = '\"' + asset['id'] + ':' + self.tasks_t + '\"'
                string = 'select * from ' + table
                try:
                    c.execute(string)
                except:
                    print(('Not exicute in _service_add_list_to_input_from_asset_list -> ' + asset['name']))
                    continue
                else:
                    td_dict = {}
                    rows = c.fetchall()
                    for td in rows:
                        td_dict[td['task_name']] = td
                        
                    for td in rows:
                        if td['activity'] == activity:
                            if not dict(td).get('input') or td_dict[td['input']]['activity'] != activity:
                                final_tasks_list.append(td)
            
            else:
                task_name = (asset['name'] + ':final')
                
                table = '\"' + asset['id'] + ':' + self.tasks_t + '\"'
                string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
                try:
                    c.execute(string)
                    final_task = dict(c.fetchone())
                    final_tasks_list.append(final_task)
                except:
                    print(('not found task: ' + task_name))
        
        conn.close()
        '''
        
        result = self._service_add_list_to_input(final_tasks_list, task_data)
        if not result[0]:
            return(False, result[1])
        
        #
        if self.task_name == task_data['task_name']:
            self.status = result[1][0]
            for task_name in result[1][1]:
                if not task_name in self.input:
                    self.input.append(task_name)
        
        return(True, result[1])
        
    def _service_remove_task_from_input(self, removed_tasks_list, task_data=False, change_status = True): # v2
        """Удаление списка задач из :attr:`edit_db.task.input` сервисной задачи, с возможными изменениями статусов, как данной, так и исходящих задач.
        
        .. attention :: Переработать, уйти от словарей, переделать на объекты, не передавать ``task_data``.
        
        Parameters
        ----------
        removed_tasks_list : list
            Содержит список словарей удаляемых из инпута задач ``?? переработать - заменить на объекты``
        task_data : dict, optional
            Изменяемая задача, если *False* - значит предполагается, что *task* инициализирован ``лучше не использовать``.
        change_status : bool, optional
            Если *True* то пересматривается статус данной и исходящих задачь, если *False* то статусы персматриваться не будут.
        
        Returns
        -------
        tuple
            (*True*, (``new_status`` [13]_, ``input_list`` [14]_) или (*False*, comment)
            
            .. [13] ``new_status`` - новый статус данной задачи.
            .. [14] ``input_list`` - получаемое значение инпут атрибута :attr:`edit_db.task.input`.
        """
        pass
        # 0 - получение task_data.
        # 1 - тест на статус сервис-не сервис.
        # 2 - очистка списка входящих.
        # 3 - замена статуса очищаемой задачи.
        # 4 - удаление данной задачи из output - входящей задачи.
        # 5 - перезепись status, input - изменяемой задачи.
        # 6 - изменение статуса далее по цепи.
        # 7 - внесение изменений в объект, если он инициализирован
        
        # (0)
        if not task_data:
            task_data={}
            for key in self.tasks_keys:
                exec('task_data["%s"] = self.%s' % (key, key))
        
        # (1)
        if task_data['task_type'] != 'service':
            description = 'In task._service_remove_task_from_input() - incorrect type!\nThe type of task being cleared, must be "service".\nThis type: "%s"' % task_data['task_type']
            return(False, description)
        
        # (2)
        # get input_list
        input_list = task_data['input']
        # removed input list
        for tsk in removed_tasks_list:
            if tsk['task_name'] in input_list:
                input_list.remove(tsk['task_name'])
            else:
                print('warning! *** ', tsk['task_name'], ' not in ', input_list)
        
        # (3)
        # GET STATUS
        new_status = None
        old_status = task_data['status']
        assets = False
        if old_status == 'done' or not input_list:
            new_status = 'done'
        else:
            # get assets dict
            result = self.asset.get_dict_by_name_by_all_types()
            if not result[0]:
                return(False, result[1])
            assets = result[1]
            #
            bool_statuses = []
            
            for task_name in input_list:
                bool_, r_data = self.get_tasks_by_name_list([task_name], assets_data = assets.get(task_name.split(':')[0]))
                if not bool_:
                    print('#'*5)
                    print('in task.get_tasks_by_name_list()')
                    print('task_name - %s' % task_name)
                    print('asset_data - ', assets_data)
                    continue
                else:
                    if r_data:
                        inp_task_data = r_data[task_name]
                    else:
                        continue
                
                if inp_task_data['status'] in self.end_statuses:
                    bool_statuses.append(True)
                else:
                    bool_statuses.append(False)
                    
            if False in bool_statuses:
                new_status = 'null'
            else:
                new_status = 'done'
        '''
        # ****** connect to db
        conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        assets = False
        if old_status == 'done' or not input_list:
            new_status = 'done'
        else:
            # get assets dict
            result = self.get_dict_by_name_by_all_types(project_name)
            if not result[0]:
                return(False, result[1])
            assets = result[1]
            
            bool_statuses = []
            
            for task_name in input_list:
                try:
                    asset_id = assets[task_name.split(':')[0]]['id']
                except:
                    print(('in from_service_remove_input_tasks incorrect key: ' + task_name.split(':')[0] + ' in ' + task_name))
                    continue
                
                table = '\"' + asset_id + ':' + self.tasks_t + '\"'
                
                string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
                try:
                    c.execute(string)
                    inp_task_data = c.fetchone()
                except:
                    conn.close()
                    return(False, ('in from_service_remove_input_tasks can not read ' + string))
                    
                if inp_task_data['status'] in self.end_statuses:
                    bool_statuses.append(True)
                else:
                    bool_statuses.append(False)
                    
            if False in bool_statuses:
                new_status = 'null'
            else:
                new_status = 'done'
        '''	
        # (4)
        for tsk in removed_tasks_list:
            output_list = tsk['output']
            if not output_list:
                continue
            
            if task_data['task_name'] in output_list:
                output_list.remove(task_data['task_name'])
                print('#'*5, tsk['task_name'], output_list)
            else:
                print('#'*5)
                continue
            
            table = '"%s:%s"' % (tsk['asset_id'], self.tasks_t)
            update_data = {'output': output_list}
            where = {'task_name': tsk['task_name']}
            bool_, r_data = database().update('project', self.asset.project, table, self.tasks_keys, update_data, where, table_root=self.tasks_db)
            if not bool_:
                return(bool_, r_data)
            '''
            string = 'UPDATE ' + table + ' SET output = ? WHERE task_name = ?'
            data = (json.dumps(output_list), tsk['task_name'])
            c.execute(string, data)
            '''
        # (5)
        table = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
        if change_status:
            update_data = {'input': input_list, 'status':new_status}
        else:
            update_data = {'input': input_list}
        where = {'task_name': task_data['task_name']}
        bool_, r_data = database().update('project', self.asset.project, table, self.tasks_keys, update_data, where, table_root=self.tasks_db)
        if not bool_:
            return(bool_, r_data)
        
        '''
        table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
        string = 'UPDATE ' + table + ' SET status = ?, input = ?  WHERE task_name = ?'
        data = (new_status, json.dumps(input_list), task_data['task_name'])
        c.execute(string, data)
        conn.commit()
        conn.close()
        '''
        
        # (6)
        if change_status:
            if old_status == 'done' and new_status == 'null':
                self._this_change_from_end(task_data, assets = assets)
            elif old_status == 'null' and new_status == 'done':
                self._this_change_to_end(task_data, assets = assets)
                
        # (7)
        if self.task_name == task_data['task_name']:
            if change_status:
                self.status = new_status
            self.input = input_list
        
        # return
        if change_status:
            return(True, (new_status, input_list))
        else:
            return(True, (old_status, input_list))
    
    def _service_change_task_in_input(self, removed_task_data, added_task_data, task_data=False): # v2
        """Замена одной входящей задачи на другую, для сервисной задачи. Изменение параметра :attr:`edit_db.task.input`, с возможными изменениями статусов данной и исходящих задач.
        
        .. attention :: Переработать, уйти от словарей, переделать на объекты, не передавать ``task_data``.
        
        Parameters
        ----------
        removed_task_data : dict
            Словарь удаляемой задачи, ``переработать - заменить на экземпляр!!!``.
        added_task_data : dict
            Словарь добавляемой задачи, ``переработать - заменить на экземпляр!!!``.
        task_data : dict, optional
            Изменяемая задача, если *False* - значит предполагается, что *task* инициализирован ``лучше не использовать``.
        
        Returns
        -------
        tuple
            (*True*, (``this_task_data``, ``append_task_name_list``)) ``?? пересмотреть``  или (*False, коммент*).
        """
        pass
        # 0 - получение task_data.
        
        # (0)
        if not task_data:
            task_data={}
            for key in self.tasks_keys:
                exec('task_data["%s"] = self.%s' % (key, key))
        
        # debug
        #print(task_data['task_name'])
        #print(removed_task_data['task_name'])
        #print(added_task_data['task_name'])
        
        # remove task
        result = self._service_remove_task_from_input([removed_task_data], task_data=task_data)
        if not result[0]:
            return(False, result[1])
        
        new_status, input_list = result[1]
        
        # edit task_data
        print(task_data['input'], task_data['status'])
        #
        task_data['input'] = input_list
        task_data['status'] = new_status
        #
        print(task_data['input'], task_data['status'])
        
        #print(json.dumps(task_data, sort_keys = True, indent = 4))
        #return(False, 'Epteeeee!')
        
        # add task
        result = self._service_add_list_to_input([added_task_data], task_data=task_data)
        if not result[0]:
            return(False, result[1])
        
        #
        if self.task_name == task_data['task_name']:
            self.status = result[1][0]
            self.input = input_list + result[1][1]
            
        return(True, result[1])

    # заменяет все рид статусы задачи на 0
    # task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
    def task_edit_read_status_unread(self, task_data=False): # УСТАРЕЛО!!!!!!!!!!!!! 
        pass
        # 0 - получение task_data.
        # 1 - принудительное прочтение задачи из БД - ???????????? зачееемм!!!!!!
        
        # (0)
        if not task_data:
            task_data={}
            for key in self.tasks_keys:
                exec('task_data["%s"] = self.%s' % (key, key))
                
        # (1)
        read_ob = self.asset.project
        table_name = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
        keys = self.tasks_keys
        where = {'task_name': task_data['task_name']}
        
        
        '''
        table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
        string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
        data = (task_data['task_name'],)
        
        # connect db
        try:
            conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
        except:
            return(False, 'in task_edit_read_status_unread - not connect db!')
        
        # read-edit data
        c.execute(string, data)
        task_data = dict(c.fetchone())
        try:
            readers = json.loads(task_data['readers'])
            for nik_name in readers:
                readers[nik_name] = 0
            task_data['chat_local'] = json.dumps(readers)
        except:
            task_data['chat_local'] = json.dumps({})
            
        # write data
        string = 'UPDATE ' + table + 'SET chat_local = ? WHERE task_name = ?'
        data = (task_data['chat_local'], task_data['task_name'])
        c.execute(string, data)
        
        conn.commit()
        conn.close()
        '''
        return(True, 'Ok!')

    # заменяет все рид статусы задачи на 1
    # self.task - должен быть инициализирован
    def task_edit_read_status_read(self, project_name, task_data, nik_name): # УСТАРЕЛО!!!!!!!!!!!!! 
        pass
        # test project
        result = self.get_project(project_name)
        if not result[0]:
            return(False, result[1])
            
        table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
        string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
        data = (task_data['task_name'],)
        
        # connect db
        try:
            conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
        except:
            return(False, 'in task_edit_read_status_read - not connect db!')
        
        # read-edit data
        c.execute(string, data)
        task_data = dict(c.fetchone())
        
        readers2 = {}
        try:
            readers2 = json.loads(task_data['chat_local'])
            readers2[nik_name] = 1
        except:
            readers2[nik_name] = 1
        task_data['chat_local'] = json.dumps(readers2)
        
        # write data
        string = 'UPDATE ' + table + 'SET chat_local = ? WHERE task_name = ?'
        data = (task_data['chat_local'], task_data['task_name'])
        c.execute(string, data)
        
        conn.commit()
        conn.close()
        
        return(True, 'Ok!')

class log(studio):
    """**level** = 'project'

    Данные хранимые в БД (имя столбца : тип данных):

    Лог экшена задачи (активити) из списка :attr:`edit_db.log.log_actions`. Одна запись на экшн. :attr:`edit_db.studio.logs_keys`.
    
    .. code-block:: python
        
        logs_keys = {
        'version': 'text',              # hex 4 символа
        'date_time': 'timestamp',       # время и дата записи
        'activity': 'text',             # ативити задачи
        'task_name': 'text',            # имя задачи
        'action': 'text',               # тип записи из log.log_actions
        'artist': 'text',               # nik_name артиста, кто делает запись
        'description': 'text',          # коментарий
        'source': 'json',               # для push - версия коммита источника (в случае sketch - список версий по всем веткам, порядок совпадает с порядком записи веток в branch), для publish - версия push источника.
        'branch' : 'text',              # ветка - в случае push, publish (для sketch - список веток).
        'time' : 'integer',             # время затраченное на commit, ед. измерения секунда.
        }
        
    Лог артиста по задачам. Одна запись на задачу. :attr:`edit_db.studio.artists_logs_keys`.
    
    .. code-block:: python
    
        artists_logs_keys = {
        'project_name': 'text',
        'task_name': 'text',
        'full_time': 'integer',         # суммарное время затраченое артистом на задачу, ед. измерения секунда.
        'price': 'real',                # сумма начисленная за выполнение задачи. вносится по принятию задачи.
        'start': 'timestamp',           # дата-время создания записи, запись создаётся при первом open задачи.
        'finish': 'timestamp',          # дата-время принятия задачи.
        }
        
    Лог артиста по дням, заполняемый вручную: день/проект/задача/время. Одна запись на задачу в день. :attr:`edit_db.studio.artists_time_logs_keys`.
    
    .. code-block:: python
    
        artists_time_logs_keys = {
        'project_name':'text',
        'task_name':'text',
        'date':'timestamp',  # возможно только дата без времени?
        'time':'integer',    # суммарное время затраченое артистом на задачу, ед. измерения секунда. Заполняется вручную.
        }
        
    Examples
    --------
    Создание экземпляра класса:

    .. code-block:: python
    
        import edit_db as db
  
        project = db.project()
        asset = db.asset(project)
        task = db.task(asset)
        
        log = db.log(task) # task - обязательный параметр при создании экземпляра log
        # доступ ко всем параметрам и методам принимаемого экземпляра task - через log.task
    
    Attributes
    ----------
    task : :obj:`edit_db.task`
        Экземпляр задачи принимаемый при создании экземпляра класса, содержит все атрибуты и методы :obj:`edit_db.task`.
    """
    
    no_editable_keys = ['project_name', 'task_name', 'start']
    """Список параметров лога артиста, которые нельзя редактировать. """
    
    camera_log_file_name = 'camera_logs.json'
    """str: Имя ``json`` файла куда записывается лог камеры. ``?``"""
    
    playblast_log_file_name = 'playblast_logs.json'
    """str: Имя ``json`` файла куда записывается лог плейбласта. ``?``"""
    
    log_actions = [
    'pull',
    'commit',
    'push',
    'publish',
    'open',
    'report',
    'recast',
    'change_artist',
    'close',
    'done', # принятие задачи со всеми вытекающими
    'reader_accept', # утверждение задачи одним из проверяющих, в процедуре task.readers_accept_task()
    'return_a_job',
    'send_to_outsource',
    'load_from_outsource'
    ]
    """list: Список возможных экшенов для задач."""
        
    def __init__(self, task_ob): # v2
        if not isinstance(task_ob, task):
            raise Exception('in log.__init__() - Object is not the right type "%s", must be "task"' % task_ob.__class__.__name__)
        self.task = task_ob
        #
        for key in self.logs_keys:
            exec('self.%s = False' % key)

    def write_log(self, logs_keys, artist_ob=False): # v2 - процедура бывшая notes_log
        """Запись лога активити задачи.
        
        Parameters
        ----------
        logs_keys : str
            Словарь по :attr:`edit_db.studio.logs_keys` - обязательные ключи: ``description``, ``version``, ``action``.
        artist_ob : :obj:`edit_db.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`.
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        pass
        # 1 - тест обязательных полей: description, version, action
        # 2 - чтение artist
        # 3 -
        # 4 - заполнение полей task_name, date_time, artist
        # 5 - запись БД
        
        # (1)
        for item in ["description", "action"]:
            if logs_keys.get(item) is False or logs_keys.get(item) is None:
                return(False, 'in log.write_log() - no "%s" submitted!' % item)
        #
        if not logs_keys['action'] in self.log_actions:
            return(False, 'in log.write_log() - wrong action - "%s"!' % logs_keys['action'])
        #	
        if not logs_keys['action'] in ['close', 'return_a_job', 'send_to_outsource', 'load_from_outsource', 'done', 'reader_accept', 'change_artist', 'recast', 'report', 'open']:
            for item in ['version']:
                if logs_keys.get(item) is False or logs_keys.get(item) is None:
                    return(False, 'in log.write_log() - no "%s" submitted!' % item)
            #
            b, r = self._template_version_num(logs_keys['version'])
            if not b:
                return(b, r)
            else:
                logs_keys['version']=r
            #
            if not logs_keys.get('branch'):
                logs_keys['branch'] = 'master'
        else:
            pass
        
        # (2)
        if not artist_ob:
            artist_ob = artist()
            bool_, r_data = artist_ob.get_user()
            if not bool_:
                return(bool_, r_data)
        
        # (3)

        # (4)
        # task_name
        if not self.task.task_name:
            return(False, 'in log.write_log() - value "self.task.task_name" not defined!')
        else:
            logs_keys['task_name'] = self.task.task_name
        #
        if not logs_keys.get('date_time'):
            logs_keys['date_time'] = datetime.datetime.now()
        #
        logs_keys['artist'] = artist_ob.nik_name
        #
        logs_keys['activity'] = self.task.activity
        
        # (5)
        table_name = '"%s:%s:logs"' % (self.task.asset.id, logs_keys['activity'])
        read_ob = self.task.asset.project
        #
        bool_, r_data = database().insert('project', read_ob, table_name, self.logs_keys, logs_keys, table_root=self.logs_db)
        if not bool_:
            return(bool_, r_data)
            
        return(True, 'ok')

    def read_log(self, action=False, branch=False): # v2
        """Чтение лога активити задачи. Заполняет :attr:`edit_db.task.branches`.
        
        Parameters
        ----------
        action : str, list, optional
            Фильтр по экшенам. Если *False* - то возврат для всех ``action``, если ``str`` (название экшена) - то все логи по данному экшену, если ``list`` (список наименований экшенов) - то будет использован оператор ``WHERE OR`` тоесть возврат по всем перечисленным экшенам.
        branch : str, optional
            Фильтр по веткам, если *False* - то вернёт логи для всех веток.
            
        Returns
        -------
        tuple
            (*True, ([список словарей логов, сотрирован по порядку], [список наименований веток])*) или (*False*, comment)
        """
        pass
        # 1 - проверка инициализации ассета.
        # 2 - проверка action
        # 3 - чтение БД.

        # (1)
        if not self.task.task_name:
            return(False, 'in log.write_log() - value "self.task.task_name" not defined!')
        
        ## (2)
        #if action and not action in self.log_actions:
            #return(False, 'in log.read_log() - wrong "action" - "%s"!' % action)
        
        # (3)
        table_name = '"%s:%s:logs"' % (self.task.asset.id, self.task.activity)
        read_ob = self.task.asset.project
        if action:
            if isinstance(action, str):
                where = {'action': action}
            elif isinstance(action, list) or isinstance(action, tuple):
                where = {'action': action, 'condition': 'or'}
        else:
            where = False
        bool_, r_data = database().read('project', read_ob, table_name, self.logs_keys, where=where, table_root=self.logs_db)
        if not bool_:
            return(bool_, r_data)
        branches = list()
        final_r_data = list()
        for item in r_data:
            branch_ = item['branch']
            if isinstance(branch_, str) or isinstance(branch_, unicode):
                branches.append(branch_)
            elif isinstance(branch_, list):
                branches.extend(branch_)
            if branch and (isinstance(branch_, str) or isinstance(branch_, unicode)) and branch_ !=branch:
                continue
            final_r_data.append(item)
        branches = list(set(branches))
        
        # fill branches
        self.task._set_branches(branches)
        
        return(True, (final_r_data, branches))

    def get_push_logs(self, task_data=False, time_to_str = False): # v2 возможно устаревшая
        """Возврат списка ``push`` логов для задачи.
        
        .. attention:: Возможно устарело!.
        
        Parameters
        ----------
        task_data : dict, optional
            Если *False* - значит текущая задача. ``лучше не использовать``
        time_to_str : bool, optional
            Если *True* - то преобразует дату в строку.
        
        Returns
        -------
        tuple
            (*True, ([список словарей логов, сотрирован по порядку], [список наименований веток])*) или (*False*, comment)
        """
        pass
        # get all logs
        if not task_data:
            bool_, r_data = self.read_log(action='push')
            if not bool_:
                return(False, r_data)
        else:
            # get asset/task
            if task_data['asset_name'] != self.task.asset.name:
                asset_ob = self.task.asset.init(task_data['asset_name'])
                task_ob = task(asset_ob)
            else:
                task_ob = task(self.task.asset)
            #
            task_ob.init_by_keys(task_data, new=False)
            # get log
            log_new = log(task_ob)
            # read log
            bool_, r_data = log_new.read_log(action='push')
            if not bool_:
                return(False, r_data)
        
        if time_to_str:
            for row in r_data[0]:
                dt = row['date_time']
                data = dt.strftime("%d-%m-%Y %H:%M:%S")
                row['date_time'] = data
                
        return(True, r_data)

    # *** ARTIST LOGS ***

    def artist_start_log(self, artist_ob=False):
        """Создание, при отсутствии, лога артиста по данной задаче, заполнение ``artist_log.start``
        
        Parameters
        ----------
        artist_ob : :obj:`edit_db.studio.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`.
        
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        pass
        # 1 - input data
        # 2 - read log 
        # 3 - write log
        
        # (1)
        if not artist_ob:
            artist_ob = artist()
            b, r = artist_ob.get_user()
            if not b:
                return(b, r)
            
        # (2)
        b, r = self.artist_read_log()
        if not b:
            return(b, r)
        if r:
            return(True, 'log allready exists!')
        
        # (3)
        if self.task.start:
            start_time = self.task.start
        else:
            start_time = datetime.datetime.now()
        write_data = {
            'project_name': self.task.asset.project.name,
            'task_name': self.task.task_name,
            'start': start_time,
            }
        table_name = '%s_tasks_logs' % artist_ob.nik_name
        b, r = database().insert('studio', self, table_name, self.artists_logs_keys, write_data, table_root=self.artists_logs_db)
        if not b:
            return(b, r)
        
        return(True, 'Ok!')

    def artist_read_log(self, all=False, artist_ob=False):
        """Чтение логов артиста.
        
        Parameters
        ----------
        all : bool, optional
            Если *True* - то все логи этого артиста, если *False* - То только по этой задаче.
        artist_ob : :obj:`edit_db.studio.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`.
            
        Returns
        -------
        tuple
            * Если ``all`` = *True* - (*True*, [список логов - словари]) или (*False*, comment).
            * Если ``all`` = *False* - (*True*, {лог - словарь}) или (*False*, comment).
        """
        pass
        # 1 - input data
        # 2 - read log
        
        # (1)
        if not artist_ob:
            artist_ob = artist()
            bool_, r_data = artist_ob.get_user()
            if not bool_:
                return(bool_, r_data)
            
        # (2)
        if all:
            where=False
        else:
            where = {'project_name': self.task.asset.project.name, 'task_name': self.task.task_name}
        b,r = database().read('studio', self, '%s_tasks_logs' % artist_ob.nik_name, self.artists_logs_keys, where=where, table_root=self.artists_logs_db)
        if not b:
            return(b, r)
        if all:
            return(b, r)
        elif r:
            return(b, r[0])
        else:
            return(b, dict())		

    def artist_write_log(self, keys, artist_ob=False):
        """Внесение изменений в лог артиста по задаче (кроме параметров из :attr:`edit_db.log.no_editable_keys`).
        
        Parameters
        ----------
        keys : dict
            Словарь данных на замену по ключам :attr:`edit_db.studio.artists_logs_keys`.
        artist_ob : :obj:`edit_db.studio.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`.
        
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        pass
        # 1 - input data
        # 2 - read log
        # 3 - write log
        
        # (1)
        if not artist_ob:
            artist_ob = artist()
            bool_, r_data = artist_ob.get_user()
            if not bool_:
                return(bool_, r_data)
        # (2)
        b, r = self.artist_read_log()
        if not b:
            return(b, r)
        if not r:
            return(False, 'The artist`s log no exists!')
        
        update_data=dict()
        for key in keys:
            if key in self.no_editable_keys:
                continue
            else:
                update_data[key]=keys[key]
        #
        if not update_data:
            return(False, 'No found data to update! (%s)' % str(keys))
                
        where = {'project_name': self.task.asset.project.name, 'task_name': self.task.task_name}
        table_name = '%s_tasks_logs' % artist_ob.nik_name
        b, r = database().update('studio', self, table_name, self.artists_logs_keys, update_data, where=where, table_root=self.artists_logs_db)
        if not b:
            return(b, r)
        
        return(True, 'Ok!')

    def artist_add_full_time(self, time, artist_ob=False):
        """Добавление временик ``full_time`` в лог артиста по задачам.
        
        Parameters
        ----------
        time : float
            Время затраченное на ``commit`` (секунды).
        artist_ob : :obj:`edit_db.studio.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`.
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment)
        """
        pass
        # 1 - input data
        # 2 - read log + added time
        # 3 - write log
        
        # (1)
        if not isinstance(time, float) and not isinstance(time, int):
            return(False, 'time - wrong type - "%s", need "float" or "int"' % time.__class__.__name__)
        if not artist_ob:
            artist_ob = artist()
            bool_, r_data = artist_ob.get_user()
            if not bool_:
                return(bool_, r_data)
        # (2)
        b, r = self.artist_read_log()
        if not b:
            return(b, r)
        if not r:
            return(False, 'The artist`s log no exists!')
        #
        if r['full_time']:
            update_data = {'full_time' : (r['full_time'] + time)}
        else:
            update_data = {'full_time' : time}
        where = {'project_name': self.task.asset.project.name, 'task_name': self.task.task_name}
        table_name = '%s_tasks_logs' % artist_ob.nik_name
        b, r = database().update('studio', self, table_name, self.artists_logs_keys, update_data, where=where, table_root=self.artists_logs_db)
        if not b:
            return(b, r)
        
        return(True, 'Ok!')
        

    # *** CAMERA LOGS ***
    def camera_write_log(self, artist_ob, description, version, task_data=False): # v2 - возможно нужна поверка существования версии ?
        """Запись лога для сохраняемой камеры шота.
        
        Parameters
        ----------
        artist_ob : :obj:`edit_db.artist`
            Никнейм данного артиста записывается в лог.
        description : str
            Комментарий.
        version : str, int
            Номер версии. ``Лучше сделать автоопределение номера``.
        task_data : dict
            Словарь данных задачи, для которой делается запись, если не передавать - то текущая. ``Лучше не использовать``.
        
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment).
        """
        pass
        # 0 - проверка user
        # 1 - заполнение task_data
        # 2 - тест обязательных полей: description, version
        # 3 - заполнение logs_keys
        # 4 - запись json
        
        # (0)
        if not isinstance(artist_ob, artist):
            return(False, 'in log.camera_write_log() - "artist_ob" parameter is not an instance of "artist" class')
        if not artist_ob.nik_name:
            return(False, 'in log.camera_write_log() - required login!')
        
        # (1)
        if not task_data:
            task_data={}
            for key in self.tasks_keys:
                exec('task_data["%s"] = self.task.%s' % (key, key))
        else:
            if not taks_data['asset_name'] == self.task.asset.name:
                return(False, 'in log.camera_write_log() - transferred "task_data" is not from the correct asset: transferred: "%s", required: "%s"' % (taks_data['asset_name'], self.task.asset.name))
                
        # (2)
        for item in [description, version]:
            if not item:
                return(False, '"%s" parameter not passed!' % item)
        
        # (3)
        logs_keys = {}
        for key in self.logs_keys:
            if key in self.tasks_keys:
                logs_keys[key] = task_data[key]
        
        str_version = '%04d' % int(version)
        logs_keys['description'] = description
        logs_keys['action'] = 'push_camera'
        logs_keys['date_time'] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        logs_keys['version'] = str_version
        logs_keys['artist'] = artist_ob.nik_name
        
        # (4)
        path = os.path.join(task_data['asset_path'], self.task.asset.ADDITIONAL_FOLDERS['meta_data'], self.camera_log_file_name)
        path = NormPath(path)
        
        data = {}
        
        if os.path.exists(path):
            with open(path, 'r') as f:
                try:
                    data = json.load(f)
                except:
                    pass
        
        data[str_version] = logs_keys
        
        with open(path, 'w') as f:
            jsn = json.dump(data, f, sort_keys=True, indent=4)
        
        return(True, 'Ok!')

    def camera_read_log(self, task_data=False): # v2
        """Чтение логов камеры шота.
        
        Parameters
        ----------
        task_data : dict
            Словарь данных задачи, для которой делается чтение логов, если не передавать - то текущая. ``Лучше не использовать``.
            
        Returns
        -------
        tuple
            (*True*, [Список словарей логов камеры, сортированы по порядку создания]) или (*False*, comment).
        """
        pass
        # 1 - заполнение task_data
        # 2 - определение пути к файлу
        # 3 - чтение json
        # 4 - сортировка
        
        # (1)
        if not task_data:
            task_data={}
            for key in self.tasks_keys:
                exec('task_data["%s"] = self.task.%s' % (key, key))
        else:
            if not taks_data['asset_name'] == self.task.asset.name:
                return(False, 'in log.camera_read_log() - transferred "task_data" is not from the correct asset: transferred: "%s", required: "%s"' % (taks_data['asset_name'], self.task.asset.name))		
        
        # (2)
        path = os.path.join(task_data['asset_path'], self.task.asset.ADDITIONAL_FOLDERS['meta_data'], self.camera_log_file_name)
        if not os.path.exists(path):
            return(False, 'No saved versions!')
            
        # (3)
        with open(path, 'r') as f:
            data = None
            try:
                data = json.load(f)
            except:
                return(False, ('problems with file versions: ' + path))
        # (4)
        nums = []
        sort_data = []
        for key in data:
            nums.append(int(key))
        nums.sort()
        
        for num in nums:
            #key = '0'*(4 - len(str(num))) + str(num)
            key = '%04d' % int(num)
            if data.get(key):
                sort_data.append(data[str(key)])
            else:
                print('*** not key')
            
        return(True, sort_data)
        
    def playblast_write_log(self, artist_ob, description, version, task_data=False): # v2
        """Запись лога создаваемого плейбласта шота.
        
        Parameters
        ----------
        artist_ob : :obj:`edit_db.artist`
            Никнейм данного артиста записывается в лог.
        description : str
            Комментарий.
        version : str, int
            Номер версии. ``Лучше сделать автоопределение номера``.
        task_data : dict
            Словарь данных задачи, для которой делается запись, если не передавать - то текущая. ``Лучше не использовать``.
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False*, comment).
        """
        pass
        # 0 - проверка user
        # 1 - заполнение task_data
        # 2 - тест обязательных полей: description, version
        # 3 - заполнение logs_keys
        # 4 - запись json
        
        # (0)
        if not isinstance(artist_ob, artist):
            return(False, 'in log.playblast_write_log() - "artist_ob" parameter is not an instance of "artist" class')
        if not artist_ob.nik_name:
            return(False, 'in log.playblast_write_log() - required login!')
        
        # (1)
        if not task_data:
            task_data={}
            for key in self.tasks_keys:
                exec('task_data["%s"] = self.task.%s' % (key, key))
        else:
            if not taks_data['asset_name'] == self.task.asset.name:
                return(False, 'in log.playblast_write_log() - transferred "task_data" is not from the correct asset: transferred: "%s", required: "%s"' % (taks_data['asset_name'], self.task.asset.name))
                
        # (2)
        for item in [description, version]:
            if not item:
                return(False, '"%s" parameter not passed!' % item)
        
        # (3)
        logs_keys = {}
        for key in self.logs_keys:
            if key in self.tasks_keys:
                logs_keys[key] = task_data[key]
        
        str_version = '%04d' % int(version)
        logs_keys['description'] = description
        logs_keys['action'] = 'playblast'
        logs_keys['date_time'] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        logs_keys['version'] = str_version
        logs_keys['artist'] = artist_ob.nik_name
        
        path = os.path.join(task_data['asset_path'], self.task.asset.ADDITIONAL_FOLDERS['meta_data'], self.playblast_log_file_name)
        path = NormPath(path)
        
        data = {}
        
        if os.path.exists(path):
            with open(path, 'r') as f:
                try:
                    data = json.load(f)
                except:
                    pass
        
        data[str_version] = logs_keys
        
        with open(path, 'w') as f:
            jsn = json.dump(data, f, sort_keys=True, indent=4)
        
        return(True, 'Ok!')

    def playblast_read_log(self, task_data=False): # v2
        """Чтение логов плейбластов шота.
        
        Parameters
        ----------
        task_data : dict
            Словарь данных задачи, для которой делается чтение логов, если не передавать - то текущая. ``Лучше не использовать``.
            
        Returns
        -------
        tuple
            (*True*, [Список словарей логов, сортированы по порядку создания]) или (*False*, comment).
        """
        pass
        # 1 - заполнение task_data
        # 2 - определение пути к файлу
        # 3 - чтение json
        # 4 - сортировка
        
        # (1)
        if not task_data:
            task_data={}
            for key in self.tasks_keys:
                exec('task_data["%s"] = self.task.%s' % (key, key))
        else:
            if not taks_data['asset_name'] == self.task.asset.name:
                return(False, 'in log.camera_read_log() - transferred "task_data" is not from the correct asset: transferred: "%s", required: "%s"' % (taks_data['asset_name'], self.task.asset.name))	
            
        # (2)
        path = os.path.join(task_data['asset_path'], self.task.asset.ADDITIONAL_FOLDERS['meta_data'], self.playblast_log_file_name)
        if not os.path.exists(path):
            return(False, 'No saved versions!')
        
        # (3)
        with open(path, 'r') as f:
            data = None
            try:
                data = json.load(f)
            except:
                return(False, ('problems with file versions: ' + path))
        
        # (4)
        nums = []
        sort_data = []
        for key in data:
            nums.append(int(key))
        nums.sort()
        
        for num in nums:
            #key = '0'*(4 - len(str(num))) + str(num)
            key = '%04d' % int(num)
            sort_data.append(data[key])
            
        return(True, sort_data)
        
    def camera_get_push_logs(self, project_name, task_data): # возможно никогда не понадобится
        pass

class artist(studio):
    '''**level** = 'studio'
    
    Данные хранимые в БД (имя столбца : тип данных) :attr:`edit_db.studio.artists_keys`:

    .. code-block:: python

        artists_keys = {
        'nik_name': 'text',
        'user_name': 'text',
        'password': 'text',
        'date_time': 'timestamp',
        'email': 'text',
        'phone': 'text',
        'specialty': 'text',
        'outsource': 'integer',
        'workroom': 'json', # список id отделов
        'level': 'text',
        'share_dir': 'text',
        'status': 'text',
        'working_tasks': 'json',# словарь списков имён назначенных задач, по именам отделов.
        'checking_tasks': 'json',# словарь списков имён назначенных на проверку задач, по именам отделов.
        }
        
    Examples
    --------
    Создание экземпляра класса:
    
    .. code-block:: python
    
        import edit_db as db
        
        artist = db.artist()
        
    Attributes
    ----------
    nik_name : str
        Никнейм (уникально).
    user_name : str
        Юзернейм в текущей системе, откуда сделан вход.
    password : str
        Пароль в текстовом виде.
    date_time : timestamp
        Дата и время регистрации в студии.
    email : str
        Email
    phone : str
        Номер телефона
    specialty : str
        Специализация.
    outsource : int
        Статус аутсорса: 0 или 1
    workroom : list
        Список id отделов, в которых сосотоит артист.
    level :  str
        Уровень, значение из :attr:`edit_db.studio.user_levels`
    share_dir : str
        Путь к директории обмена ``пока не используется``
    status : str
        Статус активности пользователя, значение из [``'active'``, ``'none'``] - ``Возможно перейти на булевские значения?``.
    working_tasks : dict
        Словарь списков имён назначенных задач, (по именам отделов ``?``).
    checking_tasks : dict
        Словарь списков имён назначенных на проверку задач, (по именам отделов ``?``).
    
    '''
    def __init__(self):
        pass
        #base fields
        for key in self.artists_keys:
            exec('self.%s = False' % key)
        #studio.__init__(self)
        pass

    def init(self, nik_name, new = True):
        """Инициализация по имени, возвращает новый, или инициализирует текущий экземпляр.
        
        Parameters
        ----------
        nik_name : str
            Ник нейм артиста.
        new : bool
            Если *True* - возвращает новый инициализированный экземпляр, если *False* то инициализирует текущий экземпляр.
            
        Returns
        -------
        :obj:`edit_db.artist`, tuple
            * если new= *True* - экземпляр класса :obj:`edit_db.artist`,
            * если new= *False* - (*True,  'Ok!'*) или (*False, comment*)
        """
        pass
        # get keys
        bool_, artists = self.read_artist({'nik_name': nik_name})
        if not bool_:
            return(bool_, artists)
                
        # fill fields
        if new:
            return artists[0]
        else:
            for key in self.artists_keys:
                #exec('self.%s = keys[0].get("%s")' % (key, key))
                setattr(self, key, getattr(artists[0], key))
            #self.asset_path = keys.get('asset_path')
            return(True, 'Ok')
        
    def init_by_keys(self, keys, new = True):
        """Инициализация по словарю (без чтения БД), возвращает новый, или инициализирует текущий экземпляр.
        
        Parameters
        ----------
        keys : dict
            Словарь по :attr:`edit_db.studio.artists_keys`
        new : bool, optional
            Если *True* - возвращает новый инициализированный экземпляр, если *False* то инициализирует текущий.
        
        Returns
        -------
        :obj:`edit_db.artist`, tuple
            * если new= *True* - экземпляр класса :obj:`edit_db.artist`,
            * если new= *False* - (*True,  'Ok!'*) или (*False, comment*)
        """
        pass
        # fill fields
        if new:
            new_artist = artist()
            for key in self.artists_keys:
                exec('new_artist.%s = keys.get("%s")' % (key, key))
            return new_artist
        else:
            for key in self.artists_keys:
                exec('self.%s = keys.get("%s")' % (key, key))
            #self.asset_path = keys.get('asset_path')
            return(True, 'Ok')

    def add_artist(self, keys, registration = True):
        """Добавление нового пользователя.
        
        Parameters
        ----------
        keys : dict
            Словарь по ключам :attr:`edit_db.studio.artists_keys`, обязательные поля - ``nik_name`` и ``password``.
        registration : bool, optional
            * Если =*True* - произойдёт заполнение полей :attr:`edit_db.studio.artists_keys` экземпляра класса, поле ``user_name`` будет заполнено.
            * Если =*False* - поля заполняться не будут, поле ``user_name`` - останется пустым.
            
        Returns
        -------
        tuple
            (*True*, 'Ok!') или (*False, comment*).
        """
        pass
        # test required fields.
        if not keys.get('nik_name'):
            return(False, '\"Nik Name\" not specified!')
        if not keys.get('password'):
            return(False, '\"Password\" not specified!')
        if not keys.get('outsource'):
            keys['outsource'] = 0

        # создание таблицы, если отсутствует.
        # определение level - если первый юзер то рут.
        # проверка на совпадение имени.
        # проверка на совпадение user_name и перезапись существующих в пустую строку.
        # запиь нового юзера
        
        # create table
        bool_, return_data = database().create_table('studio', self, self.artists_t, self.artists_keys)
        if not bool_:
            return(bool_, return_data)
        
        # read table
        bool_, return_data = database().read('studio', self, self.artists_t, self.artists_keys)
        if not bool_:
            return(bool_, return_data)
        # -- set level
        if not return_data:
            keys['level'] = 'root'
        else:
            if not keys.get('level'):
                keys['level'] = 'user'
        # -- date_time
        keys['date_time'] = datetime.datetime.now()
        # -- test exist name, user_name
        if registration:
            keys['user_name'] = getpass.getuser()
        else:
            keys['user_name'] = ''
        for item in return_data:
            # test nik_name
            if item.get('nik_name') == keys['nik_name']:
                return(False, 'User "%s" Already Exists!' % keys['nik_name'])
            # test user_name
            if registration:
                if item.get('user_name') == keys['user_name']:
                    bool_, return_data = database().update('studio', self, self.artists_t, self.artists_keys, {'user_name': ''}, {'user_name': keys['user_name']})
                    if not bool_:
                        return(bool_, return_data)
                
        # create user
        bool_, return_data = database().insert('studio', self, self.artists_t, self.artists_keys, keys)
        if not bool_:
            return(bool_, return_data)
        else:
            # fill fields
            if registration:
                for key in self.artists_keys:
                    com = 'self.%s = keys.get("%s")' % (key, key)
                    exec(com)
            return(True, 'ok')
        
    def read_artist(self, keys, objects=True):
        """Чтение списка данных артистов.
        
        Parameters
        ----------
        keys : dict
            словарь по ключам :attr:`edit_db.studio.artists_keys` - критерии для поиска, если ``keys``= 'all' вернёт данные по всем артистам.
        objects : bool, optional
            Если *True* - вернёт экземпляры :obj:`edit_db.artist`, если *False* - словари по :attr:`edit_db.studio.artists_keys`.
            
        Returns
        -------
        tuple
            (*True*, [артисты - словари или экземпляры]) или (*False, comment*)
        """
        if keys == 'all':
            keys = False
        bool_, r_data = database().read('studio', self, self.artists_t, self.artists_keys, where=keys)
        if not bool_:
            return(bool_, r_data)
        if not objects:
            return(bool_, r_data)
        else:
            objects = []
            for data in r_data:
                objects.append(self.init_by_keys(data))
            return(True, objects)
            
    def read_artist_of_workroom(self, workroom_id, objects=True):
        """Чтение списка артистов отдела.
        
        Parameters
        ----------
        workroom_id : str
            ``id`` отдела.
        objects : bool, optional
            Если *True* - вернёт экземпляры :obj:`edit_db.artist`, если *False* - словари по :attr:`edit_db.studio.artists_keys`.
        
        Returns
        -------
        tuple
            (*True*, [артисты - словари или экземпляры]) или (*False, comment*).
        """
        bool_, return_data = database().read('studio', self, self.artists_t, self.artists_keys)
        if not bool_:
            return(bool_, return_data)
        #
        artists_dict = {}
        for row in return_data:
            try:
                workrooms = row['workroom']
            except:
                continue
            if workrooms and workroom_id in workrooms:
                if objects:
                    artists_dict[row['nik_name']] = self.init_by_keys(row)
                else:
                    artists_dict[row['nik_name']] = row
        return(True, artists_dict)

    def get_artists_for_task_type(self, task_type, workroom_ob):
        """Возвращает активных артистов подходящих для данного типа задачи (сортированный список имён и словарь по именам).
        
        Parameters
        ----------
        task_type : str
            Тип задачи.
        workroom_ob : :obj:`edit_db.workroom`
            Любой экземпляр отдела, предполагается что выполнена процедура :func:`edit_db.workroom.get_list` и заполнено поле :attr:`edit_db.workroom.list_workroom` (список отделов).
        
        Returns
        -------
        tuple
            (*True*, [сортированный список имён артистов], {словарь артистов по именам}) или (*False, comment*).
        """
        pass
        artists_dict = {}
        active_artists_list = []
        for wr in workroom_ob.list_workroom:
            if task_type in wr.type:
                b, r_data = self.read_artist_of_workroom(wr.id)
                if not b:
                    print('*** problem in workroom.read_artist_of_workroom() by "%s"' % wr.name)
                    print(r_data)
                    continue
                else:
                    for artist_name in r_data:
                        if r_data[artist_name].status=='active':
                            active_artists_list.append(artist_name)
                    artists_dict.update(r_data)
        
        active_artists_list = list(set(active_artists_list))
        active_artists_list.sort()

        return(True, active_artists_list, artists_dict)
        
    def login_user(self, nik_name, password):
        """Логин юзера.\
        Перезаписывает текущее имя пользователя пк, в соответствие указанного ник-нейма, при этом проверит и удалит данное имя пользователя из под других ник-неймов.\
        Произойдёт заполнение полей :obj:`edit_db.artist.artists_keys` экземпляра класса.
        
        Parameters
        ----------
        nik_name : str
            Никнейм.
        password : str
            Пароль
            
        Returns
        -------
        tuple
            (*True*, (``nik_name``, ``user_name``))  или (*False, comment*).
        
        """
        pass
        # проверка наличия юзера
        # проверка пароля
        # очистка данного юзернейма
        # присвоение данного юзернейма пользователю
        user_name = getpass.getuser()
        bool_, user_data = database().read('studio', self, self.artists_t, self.artists_keys, where = {'nik_name': nik_name})
        if not bool_:
            return(bool_, user_data)
        # test exists user
        if not user_data:
            return(False, 'User is not found!')
        # test password
        else:
            if user_data[0].get('password') != password:
                return(False, 'Incorrect password!')
        # clean
        bool_, return_data = database().update('studio', self, self.artists_t, self.artists_keys, {'user_name': ''}, {'user_name': user_name})
        if not bool_:
            return(bool_, return_data)
        # set user_name
        bool_, return_data = database().update('studio', self, self.artists_t, self.artists_keys, {'user_name': user_name}, {'nik_name': nik_name})
        if not bool_:
            return(bool_, return_data)
        
        # fill fields
        for key in self.artists_keys:
            com = 'self.%s = user_data[0].get("%s")' % (key, key)
            #print('#'*3, item[0], com)
            exec(com)
        return(True, (nik_name, user_name))

    def get_user(self, outsource = False):
        """Определение текущего пользователя, инициализация текущего экземпляра.
        
        Parameters
        ----------
        outsource : bool
            С точки зрения удалённого пользователя или нет.
            
        Returns
        -------
        tuple
            (*True*, (``nik_name``, ``user_name``, ``outsource`` (bool), {``данные артиста - словарь``})) или (*False, comment*)
        
        """
        user_name = getpass.getuser()
        bool_, return_data = database().read('studio', self, self.artists_t, self.artists_keys, where = {'user_name': user_name})
        if not bool_:
            return(bool_, return_data)
        rows = return_data
        # conditions # return
        if not rows:
            return False, 'not user'
        elif len(rows)>1:
            return False, 'more than one user'
        else:
            # fill fields
            for key in self.artists_keys:
                setattr(self, key, rows[0].get(key))
                #com = 'self.%s = rows[0].get("%s")' % (key, key)
                #exec(com)
            if not outsource:
                return True, (rows[0]['nik_name'], rows[0]['user_name'], None, rows[0])
            else:
                if rows[0]['outsource']:
                    out_source = bool(rows[0]['outsource'])
                else:
                    out_source = False
                return True, (rows[0]['nik_name'], rows[0]['user_name'], out_source, rows[0])

    def edit_artist(self, keys, current_user=False):
        """Редактирование данного (инициализированного) экземпляра артиста.
        
        Parameters
        ----------
        keys : dict
            данные на замену - ``nik_name`` - не редактируется, не зависимо от того передан или нет.
        current_user : :obj:`edit_db.artist`, str, optional
            редактор - залогиненный пользователь, если *False* - то будет создан новый экземпляр и произведено :func:`edit_db.artist.get_user` (лишнее обращени е к БД) . если передать ``'force'`` - проверки уровней и доступов не выполняются.
            
        Returns
        -------
        tuple
            (*True*, "Ok!") или (*False, comment*)
        """
        pass
        # 1 - проверка заполненности keys
        # 2 - тест current_user
        # 3 - уровни доступа
        # 4 - запись данных в БД
        # 5 - изменение данных текущего объекта
        
        # (1)
        if not keys:
            return(False, 'No data to write!')
        
        # (2)
        if current_user != 'force':
            if current_user and not isinstance(current_user, artist):
                return(False, 'In artist.edit_artist() - wrong type of "current_user" - %s' % current_user.__class__.__name__)
            elif not current_user:
                current_user = artist()
                bool_, return_data = current_user.get_user()
                if not bool_:
                    return(bool_, return_data)
            
            # (3)
            # -- user не менеджер
            if not current_user.level in self.manager_levels:
                return(False, 'Not Access! (your level does not allow you to make similar changes)')
            # -- попытка возвести в ранг выше себя
            elif keys.get("level") and self.user_levels.index(current_user.level) < self.user_levels.index(keys.get("level")):
                return(False, 'Not Access! (attempt to assign a level higher than yourself)')
            # -- попытка сделать изменения пользователя с более высоким уровнем.
            elif self.user_levels.index(current_user.level) < self.user_levels.index(self.level):
                return(False, 'Not Access! (attempt to change a user with a higher level)')
        
        # (4)
        # update
        if 'nik_name' in keys:
            del keys['nik_name']
        bool_, return_data = database().update('studio', self, self.artists_t, self.artists_keys, keys, where = {'nik_name': self.nik_name}, table_root=self.artists_db)
        if not bool_:
            return(bool_, return_data)
        
        # (5)
        for key in self.artists_keys:
            if key in keys:
                exec('self.%s = keys.get("%s")' % (key, key))
        
        return True, 'ok'

    def get_working_tasks(self, project_ob, statuses = False):
        """Получение словаря задач (по именам) назначенных на артиста.
        
        Parameters
        ----------
        project_ob : :obj:`edit_db.project`
            Проект для которого ищется список задач.
        statuses : list
            Фильтр по статтусам (список статусов). Если не передавать - то все статусы.
            
        Returns
        -------
        tuple
            (*True*, {``task_name``: ``task_ob``, ...}) или (*False, comment*)
        """
        pass
        # 1 - получаем список всех ассетов
        # 2 - пробегаемся по списку artist.working_tasks - и инициализируем задачи.
        # 3 - возвращаем словарь по именам
        
        # (1)
        b, r = asset(project_ob).get_dict_by_name_by_all_types()
        if not b:
            return(False, r)
        assets = r
        
        # (2)
        tasks = {}		
        for task_name in self.working_tasks.get(project_ob.name):
            asset_name = task_name.split(':')[0]
            if asset_name in assets:
                task_ob = task(assets[asset_name]).init(task_name)
                if statuses and task_ob.status not in statuses:
                    continue
                tasks[task_name] = task_ob
                
        return(True, tasks)

    def get_reading_tasks(self, project_ob, status=False):
        """получение словаря задач (по именам) назначенных на артиста в качестве проверяющего.
        
        Parameters
        ----------
        project_ob : :obj:`edit_db.project`
            Проект для которого ищется список задач.
        status : str
            Возвращает задачи соответствующие данному статусу, если не передавать - то все статусы.
            
        Returns
        -------
        tuple
            (*True*, {``task_name``: ``task_ob``, ...}) или (*False, comment*)
        """
        pass
        # 1 - получаем список всех ассетов
        # 2 - пробегаемся по списку artist.checking_tasks - и инициализируем задачи.
        # 3 - возвращаем словарь по именам
        
        # (1)
        b, r = asset(project_ob).get_dict_by_name_by_all_types()
        if not b:
            return(False, r)
        assets = r
        
        # (2)
        tasks = {}
        if self.checking_tasks:
            for task_name in self.checking_tasks.get(project_ob.name):
                asset_name = task_name.split(':')[0]
                if asset_name in assets:
                    task_ob = task(assets[asset_name]).init(task_name)
                    if status and task_ob.status != status:
                        continue
                    tasks[task_name] = task_ob
                
        return(True, tasks)

class workroom(studio):
    """**level** = 'studio'

    Данные хранимые в БД (имя столбца : тип данных) :attr:`edit_db.studio.workroom_keys`:

    .. code-block:: python

        workroom_keys = {
        'name': 'text',
        'id': 'text',
        'type': 'json' # список типов задач, которые выполняются данным отделом.
        }

    Examples
    --------
    Создание экземпляра класса:

    .. code-block:: python
  
        import edit_db as db

        workroom = db.workroom()

    Attributes
    ----------
    name : str
        Имя отдела (уникально).
    id : str
        ``uuid.hex``
    type : list
        Список типов задач из :attr:`edit_db.studio.task_types`, которые выполняются данным отделом.
    """
    list_workroom = None
    """list: ``атрибут класса`` список отделов даной студии (экземпляры). Заполняется привыполнеии метода :func:`edit_db.workroom.get_list`, значение по умолчанию - ``[]``. """
    dict_by_name = None
    """dict: ``атрибут класса`` словарь отделов даной студии (экземпляры) с ключами по ``name``. Заполняется привыполнеии метода :func:`edit_db.workroom.get_list`, значение по умолчанию - ``{}``. """
    dict_by_id = None
    """dict: ``атрибут класса`` словарь отделов даной студии (экземпляры) с ключами по ``id``. Заполняется привыполнеии метода :func:`edit_db.workroom.get_list`, значение по умолчанию - ``{}``. """

    def __init__(self):
        pass
        for key in self.workroom_keys:
            exec('self.%s = False' % key)
        
    def init_by_keys(self, keys, new = True):
        """Инициализация по словарю (без чтения БД), возвращает новый, или инициализирует текущий экземпляр.
        
        Parameters
        ----------
        keys : dict
            Словарь по :attr:`edit_db.studio.workroom_keys`
        new : bool, optional
            Если *True* - возвращает новый инициализированный экземпляр, если *False* то инициализирует текущий.
        
        Returns
        -------
        :obj:`edit_db.workroom`, tuple
            * если new= *True* - экземпляр класса :obj:`edit_db.workroom`,
            * если new= *False* - (*True,  'Ok!'*) или (*False, comment*)
        """
        if new:
            new_ob = workroom()
            for key in self.workroom_keys:
                exec('new_ob.%s = keys.get("%s")' % (key, key))
            return new_ob
        else:
            for key in self.workroom_keys:
                exec('self.%s = keys.get("%s")' % (key, key))
            return(True, 'Ok')

    def add(self, keys, new=False):
        """Создание отдела.
        
        Parameters
        ----------
        keys : dict
            Словарь ключей по :attr:`edit_db.studio.workroom_keys`, ``name`` - обязательный параметр.
        new : bool, optional
            Если *True* - то возвращает инициализированный экземпляр.

        Returns
        -------
        :obj:`edit_db.workroom`, tuple
            * Если new= *True* - экземпляр класса :obj:`edit_db.workroom`.
            * Если new= *False* - (*True,  'Ok!'*) или (*False, comment*).
        """
        pass
        # test name
        try:
            name = keys['name']
        except:
            return(False, 'not Name!')
            
        keys['id'] = uuid.uuid4().hex
        
        # 1 - создание таблицы, если отсутствует. чтобы без вылетов сработала проверка на совпадение имени.
        # 2 - проверка на совпадение имени
        # 3 - проверка чтобы типы задач были из task_types
        # 4 - запись строки в таблицу
        
        # (1) create table 
        bool_, return_data = database().create_table('studio', self, self.workroom_t, self.workroom_keys, table_root = self.workroom_db)
        if not bool_:
            return(bool_, return_data)
        
        # (2) test exists name
        bool_, return_data = database().read('studio', self, self.workroom_t, self.workroom_keys, where={'name': name}, table_root=self.workroom_db)
        if not bool_:
            return(bool_, return_data)
        elif return_data:
            return(False, 'This workroom name: "%s" already exists!' % name)
        
        # (3) test type
        type_ = keys.get('type')
        if type_:
            if type_.__class__.__name__ == 'list':
                for item in type_:
                    if not item in self.task_types:
                        return(False, 'This type of task: "%s" is not correct!' % item)
            else:
                return(False, 'This type of keys[type]: "%s" is not correct (must be a list, False or None)' % str(type_))
            
        # (4) insert string
        bool_, return_data = database().insert('studio', self, self.workroom_t, self.workroom_keys, keys, table_root=self.workroom_db)
        if not bool_:
            return(bool_, return_data)
        
        if not new:
            return(True, 'ok')
        else:
            return(self.init_by_keys(keys, True))
        
    def get_list(self, return_type = False, objects=True):
        """Получение списка отделов.

        .. note:: Заполняет ``атрибуты класса``: :attr:`edit_db.workroom.list_workroom`, :attr:`edit_db.workroom.dict_by_name`, :attr:`edit_db.workroom.dict_by_id`.

        .. attention:: Учитывая вышесказанное - про заполнение атрибутов класса - история с ``return_type`` излишня - достаточно возвращать тру-ок.

        Parameters
        ----------
        return_type : str
            параметр определяющий структуру возвращаемой информации значения из [*False*, ``'by_name'``, ``'by_id'``]. 
        objects : bool
            Определяет в каком виде возвращаются отделы, если *False* - то словари, а если *True* - то экземпляры класса :obj:`edit_db.workroom`.

        Returns
        -------
        tuple
            * Если return_type= *False* - (*True*, [список отделов (экземпляры или словари)]) или (*False, comment*).
            * Если return_type= ``'by_name'`` - (*True*, {словарь по ``name`` - значения отделы (экземпляры или словари)}) или (*False, comment*).
            * Если return_type= ``'by_id'`` - (*True*, {словарь по ``id`` - значения отделы (экземпляры или словари)}) или (*False, comment*).
        """
        pass
        bool_, return_data = database().read('studio', self, self.workroom_t, self.workroom_keys, table_root=self.workroom_db)
        if not bool_:
            return(bool_, return_data)

        return_data_0 = {}
        return_data_1 = []
        return_data_2 = {}
        for row in return_data:
            #return_data['name'] = row['name']
            work_room_data = {}
            work_room_data_1 = {}
            work_room_data_2 = {}
            if objects:
                wr_data = self.init_by_keys(row)
            else:
                wr_data = row
            return_data_0[row['name']] = wr_data
            return_data_1.append(wr_data)
            return_data_2[row['id']] = wr_data
        
        # fill fields
        self._fill_fields_of_workroom_class(return_data_1, return_data_0, return_data_2)
        
        # return
        if not return_type:
            return(True, return_data_1)
        elif return_type == 'by_name':
            return(True, return_data_0)
        elif return_type == 'by_id':
            return(True, return_data_2)
        elif return_type == 'by_id_by_name':
            return(True, return_data_2, return_data_0)
        else:
            return(False, ('Incorrect "return_type": %s' % return_type))
        
    @classmethod
    def _fill_fields_of_workroom_class(self, list_workroom, dict_by_name, dict_by_id):
        pass
        self.list_workroom = list_workroom
        self.dict_by_name = dict_by_name
        self.dict_by_id = dict_by_id


    def get_name_by_id(self, id_):
        """Возвращает имя отдела по его ``id``. Обращение к БД.
  
        .. attention:: Возможно лучше не использовать, или переписать без обращения к БД - чисто через класс атрибуты.

        Parameters
        ----------
        id_ : str
            ``id`` отдела.

        Returns
        -------
        tuple
            (*True*, workroom_name) или (*False, комментарий*).
        """
        where = {'id': id_}
        bool_, return_data = database().read('studio', self, self.workroom_t, self.workroom_keys, columns = ['name'], where = where, table_root=self.artists_db)
        if not bool_:
            return(bool_, return_data)
        else:
            if return_data:
                return(True, return_data[0]['name'])
            else:
                print('#'*3, 'workroom.get_name_by_id() - id is incorrect!')
                print('#'*3, 'id:', id_)
                return(False, 'Look the terminal!')

    def get_id_by_name(self, name):
        """Возвращает ``id`` отдела по его имени. Обращение к БД.

        .. attention:: Возможно лучше не использовать, или переписать без обращения к БД - чисто через класс атрибуты.

        Parameters
        ----------
        name : str
            ``name`` отдела.

        Returns
        -------
        tuple
            (*True*, workroom_id) или (*False, комментарий*).
        """
        where = {'name': name}
        bool_, return_data = database().read('studio', self, self.workroom_t, self.workroom_keys, columns = ['id'], where = where, table_root=self.artists_db)
        if not bool_:
            return(bool_, return_data)
        else:
            if return_data:
                return(True, return_data[0]['id'])
            else:
                print('#'*3, 'workroom.get_id_by_name() - name is incorrect!')
                print('#'*3, 'name:', name)
                return(False, 'Look the terminal!')

    def name_list_to_id_list(self, name_list):
        """Возвращает список ``id`` отделов по списку имён. Обращение к БД.

        .. attention:: Возможно лучше не использовать, или переписать без обращения к БД - чисто через класс атрибуты.

        Parameters
        ----------
        name_list : list
            Список имён отделов.

        Returns
        -------
        tuple
            (*True*, list_of_id) или (*False, comment*).
        """
        bool_, data = self.get_list('by_name', False)
        if not bool_:
            return(bool_, data)
        if data:
            return_data = []
            for key in data:
                if key in name_list:
                    return_data.append(data[key]['id'])
            return(True, return_data)
        else:
            print('#'*3, 'workroom.name_list_to_id_list() - list of names is incorrect!')
            print('#'*3, 'name list:', name_list)
            return(False, 'Look the terminal!')

    def id_list_to_name_list(self, id_list):
        """Возвращает список имён отделов по списку ``id``. Обращение к БД.

        .. note:: Используется при записи.

        .. attention:: Возможно лучше не использовать, или переписать без обращения к БД - чисто через класс атрибуты.

        Parameters
        ----------
        id_list : list
            Список ``id`` отделов.

        Returns
        -------
        tuple
            (*True*, list_of_names) или (*False, comment*).
        """
        bool_, data = self.get_list('by_id', False)
        if not bool_:
            return(bool_, data)
        if data:
            return_data = []
            for key in data:
                if key in id_list:
                    return_data.append(data[key]['name'])
            return(True, return_data)
        else:
            print('#'*3, 'workroom.id_list_to_name_list() - list of id is incorrect!')
            print('#'*3, 'id list:', id_list)
            return(False, 'Look the terminal!')
            
    def rename_workroom(self, new_name):
        """Переименование отдела (текущего экземпляра).  Перезапись параметра :attr:`edit_db.workroom.name`.

        Parameters
        ----------
        new_name : str
            Новое имя отдела.

        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*).
        """
        new_name = new_name.replace(' ', '_')
        
        # 1 - проверка имени на совпадение, со старым и с имеющимися
        # 2 - запись данных в БД
        # 3 - перезапись name текущего объекта.
        
        # (1)
        if self.name == new_name:
            return(False, 'Match names!')
        bool_, return_data = self.get_list('by_name', False)
        if not bool_:
            return(bool_, return_data)
        if new_name in return_data:
            return(False, 'This name of workroom already exists! "%s"' % new_name)
        
        # (2)
        update_data = {'name':new_name}
        where = {'id': self.id}
        bool_, return_data = database().update('studio', self, self.workroom_t, self.workroom_keys, update_data, where, table_root=self.workroom_db)
        if not bool_:
            return(bool_, return_data)
        
        # (3)
        self.name = new_name
        
        return(True, 'Ok!')

    def edit_type(self, new_type_list):
        """Замена типов задач с которыми работает данный отдел (текущий экземпляр). Перезапись параметра :attr:`edit_db.workroom.type`.

        Parameters
        ----------
        new_type_list : list
            Список типов задач для отдела. Типы задач - значения из :attr:`edit_db.studio.task_types`.

        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*).
        """
        pass
        # (1) test type
        if new_type_list:
            if new_type_list.__class__.__name__ == 'list':
                for item in new_type_list:
                    if not item in self.task_types:
                        return(False, 'This type of task: "%s" is not correct!' % item)
            else:
                return(False, 'This type of keys[type]: "%s" is not correct (must be a list, False or None)' % str(new_type_list))
        # (2)
        update_data = {'type': new_type_list}
        where = {'id': self.id}
        bool_, return_data = database().update('studio', self, self.workroom_t, self.workroom_keys, update_data, where, table_root=self.workroom_db)
        if not bool_:
            return(bool_, return_data)
        self.type = new_type_list
        return(True, 'Ok!')

class chat(studio):
    '''**level** = 'project'

    Данные хранимые в БД (имя столбца : тип данных) :attr:`edit_db.studio.chats_keys`:

    .. code-block:: python

        chats_keys = {
        'message_id':'text',
        'date_time': 'timestamp',
        'date_time_of_edit': 'timestamp',
        'author': 'text',
        'topic': 'json',
        'color': 'json',
        'status': 'text',
        'reading_status': 'json',
        }

    Examples
    --------
    Создание экземпляра класса:

    .. code-block:: python
  
        import edit_db as db

        project = db.project()
        asset = db.asset(project)
        task = db.task(asset)

        chat = db.chat(task) # task - обязательный параметр при создании экземпляра chat
        # доступ ко всем параметрам и методам принимаемого экземпляра task - через chat.task

    Attributes
    ----------
    message_id : str
        ``id`` сообщения
    date_time : timestamp
        Время и дата создания записи.
    date_time_of_edit : timestamp
        Время и дата изменения записи.
    author : str
        ``nik_name`` автора записи.
    topic : dict
        Словарь данных сообщения, ключи - номера строк в ковычках, значения - список из трёх значений: путь к изображению, путь к иконке изображения, сообщение.\
        {``'num_line'`` : [``path_to_img``, ``path_to_icon``, ``message``], ...}
    color : list
        ``[r,g,b]`` значения цвета от ``0`` до ``1``.
    status : str
        Статус.
    reading_status : dict
        ``??``
    task : :obj:`edit_db.task`
        Экземпляр задачи принимаемый при создании экземпляра класса, содержит все атрибуты и методы :obj:`edit_db.task`.
    '''
    def __init__(self, task_ob):
        if not isinstance(task_ob, task):
            raise Exception('in chat.__init__() - Object is not the right type "%s", must be "task"' % task_ob.__class__.__name__)
        self.task = task_ob
        # 
        for key in self.chats_keys:
            exec('self.%s = False' % key)

    def record_messages(self, input_keys, artist_ob=False): # v2
        """Запись сообщения в чат для задачи.

        Parameters
        ----------
        input_keys : dict
            Словарь по :attr:`edit_db.studio.chats_keys` - обязательные ключи: ``'topic'``, ``'color'``, ``'status'``, ``'reading_status'``.  ``??????? список обязательных полей будет пересмотрен``
        artist_ob : :obj:`edit_db.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`, обращение к БД.

        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*).
        """
        pass
        # 1 - artist_ob test
        # 2 - тест обязательных полей
        # 3 - datetime, message_id
        # 4 - запись БД
        
        # (1)
        if artist_ob and not isinstance(artist_ob, artist):
            return(False, 'in chat.record_messages() - Wrong type of "artist_ob"! - "%s"' % artist_ob.__class__.__name__)
        elif artist_ob:
            if not artist_ob.nik_name:
                return(False, 'in chat.record_messages() - User is not logged in!')
            input_keys['author'] = artist_ob.nik_name
        elif not artist_ob:
            artist_ob = artist()
            bool_, r_data = artist_ob.get_user()
            if not bool_:
                return(bool_, r_data)
            input_keys['author'] = artist_ob.nik_name
            
        # (2)
        for item in ['topic','color','status', 'reading_status']:
            if not input_keys.get(item):
                return(False, 'in chat.record_messages() - missing "%s"!' % item)
            
        # (3)
        input_keys['date_time_of_edit'] = input_keys['date_time'] = datetime.datetime.now()
        input_keys['message_id'] = uuid.uuid4().hex
        
        # (4)
        table_name = '"%s"' % self.task.task_name
        read_ob = self.task.asset.project
        #
        bool_, r_data = database().insert('project', read_ob, table_name, self.chats_keys, input_keys, table_root=self.chats_db)
        if not bool_:
            return(bool_, r_data)
        
        return(True, 'ok')

    def read_the_chat(self, message_id=False, sort_key=False, reverse = False): # v2
        """Чтение сообщений чата задачи.

        Parameters
        ----------
        message_id : str, optional
            ``id`` читаемого сообщения, если *False* - то читаются все сообщения чата.
        sort_key : str, optional
            Ключ по которому сортируется список. Если  *False* то сортировки не происходит.
        reverse : bool
            Если *True* - то делается реверсивная сортировка, имеет смысл только если передаётся ``sort_key``. ``!!! Пока не испоьзуется``.

        Returns
        -------
        tuple
            (*True*, [messages (словари)]) или (*False, comment*)
        """
        pass
        # 1 - чтение БД
        
        # (1)
        table_name = '"%s"' % self.task.task_name
        if message_id:
            where = {'message_id': message_id}
            return(database().read('project', self.task.asset.project, table_name, self.chats_keys, where = where, table_root = self.chats_db))
        else:
            b, r = database().read('project', self.task.asset.project, table_name, self.chats_keys, table_root = self.chats_db)
            if not b:
                return(b, r)
            if sort_key:
                topics = sorted(r, key=lambda x: x[sort_key], reverse=reverse)
                return(True, topics)
            else:
                return(b, r)

        '''
        table = '\"' + task_name + '\"'
        
        try:
            conn = sqlite3.connect(self.chat_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
        except:
            return False, '".chats.db" not Connect!'
        
        # read the topic
        try:
            str_ = 'select * from ' + table
            c.execute(str_)
            rows = c.fetchall()
            
        except:
            conn.close()
            return False, ('topic with name ' + table + ' not Found!')
        
        conn.close()
                
        return(True, rows)
        '''

    def edit_message(self, message_id, new_data, artist_ob=False):
        """Изменение записи автором сообщения.

        Parameters
        ----------
        message_id : str
            ``id`` редактируемого сообщения.
        new_data : dict
            Словарь данных на замену - ``topic``, ``color``.
        artist_ob : :obj:`edit_db.artist`, optional
            Текущий пользователь, если не передавать, будет сделано :func:`edit_db.artist.get_user`, обращение к БД.

        Returns
        -------
        tuple
            (*True, 'Ok!'*) или (*False, comment*).
        """
        VALID_DATA = ['topic', 'color']
        # 0 - тест new_data
        # 1 - artist_ob test
        # 2 - проверка автора
        # 3 - запись изменений
        
        # (0)
        removed_keys = []
        for key in new_data:
            if not key in ['topic', 'color']:
                removed_keys.append(key)
        for key in removed_keys:
            del new_data[key]
        
        # (1)
        if artist_ob and not isinstance(artist_ob, artist):
            return(False, 'in chat.record_messages() - Wrong type of "artist_ob"! - "%s"' % artist_ob.__class__.__name__)
        elif artist_ob and not artist_ob.nik_name:
            return(False, 'in chat.record_messages() - User is not logged in!')
        elif not artist_ob:
            artist_ob = artist()
            bool_, r_data = artist_ob.get_user()
            if not bool_:
                return(bool_, r_data)
            
        # (2)
        bool_, r_data = self.read_the_chat(message_id=message_id)
        if not bool_:
            return(bool_, r_data)
        message = r_data[0]
        if message['author'] != artist_ob.nik_name:
            return(False, 'Only author can edit messages!')
            
        # (3)
        new_data['date_time_of_edit'] = datetime.datetime.now()
        read_ob = self.task.asset.project
        table_name = '"%s"' % self.task.task_name
        where = {'message_id': message_id}
        
        bool_, r_data = database().update('project', read_ob, table_name, self.chats_keys, new_data, where=where, table_root=self.chats_db)
        if not bool_:
            return(bool_, r_data)
        
        return(True, 'Ok!')
	
class set_of_tasks(studio):
    """**level** = 'studio'

    Редактирование наборов задач.

    Данные хранимые в БД (имя столбца : тип данных) :attr:`edit_db.set_of_tasks.set_of_tasks_keys`:

    .. code-block:: python

        set_of_tasks_keys = {
        'name':'text',
        'asset_type': 'text',
        'loading_type': 'text',
        'sets':'json',
        'edit_time': 'timestamp',
        }
        
    Структура словарей атрибута :attr:`edit_db.set_of_tasks.sets_keys`:
        
    .. code-block:: python

        sets_keys = [
        'task_name',
        'input',
        'activity',
        'tz',
        'cost',
        'standart_time',
        'task_type',
        'extension',
        ]

    Attributes
    ----------
    name : str
        Имя сета (уникально).
    asset_type : str
        Тип ассета из :attr:`edit_db.studio.asset_types`.
    loading_type : str
        Способ загрузки ассета для типа ``object``, значения из :attr:`edit_db.studio.loading_types`.
    sets : list
        Сами задачи, список словарей с ключами по :attr:`edit_db.set_of_tasks.sets_keys` (ключи соответсвую атрибутам класса :obj:`edit_db.task`).
    edit_time : timestamp
        Дата и время последних изменений.
    """

    set_of_tasks_keys = {
    'name':'text',
    'asset_type': 'text',
    'loading_type':'text',
    'sets':'json',
    'edit_time': 'timestamp',
    }
    """dict: Обозначение данных хранимых в БД для объектов edit_db.set_of_tasks . Ключи - заголовки, значения - тип данных БД. """

    sets_keys = [
    'task_name',
    'input',
    'activity',
    'specification',
    'cost',
    'standart_time',
    'task_type',
    'extension',
    ]
    """list: Ключи таблицы для задач, которые хранятся в :attr:`edit_db.set_of_tasks.sets`. Это частичная выборка из :attr:`edit_db.studio.tasks_keys`. """

    def __init__(self):
        for key in self.set_of_tasks_keys:
            setattr(self, key, False)

    def init_by_keys(self, keys, new=True): # v2
        """Инициализация по словарю (без чтения БД), возвращает новый, или инициализирует текущий экземпляр.
        
        Parameters
        ----------
        keys : dict
            Словарь по :attr:`edit_db.set_of_tasks.set_of_tasks_keys`.
        new : bool, optional
            Если *True* - возвращает новый инициализированный экземпляр, если *False* то инициализирует текущий.
        
        Returns
        -------
        :obj:`edit_db.set_of_tasks`, tuple
            * если new= *True* - экземпляр класса :obj:`edit_db.set_of_tasks`,
            * если new= *False* - (*True,  'Ok!'*) или (*False, comment*).
        """
        if new:
            r_ob = set_of_tasks()
        else:
            r_ob = self
            
        for key in self.set_of_tasks_keys:
            setattr(r_ob, key, keys.get(key))
            
        if new:
            return r_ob
        else:
            return(True, 'Ok!')

    def create(self, name, asset_type, loading_type=False, keys = False, force=False): # v2
        """Создание набора задач.

        Parameters
        ----------
        name : str
            Имя набора задач.
        asset_type : str
            Тип ассета. Значение из :attr:`edit_db.studio.asset_types`.
        loading_type : str, optional
            Способ загрузки ассета для типа ``object``, значения из :attr:`edit_db.studio.loading_types`.
        keys : list
            Список задач(словари по :attr:`edit_db.set_of_tasks.sets_keys`), если *False* - будет создан пустой набор.
        force : bool
            Если *False* - то будет давать ошибку при совпадении имени, если *True* - то будет принудительно перименовывать с подбором номера.

        Returns
        -------
        tuple
            (*True*, :obj:`edit_db.set_of_tasks`) или (*False, comment*).
        """
        pass
        # 1 - тесты передаваемых имени и типа ассета
        # 2 - чтение наборов на определение совпадения имени + создание нового имени при force=True
        # 3 - запись
        
        # (1)
        # test data
        if not name:
            return(False, 'Not Name!')
        
        # (2)
        b, r = self.get_list(f = {'name': name})
        if not b:
            print(r)
        elif r and not force:
            return(False, 'A set with that name "%s" already exists' % name)
        elif r and force:
            num = 0
            while r:
                num+=1
                new_name = '%s.%i' % (name, num)
                b, r = self.get_list(f = {'name': new_name})
                if not b:
                    return(b, r)
                print(new_name)
            name = new_name
        
        if not asset_type in self.asset_types:
            return(False, 'Wrong type of asset: "%s"' % asset_type)
        
        # (3)
        # edit data
        data = {}
        data['name'] = name
        data['asset_type'] = asset_type
        if loading_type:
            data['loading_type'] = loading_type
        else:
            data['loading_type'] = ''
        data['edit_time'] = datetime.datetime.now()
        if keys:
            data['sets'] = keys

        # write data
        bool_, r_data = database().insert('studio', self, self.set_of_tasks_t, self.set_of_tasks_keys, data, table_root=self.set_of_tasks_db)
        if not bool_:
            return(bool_, r_data)
        
        return(True, self.init_by_keys(data))

    def get_list(self, f = False, path = False): # v2
        """Чтение всех наборов (экземпляры) из БД или из файла.

        Parameters
        ----------
        f : dict, optional
            Фильтр ро ключам :attr:`edit_db.set_of_tasks.set_of_tasks_keys`, используется только для чтения из базы данных при ``path`` = *False*.
        path : str, optional
            Путь до ``.json`` файла, если указан - то чтение из файла, если *False* - то чтение из базы данных.

        Returns
        -------
        tuple
            (*True, [список экземпляров]*) или (*False, comment*)
        """
        pass
        # 1 - чтение из базы данных
        # 2 - чтение из json
        data = []
        
        # (1)
        if not path:
            if f:
                wh = f
            else:
                wh = False
            bool_, r_data = database().read('studio', self, self.set_of_tasks_t, self.set_of_tasks_keys, where=wh, table_root=self.set_of_tasks_db)
            if not bool_:
                return(False, r_data)
            
            ## преобразование в словарь
            #for set_ in r_data:
                #data[set_['name']] = set_
                
            for item in r_data:
                data.append(self.init_by_keys(item))
        
        # (2)
        else:
            if not os.path.exists(path):
                return(False, ('No Exists path: %s' % path))
            # read data
            try:
                with open(path, 'r') as read:
                    r_data = json.load(read)
                    read.close()
            except Exception as e:
                print('#'*5, e)
                return(False, ("%s can not be read! Look The terminal!" % path))
            
            for key in r_data:
                item = r_data[key]
                item['name'] = key
                data.append(self.init_by_keys(item))
            
        return(True, data)
        
    def get_list_by_type(self, asset_type): # v2
        """Чтение наборов (объекты) определённого типа (обёртка на :func:`edit_db.set_of_tasks.get_list`).

        Parameters
        ----------
        asset_type : str
            Тип ассета, значение из :attr:`edit_db.studio.asset_types`.

        Returns
        -------
        tuple
            (*True, [список экземпляров]*) или (*False, comment*)
        """
        if not asset_type in self.asset_types:
            return(False, 'Wrong type of asset: "%s"' % asset_type)
        return_list = []
        return(self.get_list(f = {'asset_type': asset_type}))
        
    def get_dict_by_all_types(self): # v2
        """Чтение всех наборов из БД (экземпляры) в словарь с ключами по типам ассетов.

        Returns
        -------
        tuple
            (*True*, {return_dict} [15]_) или (*False, comment*)

            .. [15] Структура словаря ``{return_dict}`` :
            
                ::
                
                    {
                    'asset_type': {
                        'set_name' : set_instanse,
                        ...
                        },
                    ...
                    }
        """
        result = self.get_list()
        if not result[0]:
            return(False, result[1])
        
        return_list = {}
        for item in result[1]:
            asset_type = item.asset_type
            if not asset_type in return_list:
                return_list[asset_type] = {}
            
            return_list[asset_type][item.name] = item
                
        return(True, return_list)

    # возвращает новый объект по имени, обёртка на get_list(f)
    # name (str) имя сета
    def get(self, name): # v2
        pass
        # test data
        if not name:
            return(False, 'Not Name!')
        bool_, r_data = self.get_list(f = {'name': name})
        if not bool_:
            return(False, r_data)
        
        if not r_data:
            return(False, 'A set with that name "%s" was not found' % name)
        else:
            return(True, r_data[0])

    # удаление из базы данных
    # name (str) - если False - то удаляется текущий инициализированный объект: удаляется строка из БД - поля объекта переписываются на False.
    def remove(self, name=False): # v2
        pass
        # 1 - удаление записи из БД
        # 2 - перезапись полей в False - если name=False

        # (1)
        if name:
            where = {'name': name}
        else:
            where = {'name': self.name}
        bool_, r_data = database().delete('studio', self, self.set_of_tasks_t, where, table_root=self.set_of_tasks_db)
        if not bool_:
            return(False, r_data)
        
        # (2)
        if not name:
            for key in self.set_of_tasks_keys:
                setattr(self, key, False)
        
        return(True, 'ok')

    # new_name (str) - новое имя сета
    # name (str) - имя переименоваваемого сета, если False - переименовывается текущий объект.
    def rename(self, new_name, name=False): # v2
        pass
        # 1 - тест на наличие и совпадение имени
        # 2 - перезапись БД
        # 3 - перезапись полей текущего объекта

        # (1)
        if not new_name:
            return(False, 'No new name is specified!')
        
        if name:
            old_name = name
        else:
            old_name = self.name
            if not old_name:
                return(False, 'This object is not initialized!')
            
        if old_name == new_name:
            return(False, 'New name matches existing one!')
        
        # (2)
        table_name = self.set_of_tasks_t
        keys = self.set_of_tasks_keys
        update_data = {'name': new_name, 'edit_time':datetime.datetime.now()}
        where = {'name': old_name}
        bool_, r_data = database().update('studio', self, table_name, keys, update_data, where, table_root=self.set_of_tasks_db)
        if not bool_:
            return(False, r_data)
        
        # (3)
        if not name:
            self.name = new_name
            self.edit_time = update_data['edit_time']
            
        return(True, 'ok')
        
    # asset_type (str) - новый тип сета
    # name (str/bool) - имя изменяемого сета, если False - то редактируется текущий объект
    def edit_asset_type(self, asset_type, name=False): # v2
        pass
        # 1 - тест имени и типа
        # 2 - перезапись БД
        # 3 - перезапись полей текущего объекта

        # (1)
        if name:
            old_name = name
        else:
            old_name = self.name
            if not old_name:
                return(False, 'This object is not initialized!')
        
        if not asset_type in self.asset_types:
            return(False, 'Wrong type of asset: "%s"' % asset_type)	
                
        # (2)
        table_name = self.set_of_tasks_t
        keys = self.set_of_tasks_keys
        update_data = {'asset_type': asset_type, 'edit_time':datetime.datetime.now()}
        where = {'name': old_name}
        bool_, r_data = database().update('studio', self, table_name, keys, update_data, where, table_root=self.set_of_tasks_db)
        if not bool_:
            return(False, r_data)
        
        # (3)
        if not name:
            self.asset_type = asset_type
            self.edit_time = update_data['edit_time']
            
        return(True, 'ok')

    # только для ассетов "object" - редактирование параметра loading_type
    # loading_type (str) - новый тип загрузки ассета
    def edit_loading_type(self, loading_type): # v2
        pass
        # 1 - тест имени и типа
        # 2 - перезапись БД
        # 3 - перезапись полей текущего объекта

        # (1)
        if not loading_type in self.loading_types:
            return(False, 'Wrong loading type: "%s"' % loading_type)
        elif self.asset_type != 'object':
            return(False, 'This procedure can only be for an asset with an "object" type!')
                
        # (2)
        table_name = self.set_of_tasks_t
        keys = self.set_of_tasks_keys
        update_data = {'loading_type': loading_type, 'edit_time':datetime.datetime.now()}
        where = {'name': self.name}
        bool_, r_data = database().update('studio', self, table_name, keys, update_data, where, table_root=self.set_of_tasks_db)
        if not bool_:
            return(False, r_data)
        
        # (3)
        self.loading_type = loading_type
        self.edit_time = update_data['edit_time']
            
        return(True, 'ok')

    # редактирование именно значения sets
    # data (list) - список словарей по sets_keys
    # name (bool/str) - если False - то редактируется текущий инициализированный объект
    def edit_sets(self, data, name=False): # v2
        pass
        # 1 - тест типа данных data
        # 2 - перезапись БД
        # 3 - редактирование инициализированного объекта, если name=False
        
        # (1)
        if not isinstance(data, list):
            return(False, 'the "data" must be of type "list" but not "%s"' % data.__class__.__name__)
        
        # (2)
        table_name = self.set_of_tasks_t
        keys = self.set_of_tasks_keys
        update_data = {'sets': data, 'edit_time':datetime.datetime.now()}
        if name:
            where = {'name': name}
        else:
            where = {'name': self.name}
        bool_, r_data = database().update('studio', self, table_name, keys, update_data, where, table_root=self.set_of_tasks_db)
        if not bool_:
            return(False, r_data)
        
        # (3)
        if not name:
            self.sets = data
            self.edit_time = update_data['edit_time']
                
        return(True, 'ok')

    # создание копии сета
    # new_name (str) - имя создаваемого сета
    # old_name (bool / str) - имя копируемого сета, если False - то копируется текущий.
    def copy(self, new_name, old_name=False): # v2
        pass
        # 1 - тесты имён
        # 2 - создание нового сета
        
        # (1)
        if old_name == new_name:
            return(False, 'Matching names!')
        if not new_name:
            return(False, 'Name not specified!')
        
        # (2)
        if old_name:
            b, source_ob = self.get(old_name)
            if not b:
                return(b, source_ob)
        else:
            source_ob = self
            
        b, r_data = self.create(new_name, source_ob.asset_type, keys = source_ob.sets)
        return(b, r_data) # если  b=True, то r_data - новый объект.
        
    ### ****************** Library

    # запись в файл json библиотеки наборов задач.
    # path (str) - путь сохранения
    # save_objects (list) - список объектов (set_of_tasks) - если False - то сохраняет всю библиотеку.
    def save_to_library(self, path, save_objects=False): # v2
        pass
        # 1 - получение save_objects
        # 2 - создание словаря save_data по типу json файла
        # 3 - запись данных
        
        # (1)
        if not save_objects:
            b, r = self.get_list()
            if not b:
                return(b, r)
            save_objects = r
            
        # (2)
        save_data = {}
        for ob in save_objects:
            save_data[ob.name] = {}
            for key in self.set_of_tasks_keys:
                if key=='edit_time':
                    continue
                save_data[ob.name][key] = getattr(ob, key)
        
        # (3)
        try:
            with open(path, 'w') as f:
                jsn = json.dump(save_data, f, sort_keys=True, indent=4)
                f.close()
        except Exception as e:
            print('***', e)
            return(False, (path + "  can not be write"))
        
        return(True, 'ok')
    	
class season(studio):
	def __init__(self, project_ob):
		seasons_list = []
		dict_by_name = {}
		dict_by_id = {}
		
		if not isinstance(project_ob, project):
			raise Exception('in season.__init__() - Object is not the right type "%s", must be "project"' % project_ob.__class__.__name__)
		self.project = project_ob
		# fill fields
		for key in self.season_keys:
			#exec('self.%s = False' % key)
			setattr(self, key, False)
	
	def init(self, name, new=True):
		pass
		# 1 - чтение БД
		# 2 - инициализация по keys
		
		bool_, r_data = database().read('project', self.project, self.season_t, self.season_keys, where={'name': name}, table_root=self.season_db)
		if not bool_:
			return(bool_, r_data)
		if r_data:
			return self.init_by_keys(r_data[0], new=new)
		else:
			if new:
				return None
			else:
				return(False, 'a season with this name "%s" no found!')
		
	
	# заполнение полей по self.season_keys - для передачи экземпляра в уровень ниже.
	# keys (dict) словарь по self.season_keys
	# new (bool) - если True - вернёт новый объект, если False - инициализирует текущий.
	def init_by_keys(self, keys, new=True):
		if new:
			r_ob = season(self.project)
		else:
			r_ob = self
		for key in self.season_keys:
			#exec('self.%s = keys.get("%s")' % (key, key))
			setattr(r_ob, key, keys.get(key))
			
		if new:
			return r_ob
		else:
			return(True, 'Ok!')
		
	
	def create(self, name):
		keys = {}
		keys['name'] = name
		keys['status'] = 'active'
		keys['id'] = uuid.uuid4().hex
		
		# создание таблицы, если не существует. - (не нужно)
		# проверка на существование с даныи именем.
		# добавление сезона.
		
		# проверка на совпадение имени
		ob = self.init(name)
		if isinstance(ob, season):
			return(False, 'Season with this name(%s) already exists!' % keys['name'])
		
		# -- write data
		bool_, return_data = database().insert('project', self.project, self.season_t, self.season_keys, keys, table_root = self.season_db)
		if not bool_:
			return(bool_, return_data)
		return(True, self.init_by_keys(keys))
	
	# status (str) - значения из ['all', 'active', 'none']
	def get_list(self, status='all'):
		pass
	
		#
		if not status in ['all', 'active', 'none']:
			return(False, 'This status (%s) is not correct.' % status)
		
		#
		seasons_list = []
		dict_by_name = {}
		dict_by_id = {}
		
		where = False
		# write season to db
		b, r = database().read('project', self.project, self.season_t, self.season_keys, where=where, table_root=self.season_db)
		if not b:
			return(b, r)
		
		#
		for item in r:
			ob = self.init_by_keys(item)
			seasons_list.append(ob)
			dict_by_name[ob.name] = ob
			dict_by_id[ob.id] = ob
		
		#
		self.__fill_season_class_fields(seasons_list, dict_by_name, dict_by_id)
		
		seasons = []
		for ob in seasons_list:
			if status =='active' and ob.status == 'active':
				seasons.append(ob)
			elif status=='none' and ob.status == 'none':
				seasons.append(ob)
			elif status=='all':
				seasons.append(ob)
			else:
				continue
		return(True, seasons)
	
	@classmethod
	def __fill_season_class_fields(self, seasons_list, dict_by_name, dict_by_id):
		self.seasons_list = seasons_list
		self.dict_by_name = dict_by_name
		self.dict_by_id = dict_by_id

	'''
	def get_by_name(self, name):
		keys = {'name': name}
		bool_, return_data = database().read('project', self.project, self.season_t, self.season_keys, where = keys, table_root=self.season_db)
		if not bool_:
			return(bool_, return_data)
		if return_data:
			return(True, return_data[0])
		else:
			return(True, return_data)
	
	def get_by_id(self, id_):
		keys = {'id': id_}
		bool_, return_data = database().read('project', self.project, self.season_t, self.season_keys, where = keys, table_root=self.season_db)
		if not bool_:
			return(bool_, return_data)
		if return_data:
			return(True, return_data[0])
		else:
			return(True, return_data)
	'''
	
	def rename(self, new_name):
		update_data = {'name': new_name}
		where = {'id': self.id}
		bool_, return_data = database().update('project', self.project, self.season_t, self.season_keys, update_data, where, table_root=self.season_db)
		if not bool_:
			return(bool_, return_data)
		self.name=new_name
		return(True, 'ok')
	
	def stop(self):
		where = {'id': self.id}
		update_data = {'status': u'none'}
		bool_, return_data = database().update('project', self.project, self.season_t, self.season_keys, update_data, where, table_root=self.season_db)
		if not bool_:
			return(bool_, return_data)
		self.status=u'none'
		return(True, 'ok')
	
	def start(self):
		where = {'id': self.id}
		update_data = {'status': u'active'}
		bool_, return_data = database().update('project', self.project, self.season_t, self.season_keys, update_data, where, table_root=self.season_db)
		if not bool_:
			return(bool_, return_data)
		self.status=u'active'
		return(True, 'ok')
	
class group(studio):
	list_group = None
	dict_by_name = None
	dict_by_id = None
	dict_by_type = None
	
	def __init__(self, project_ob):
		if not isinstance(project_ob, project):
			raise Exception('in group.__init__() - Object is not the right type "%s", must be "project"' % project_ob.__class__.__name__)
		self.project = project_ob
		#base fields
		for key in self.group_keys:
			exec('self.%s = False' % key)
	
	# инициализация по имени группы
	# new (bool) - если True - то возвращается новый инициализированный объект класса group, если False - то инициализируется текущий объект
	def init(self, group_name, new = True):
		pass
		# get keys
		bool_, ob = self.get_by_name(group_name)
		if not bool_:
			return(bool_, ob)
		
		if new:
			return(ob)
		else:
			for key in self.group_keys:
				setattr(self, key, getattr(ob, key))
			return(True, 'Ok!')
		
	# инициализация по словарю
	# new (bool) - если True - то возвращается новый инициализированный объект класса group, если False - то инициализируется текущий объект
	# keys (dict) - словарь данных группы
	def init_by_keys(self, keys, new = True):
		if new:
			new_group = group(self.project)
			for key in self.group_keys:
				exec('new_group.%s = keys.get("%s")' % (key, key))
			return new_group
		else:
			for key in self.group_keys:
				exec('self.%s = keys.get("%s")' % (key, key))
			return(True, 'Ok!')
	
	# keys - словарь по group_keys (name и type - обязательные ключи)
	# new (bool) - если True - то возвращается новый инициализированный объект класса group, если False - то инициализируется текущий объект.
	def create(self, keys, new=True):
		pass
		# test name
		if not keys.get('name'):
			return(False, 'Not Name!')
			
		# test type
		if not keys.get('type') or (not keys.get('type') in self.asset_types):
			return(False, 'Not Type!')
		
		# get id
		keys['id'] = uuid.uuid4().hex
		# get description
		if not 'description' in keys:
			keys['description'] = ''
		
		# test season key
		if keys['type'] in self.asset_types_with_season:
			if 'season' in keys and keys['season'] == '':
				return(False, 'For This Type Must Specify a Season!')
			elif not 'season' in keys:
				return(False, 'Required For This Type of Key Season!')
		else:
			keys['season'] = ''
		#return(keys)
		# create group
		# -- create table
		bool_, return_data  = database().create_table('project', self.project, self.group_t, self.group_keys, table_root = self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		# проверка на совпадение имени
		if self.get_by_name(keys['name'])[0]:
			return(False, 'Group with this name(%s) already exists!' % keys['name'])
		
		# -- write data
		bool_, return_data = database().insert('project', self.project, self.group_t, self.group_keys, keys, table_root = self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		if new:
			return(True, self.init_by_keys(keys))
		else:
			for key in self.group_keys:
				setattr(self, key, keys[key])
			return(True, 'ok')
		
	def create_recycle_bin(self):
		pass
		# -- create table
		bool_, return_data  = database().create_table('project', self.project, self.group_t, self.group_keys, table_root = self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		# get group list
		result = self.get_list()
		if not result[0]:
			return(False, (result[1] + ' in get group list'))
		groups = result[1]
		
		all_group = False
		recycle_bin = False
		names = []
		id_s = []
		if groups:
			for group in groups:
				names.append(group.name)
				id_s.append(group.id)
				if group.name == self.recycle_bin_name:
					recycle_bin = group
				if group.type == 'recycle_bin':
					all_group = group
				
		if not all_group:
			#print('Not ALL type')
			# rename
			if recycle_bin:
				#print('Exist RB name')
				# -- new name
				new_name = self.recycle_bin_name + hex(random.randint(0, 1000000000)).replace('0x','')
				while new_name in names:
					new_name = self.recycle_bin_name + hex(random.randint(0, 1000000000)).replace('0x','')
				# -- rename
				result = self.dict_by_name[self.recycle_bin_name].rename(new_name)
				if not result[0]:
					return(False, result[1])
				
			# create group
			# -- keys
			keys = {
			'name':self.recycle_bin_name,
			'type': 'recycle_bin',
			'description':'removed assets'
			}
			# -- get id
			keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
			while keys['id'] in id_s:
				keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
			#print(keys)
			# -- write data
			bool_, return_data = database().insert('project', self.project, self.group_t, self.group_keys, keys, table_root = self.group_db)
			if not bool_:
				return(bool_, return_data)
		else:
			#print('Exist RB!')
			if not recycle_bin:
				# -- rename
				result = self.rename(all_group['name'], self.recycle_bin_name)
				if not result[0]:
					return(False, (result[1] + 'in rename rcycle bin'))
			
		return(True, 'ok')
			
	# возвращает список групп (объекты) согласно фильтру - заполняет поля класса: list_group, dict_by_name, dict_by_id, dict_by_type
	# f (list) - filter of types список типов
	def get_list(self, f = False): # f = [...] - filter of types список типов
		pass
		# 1 - пустые поля
		# 2 - чтение БД
		# 3 - output list
		# 4 - заполнение полей
		
		# (1)
		list_group = []
		dict_by_name = {}
		dict_by_id = {}
		dict_by_type = {}
		
		# (2)
		bool_, return_data = database().read('project', self.project, self.group_t, self.group_keys, table_root=self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		# (3)
		output_list = []
		if not f:
			for grp_d in return_data:
				output_list.append(self.init_by_keys(grp_d))
		else:
			for grp_d in return_data:
				if grp_d['type'] in f:
					output_list.append(self.init_by_keys(grp_d))
					
		# (4)
		for t in self.asset_types + ['recycle_bin']:
			dict_by_type[t] = []
			
		for d in return_data:
			ob = self.init_by_keys(d)
			list_group.append(ob)
			dict_by_name[ob.name] = ob
			dict_by_id[ob.id] = ob
			dict_by_type[ob.type].append(ob)
			
		self._fill_fields_of_group_class(list_group, dict_by_name, dict_by_id, dict_by_type)
		return(True, output_list)
		
	@classmethod
	def _fill_fields_of_group_class(self, list_group, dict_by_name, dict_by_id, dict_by_type):
		pass
		self.list_group = list_group
		self.dict_by_name = dict_by_name
		self.dict_by_id = dict_by_id
		self.dict_by_type = dict_by_type

	
	''' не нужен так как class.dict_by_id - заполняется в self.get_list()
	def get_groups_dict_by_id(self):
		result = self.get_list()
		if not result[0]:
			return(False, result[1])
		
		group_dict = {}
		for row in result[1]:
			group_dict[row['id']] = row
			
		return(True, group_dict)
	'''
	
	# keys (dict) - словарь по self.group_keys
	# возвращает список объектов
	def get_by_keys(self, keys):
		if not keys:
			return(False, 'Not Keys!')
		elif keys.__class__.__name__ != 'dict':
			return(False, 'Wrong type of keys: %s' % keys.__class__.__name__)
		
		bool_, return_data = database().read('project', self.project, self.group_t, self.group_keys, where = keys, table_root=self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		r_list = []
		for keys in return_data:
			r_list.append(self.init_by_keys(keys))
		
		return(True, r_list)
	
	# обёртка на self.get_by_keys()
	# name (str)
	def get_by_name(self, name):
		rows = self.get_by_keys({'name': name})
		if rows[0] and rows[1]:
			return(True, rows[1][0])
		elif rows[0] and not rows[1]:
			return(False, 'This name(%s) not Found' % name)
		else:
			return(False, rows[1])
	
	# обёртка на self.get_by_keys()
	# id_ (str)
	def get_by_id(self, id_):
		rows = self.get_by_keys({'id': id_})
		if rows[0] and rows[1]:
			return(True, rows[1][0])
		elif rows[0] and not rows[1]:
			return(False, 'This id(%s) not Found' % id_)
		else:
			return(False, rows[1])
	
	# обёртка на self.get_by_keys()
	# season (str)
	def get_by_season(self, season):
		rows = self.get_by_keys({'season': season})
		if rows[0] and rows[1]:
			return(True, rows[1][0])
		elif rows[0] and not rows[1]:
			return(False, 'This season(%s) not Found' % season)
		else:
			return(False, rows[1])
	
	# обёртка на self.get_list()
	# type_list (list) - список типов по self.
	def get_by_type_list(self, type_list):
		data = []
		b, r = self.get_list(f = type_list)
		if not b:
			return(b, r)
				
		return(True, r)
		
	''' не нужен так как class.dict_by_type - заполняется в self.get_list()
	def get_dict_by_all_types(self):
		pass
		# get all group data
		result = self.get_list()
		if not result[0]:
			return(False, result[1])
		
		# make data
		data = {}
		for group in result[1]:
			if not group['type'] in data.keys():
				c_data = []
			else:
				c_data = data[group['type']]
			c_data.append(group)
			data[group['type']] = c_data
			
		return(True, data)
	'''
	
	# переименование текущего объекта
	# new_name (str)
	def rename(self, new_name):
		pass
		update_data = {'name': new_name}
		where = {'id': self.id}
		bool_, return_data = database().update('project', self.project, self.group_t, self.group_keys, update_data, where, table_root=self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		# изменение текущего объекта
		self.name = new_name
		
		return(True, 'ok')
		
	# изменение комента текущего объекта
	# description (str)
	def edit_description(self, description):
		update_data = {'description': description}
		where = {'id': self.id}
		bool_, return_data = database().update('project', self.project, self.group_t, self.group_keys, update_data, where, table_root=self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		self.description = description
		return(True, 'ok')
		
class list_of_assets(studio):
	def __init__(self, group_ob):
		if not isinstance(group_ob, group):
			raise Exception('in list_of_assets.__init__() - Object is not the right type "%s", must be "group"' % group_ob.__class__.__name__)
		self.group = group_ob

	# rows (list) = [{keys}, {keys}, ...]
	def save_list(self, rows, group_name = False):
		list_of_assets_path = self.group.project.list_of_assets_path
		# test data keys
		if not group_name:
			if not self.group.name:
				return(False, 'No init of Group!')
			group_name = self.group.name
		
		if not self.group.project.name:
			return(False, 'No init of Project!')
		
		# test exists path
		if not os.path.exists(list_of_assets_path):
			try:
				with open(list_of_assets_path, 'w') as f:
					jsn = json.dump({}, f, sort_keys=True, indent=4)
					f.close()
			except:
				return(False, '"%s"  can not be write' % list_of_assets_path)
		
		# read data
		try:
			with open(list_of_assets_path, 'r') as read:
				data = json.load(read)
				read.close()
		
		except:
			return(False, '"%s"  can not be read' % list_of_assets_path)
		
		# edit data
		data[group_name] = rows
		
		# write data
		try:
			with open(list_of_assets_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				#print('data:', data)
				f.close()
		except:
			return(False, '"%s"  can not be write' % list_of_assets_path)
		
		return(True, 'ok')
		
	def get_list(self):
		list_of_assets_path = self.group.project.list_of_assets_path
		# test exists path
		if not os.path.exists(list_of_assets_path):
			return(True, [])
		
		# read data
		try:
			with open(list_of_assets_path, 'r') as read:
				data = json.load(read)
				read.close()
								
		except:
			return(False, '"%s" can not be read!' % list_of_assets_path)
			
		return(True, data)
		
	def get(self, group_name = False):
		list_of_assets_path = self.group.project.list_of_assets_path
		if not group_name:
			if not self.group.name:
				return(False, 'No init of group!')
			group_name = self.group.name
			
		# test exists path
		if not os.path.exists(list_of_assets_path):
			return(False, '"%s" Not Found!' % list_of_assets_path)
		
		# read data
		try:
			with open(list_of_assets_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, '"%s" can not be read!' % list_of_assets_path)
		
		if group_name in data:
			return(True, data[group_name])
		else:
			return(False, 'list of assets for "%s" not found!' % group_name)
		
		
	def remove(self, group_name = False):
		list_of_assets_path = self.group.project.list_of_assets_path
		if not group_name:
			if not self.group.name:
				return(False, 'No init of group!')
			group_name = self.group.name
		
		# test exists path
		if not os.path.exists(list_of_assets_path):
			return(False, '"%s" Not Found!' % list_of_assets_path)
			
		# read data
		try:
			with open(list_of_assets_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, '"%s" can not be read!' % list_of_assets_path)
			
		if group_name in data:
			del data[group_name]
		else:
			return(False, 'list of assets for "%s" not found!' % group_name)
			
		# write data
		try:
			with open(list_of_assets_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				#print('data:', data)
				f.close()
		except:
			return(False, '"%s"  can not be write' % list_of_assets_path)
			
		return(True, 'Ok')
		
		
	def create_assets(self, project, group):
		pass
	
