.. _class-chat-page:

Class Chat
==========

**chat(studio)**

**level** = 'project'

Данные хранимые в БД (имя столбца : тип данных):

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
    
Создание экземпляра класса:
---------------------------

.. code-block:: python
  
  import edit_db as db
  
  project = db.project()
  asset = db.asset(project)
  task = db.task(asset)
  
  chat = db.chat(task) # task - обязательный параметр при создании экземпляра chat
  # доступ ко всем параметрам и методам принимаемого экземпляра task - через chat.task
  
Атрибуты
--------

:message_id: (*str*) -

:date_time: (*timestamp*) - время и дата создания записи

:date_time_of_edit: (*timestamp*) - время и дата изменения записи

:author: (*str*) - *nik_name* автора записи

:topic: (*dict*) - словарь данных сообщения, ключи - номера строк в ковычках, значения - список из трёх значений: путь к изображению, путь к иконке изображения, сообщение.  *{'num_line': [path_to_img, path_to_icon, message], ...}*

:color: (*list*) - *[r,g,b]* значения цвета от *0* до *1*.

:status: (*str*) -

:reading_status: (*dict*) - ``??``

:task: (*task*) - экземпляр :ref:`class-task-page` принимаемый при создании экземпляра класса, содержит все атрибуты и методы :ref:`class-task-page`.

Методы
------

.. py:function:: record_messages(input_keys[, artist_ob=False])

  запись сообщения в чат для задачи.

  .. note:: *self.task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **input_keys** (*dict*) - словарь по *studio.chats_keys* - обязательные ключи: *'topic','color','status', 'reading_status'*  ``??????? список обязательных полей будет пересмотрен``
  * **artist_ob** (*bool/artist*) - если *False* - значит создаётся новый объект *artist* и определяется текущий пользователь
  * **return** - (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: read_the_chat([message_id=False, sort_key=False, reverse = False])

  чтение сообщений чата задачи.

  .. note:: *self.task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **message_id** (*hex/bool*) - *id* читаемого сообщения, если *False* - то читаются все сообщения чата
  * **sort_key** (*str*) - ключ по которому сортируется список. Если  *False* то сортировки не происходит
  * **reverse** (*bool*) - пока никак не используется
  * **return** - (*True, [messages]*) или (*False, comment*)

.. py:function:: edit_message(message_id, new_data[, artist_ob=False])

  изменение записи автором сообщения.

  .. note:: *self.task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **artist_ob** (*bool/artist*) - если *False* - значит создаётся новый объект *artist* и определяется текущий пользователь
  * **message_id** (*hex*) - *id* изменяемого сообщения
  * **new_data** (*dict*) - словарь данных на замену - *topic, color*
  * **return** - (*True, 'Ok!'*) или (*False, comment*)