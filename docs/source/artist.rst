.. _class-artist-page:

Class Artist
============

**artist(studio)**

**level** = 'studio'

Данные хранимые в БД (имя столбца : тип данных):

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
  
Создание экземпляра класса:
---------------------------

.. code-block:: python
  
  import edit_db as db
  
  artist = db.artist()
  
Атрибуты
--------

:nik_name: (*str*) - никнейм (уникально).

:user_name: (*str*) - юзернейм в текущей системе, откуда сделан вход.

:password: (*str*) - 

:date_time: (*timestamp*) - дата и время регистрации в студии.

:email: (*str*) - 

:phone: (*str*) - 

:specialty: (*str*) - 

:outsource: (*int*) - 0 или 1

:workroom: (*list*) - список id отделов

:level:  (*str*) - уровень, значение из *studio.user_levels*

:share_dir: (*str*) - путь к директории обмена ``пока не используется``

:status: (*str*) - значение из *['active', 'none']*

:working_tasks: (*dict*) - словарь списков имён назначенных задач, по именам отделов ``? на счёт того что по именам отделов``.

:checking_tasks: (*dict*) - словарь списков имён назначенных на проверку задач, по именам отделов ``? на счёт того что по именам отделов``.
  
Методы
------

.. py:function:: init(nik_name[, new = True])

  инициализация (заполнение полей экземпляра соответственно данного артиста) по *nik_name*
  
  **Параметры:**
  
  * **nik_name** (*str*) - никнейм
  * **new** (*bool*) - если *True* - то возвращается новый инициализированный экземпляр класса *artist*, если *False* - то инициализируется текущий экземпляр
  * **return** - new_artist (*artist*) / (*True, 'Ok!'*) или (*False, comment*)
  
.. py:function:: init_by_keys(keys[, new = True])
  
  инициализация (заполнение полей экземпляра соответственно данного артиста) по словарю
  
  **Параметры:**
  
  * **keys** (*dict*) - словарь по *studio.artists_keys*
  * **new** (*bool*) - если *True* - то возвращается новый инициализированный экземпляр класса *artist*, если *False* - то инициализируется текущий экземпляр
  * **return** - new_artist (*artist*) / (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: add_artist(keys[, registration = True])

  добавление нового пользователя
  
  **Параметры:**
  
  * **keys** (*dict*) - словарь по ключам *artists_keys*, обязательные значения - *nik_name* и *password*.
  * **registration** (*bool*) если =*True* - произойдёт заполнение полей *artists_keys* экземпляра класса, поле *user_name* будет заполнено, если *registration*=*False* - поля *artists_keys* заполняться не будут, поле *user_name* - останется пустым.
  * **return** - (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: read_artist(keys[, objects=True])

  чтение списка данных артистов
  
  **Параметры:**
  
  * **keys** (*dict*) - словарь по ключам *artists_keys* - критерии для поиска, если *keys= 'all'* вернёт данные по всем артистам.
  * **objects** (*bool*) - если *True* - то возвращаются экземпляры, если *False* - то словари.
  * **return** - (*True, [артисты - словари или экземпляры]*) или (*False, comment*)

.. py:function:: read_artist_of_workroom(workroom_id[, objects=True])

  чтение списка данных артистов по *id* отдела
  
  **Параметры:**
  
  * **workroom_id** (*str*) - *id* отдела
  * **objects** (*bool*) - если *True* - то возвращаются экземпляры, если *False* - то словари.
  * **return** - (*True, [артисты - словари или экземпляры]*) или (*False, comment*)

.. py:function:: get_artists_for_task_type(task_type, workroom_ob)

  сортированный список активных артистов подходящих для данного типа задачи.
  
  **Параметры:**
  
  * **task_type** (*str*) - тип задачи
  * **workroom_ob** (*workroom*) - предполагается что выполнена процедура *workroom.get_list()* и заполнено поле *list_workroom* (список всех отделов)
  * **rturn** - (*True, сортированный список имён артистов, словарь артистов по именам.*) или (*False, comment*)

.. py:function:: login_user(nik_name, password)
  
  Логин юзера. Перезаписывает текущее имя пользователя пк, в соответствие указанного ник-нейма, при этом проверит и удалит данное имя пользователя из под других ник-неймов. Произойдёт заполнение полей *artists_keys* экземпляра класса.
  
  **Параметры:**
  
  * **nik_name** (*str*) - никнейм
  * **password** (*str*) - пароль
  * **return** - (*True, (nik_name, user_name)*)  или (*False, comment*)

.. py:function:: get_user([outsource = False])

  определение текущего пользователя, заполнение полей *artists_keys* экземпляра класса.
  
  **Параметры:**
  
  * **outsource** (*bool*)- с точки зрения удалённого пользователя или нет.
  * **return** -(*True, (nik_name, user_name, outsource, {данные артиста - словарь})*) или (*False, comment*)

.. py:function:: edit_artist(key_data[, current_user=False])

  редактирование данного (инициализированного) экземпляра артиста.
  
  **Параметры:**
  
  * **keys** (*dict*) - данные на замену - *nik_name* - не редактируется, поэтому удаляется из данных перед записью.
  * **current_user** (*artist*) - редактор - залогиненный пользователь, если *False* - то будет создан новый экземпляр и произведено *get_user()* (лишнее обращени е к БД) . если *force* - проверки уровней и доступов не выполняются.
  * **return** - (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: get_working_tasks(project_ob[, statuses=False])

  получение словаря задач (назначенных на артиста) по именам.
  
  **Параметры:**
  
  * **project_ob** (*project*) - текущий проект
  * **statuses** (*bool / list*) - *False* или список статусов задач
  * **return** (*True, {task_name: task_ob, ...}*) или (*False, comment*)

.. py:function:: get_reading_tasks(project_ob[, status=False])

  получение словаря задач (назначенных на артиста в качестве проверяющего) по именам.
  
  **Параметры:**
  
  * **project_ob** (*project*) - текущий проект
  * **status** (*bool/ str*) - если не *False*, то возвращает только задачи соответствующие данному статусу.
  * **return** (*True, {task_name: task_ob, ...}*) или (*False, comment*)

.. note:: *add_stat(), read_stat(), edit_stat()* - не правились, возможно будут удалены.
