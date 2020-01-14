.. _class-task-page:

Class Task
==========

**task(studio)**

**level** = 'project'

Данные хранимые в БД (имя столбца : тип данных):

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

Создание экземпляра класса:
---------------------------

.. code-block:: python
  
  import edit_db as db
  
  project = db.project()
  asset = db.asset(project)
  
  task = db.task(asset) # asset - обязательный параметр при создании экземпляра task
  # доступ ко всем параметрам и методам принимаемого экземпляра asset - через task.asset
  
Атрибуты
--------

:activity: (*str*) - активити из *asset.ACTIVITY_FOLDER[asset_type]*

:task_name: (*str*) - имя задачи, структура имени: *asset_name:task_name*

:task_type: (*str*) - тип задачи из *studio.task_types* + *service*

:source: (*list*) - имена задач, объекты из активити которых используются как исходники.

:input: (*str* / *list*) - для сервисной задачи (*task_type=service*) - это список имён входящих задач. для не сервисной задачи - это имя входящей задачи.

:status: (*str*) - статус задачи из *studio.task_status*

:outsource: (*int*) - значение из [0, 1] если = 1 - задача на аутсорсе.

:artist: (*str*) - *nik_name* исполнителя.

:level: (*text*) -  пользовательский уровень сложности задачи.

:planned_time: (*float*) - планируемое время (ед. измерения - час).

:price: (*float*) - стоимость работ по задаче (ед. измерения - юнит).

:time: (*dict*) - словарь: ключи - ``nik_name``, значения - ссумарное время атриста по этой задаче (ед. измерения - секунда).

:full_time: (*real*) - ссумарное время всех атристов по этой задаче (ед. измерения - секунда).

:deadline: (*timestamp*) - расчётная дата окончания работ.

:start: (*timestamp*) - дата и время взятия задачи в работу.

:end: (*timestamp*) - дата и время приёма задачи.

:specification: (*str*) - ссылка на техническое задание.

:chat_local: ``?``

:web_chat: ``?``

:supervisor: ``?``

:readers: (*dict*) - словарь: ключ - *nik_name*, значение - 0 или 1 (статус проверки),  плюс одна запись: ключ - *'first_reader'*, значение - *nik_name* - это первый проверяющий - пока он не проверит даннаня задача не будет видна у других проверяющих в списке на проверку.

:output: (*list*) - список имён исходящих задач.

:priority: (*int*) - приоритет.

:extension: (*str*) - расширение файла для работы над данной задачей, начинается с точки, например: *'.blend'*

:approved_date: (*timestamp*) - дата планируемого окончания работ (вычисляется при создании экземпляра)

:asset: (*asset*) - экземпляр :ref:`class-asset-page` принимаемый при создании экземпляра класса, содержит все атрибуты и методы :ref:`class-asset-page`.

:description: (*text*) - описание задачи

:branches: (*list*) - ``атрибут класса`` список веток активити задачи. Заполняется при выполнении метода `_set_branches`_

Методы
------

Чтение
~~~~~~

.. py:function:: init(task_name[, new = True])

  заполнение полей экземпляра по *studio.tasks_keys*
  
  .. rubric:: Параметры:

  * **task_name** (*str*) - имя задачи. данные задачи будут считаны из базы данных
  * **new** (*bool*) - если *True* - то возвращается новый инициализированный экземпляр класса *task*, если *False* - то инициализируется текущий экземпляр
  * **return**:
      * если *new=True* - инициализированный экземпляр, 
      * если *new=False* - (*True, 'Ok!'*) / или (*False, comment*)

.. py:function:: init_by_keys(keys[, new=True])

  заполнение полей экземпляра по *studio.tasks_keys*
  
  .. rubric:: Параметры:

  * **keys** (*dict*) - словарь данных задачи, получаемый в функции `_read_task`_ ()
  * **new** (*bool*) - если *True* - то возвращается новый инициализированный экземпляр класса *task*, если *False* - то инициализируется текущий экземпляр
  * **return**:
      * если *new=True* - инициализированный экземпляр, 
      * если *new=False* - (*True, 'Ok!'*)
    
.. py:function:: get_list([asset_id=False, task_status = False, artist = False])

  получение списка задач ассета (экземпляры).

  .. rubric:: Параметры:

  * **asset_id** (*str*) - требуется если экземпляр *task.asset* не инициализирован, либо требуется список задач не для этого инициализированного ассета
  * **task_status** (*str*) - фильтр по статусам задач
  * **artist** (*str*) - фильтр по имени
  * **return** - (*True, task_list(список задач - экземпляры)*) или (*False, коммент*)

.. py:function:: get_tasks_by_name_list(task_name_list[, assets_data = False])

  возвращает задачи (экземпляры) по списку имён задач, из различных ассетов данного проекта.
  
  .. note:: *task.asset.project* - инициализирован

  .. rubric:: Параметры:

  * **task_name_list** (*list*) - список имён задач
  * **assets_data** (*dict*) - *dict{asset_name: asset(экземпляр),...}* результат функции *asset.get_dict_by_name_by_all_types()*, если не передавать - будет произведено чтение БД
  * **return** - (*True, { task_name: task(экземпляр), ... }*) или (*False, коммент*)


Work пути
~~~~~~~~~

.. py:function:: get_final_work_file_path([current_artist=False])

  возвращает путь и версию последнего рабочего файла, для взятия в работу. Логика тут :ref:`task-specification-page`
  
  .. rubric:: Параметры:
  
  * **current_artist** (*artist*) - текущий пользователь, если не передавать, будет сделано *get_user*
  * **return** - (*True, (path, version)*) или (*False, comment*)
      * если нет ни одного лога - (*True, ('','')*)
  
.. py:function:: get_version_work_file_path(version)

  возвращает путь до указанной версии рабочего файла.
  
  .. rubric:: Параметры:
  
  * **version** (*int / str*) - номер версии
  * **return** - (*True, path*) - или (*false, comment*)
  
.. py:function:: get_new_work_file_path()

  создание пути для новой *commit* или *pull* версии файла.
  
  .. rubric:: Параметры:
  
  * **return** - (*True, (path, version)*) или (*False, comment*)
  
Push пути
~~~~~~~~~

.. py:function:: get_final_push_file_path([current_artist=False])

  возвращает путь и версию финальной *push* версии файла.
  
  .. rubric:: Параметры:
  
  * **current_artist** (*artist*) - текущий пользователь, если не передавать, будет сделано *get_user()*
  * **return** 
      * для ``sketch`` - (*True*, ( {словарь - ключи: типы путей ``look_path``, ``push_path``, значение: {словарь - пути по веткам}}, *version* ))
      * для остальных - (*True, (path, version)*) - или (*false, comment*)
      
.. py:function:: get_version_push_file_path(version[, current_artist=False])

  возвращает путь до указанной *push* версии файла.
  
  .. rubric:: Параметры:
  
  * **version** (*int / str*) - номер версии
  * **current_artist** (*artist*) - текущий пользователь, если не передавать, будет сделано *get_user()*
  * **return**
      * для ``sketch`` - (*True*, {словарь - ключи: типы путей ``look_path`` или ``push_path``, значение: {словарь - пути по веткам}})
      * для остальных - (*True, path*) - или (*false, comment*)
      
.. py:function:: get_new_push_file_path([version=False, current_artist=False])

  возвращает пути и версию до новой *push* версии
  
  .. rubric:: Параметры:
  
  * **version** (*int / str*) - номер версии исходника (*pull* или *commit*) при отсутствии *push* последней версии. Для мультипаблиша (*sketch*) всегда только из последних версий веток.
  * **current_artist** (*artist*) - текущий пользователь, если не передавать, будет сделано *get_user()*
  * **return**
      * для ``sketch`` - (*True*, ({словарь с ключами: ``source_path``, ``source_versions``, ``push_path``, ``look_path`` - значения словари по веткам}, *new_version*)
      * для остальных (*True*, (*source_path*, *source_version*, *source_branch*, *new_path*, *new_version*))
      
Publish пути
~~~~~~~~~~~~

.. py:function:: get_version_publish_file_path([version=False, branches=False, version_log=False])

  пути до файлов указанной *publish* версии.
  
  .. rubric:: Параметры
  
  * **version** (*int / str*) - номер *publish* версии
  * **branches** (*bool / list*) - список веток данного паблиша, для мультипаблиша.
  * **version_log** (*bool / dict*) - словарь лога данной версии, если его передавать, то *branches* и *version* не имеют смысла.
  * **return** (*True, *r_data*) или (*False, comment*)
  * структура **r_data**:
      * для мультипаблиша - словарь с ключами ``look_path``, ``publish_path``, значения - словари путей по веткам.
      * не для мультипаблиша - путь к файлу.

.. py:function:: get_final_publish_file_path()

  пути к *top* версии паблиш файлов
  
  .. rubric:: Параметры
  
  * **return** (*True, (*r_data*, version)) или (*False, comment*)
  * структура **r_data**:
      * для мультипаблиша - словарь с ключами ``look_path``, ``publish_path``, значения - словари путей по веткам.
      * не для мультипаблиша - путь к файлу.

.. py:function:: get_new_publish_file_path([republish=False, source_log=False, source_version=False])

  пути до файлов новой *publish* версии (и *top*, и версию)
  
  .. rubric:: Параметры
  
  * **republish** (*bool*) - репаблиш или нет.
  * **source_log** (*bool / dict*) - лог источника для паблиша (*push* или *publish*), при наличие этого лога версия *source_version* передавать не имеет смысла.
  * **source_version** (*bool / str*) - версия исходника (*push* или *publish*) если *False* - последняя версия.
  * **return**:
      * для мультипаблиш (*true, (dict_path, version, source, branches*)) или (*False, comment*):
          * структура **dict_path**:
              * ключи - ``top_path``, ``top_look_path``, ``version_path``, ``version_look_path``, ``source_path``, ``source_look_path``
              * значения - пути или словари путей по веткам.
          * **version** - новая версия
          * **source** - версия (*push* или *publish*) от куда делается паблиш.
          * **branches** - ветки которые паблишатся.
      * для не мультипаблиша (*true, (dict_path, version, source*)) или (*False, comment*):
          * структура **dict_path**:
              * ключи - ``top_path``, ``version_path``, ``source_path``
              * значения - пути.
          * **version** - новая версия.
          * **source** - версия (*push* или *publish*) от куда делается паблиш.

Пути (old)
~~~~~~~~~~

.. py:function:: get_final_file_path([task_data=False])

  .. danger:: Устарело!
  
  получение пути к последней версии файла задачи.
  
  .. rubric:: Параметры:

  * **task_data** (*dict*) - требуется если не инициализирован *task* ``лучше не использовать``
  * **return_data** - (*True, final_file_path, asset_path*) или  (*False, comment*)

.. py:function:: get_version_file_path(version[, task_data=False])

  .. danger:: Устарело!
  
  получение пути к файлу задачи по указанной версии.
  
  .. rubric:: Параметры:

  * **version** (*str*) - *hex* 4 символа
  * **task_data** (*dict*) - требуется если не инициализирован *task* ``лучше не использовать``
  * **return** - (*True, version_file_path*) или  (*False, comment*)

.. py:function:: get_new_file_path([task_data=False])

  .. danger:: Устарело!
  
  получение пути к файлу задачи для новой версии
  
  .. rubric:: Параметры:

  * **task_data** (*dict*) - требуется если не инициализирован *task* ``лучше не использовать``
  * **return** - (*True, (new_dir_path, new_file_path)*)

.. py:function:: get_publish_file_path(activity)

  .. danger:: Устарело!
  
  получение пути к паблиш версии файла активити.
  
  .. rubric:: Параметры:

  *	**activity** (*str*) - активити
  * **return** - (*True, publish_file_path*) или  (*False, comment*)
  
Операции commit/look/open/push/publish
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:function:: commit(work_path, description[, branch=False, artist_ob=False])

  запись новой рабочей версии в ``work`` директорию.
  
  .. note:: заполнение: ``task.open_time``, ``task.start``. Выполнение ``log.artist_start_log()`` (создание, при отсутствии, артист лога на эту задачу).
  
  .. rubric:: Параметры:
  
  * **work_path** (*unicode*) - путь к текущему рабочему файлу
  * **description** (*unicode*) - коммент
  * **branch** (*unicode*) - наименование ветки, если не передавать - то *master*
  * **artist_ob** (*artist*) - если не передовать, то будет выполнен *get_user()*
  * **return** (*True, path* - путь до сохранённого файла) или (*False, comment*)
  
.. py:function:: run_file(path[, viewer=False])

  запуск файлов редактором или вьювером, создание *tmp* копии файла.
  
  .. rubric:: Параметры:
  
  * **path** (*str*) - путь до оригинального файла.
  * **viewer** (*bool*):
      * если *True* - открытие вьювером по оригинальному пути.
      * если *False* - открытие редактором *tmp* копии файла.
  * **return** (*True, path*) или (*False, comment*)
  
.. py:function:: look([action='push', version=False, launch=True])

  просмотр какой-либо версии файла для менеджеров (*push, publish* версии)
  
  .. note:: если тип задачи из ``studio.multi_publish_task_types`` (например ``sketch``) то запуска не будет, но будут возвращены пути.
  
  .. rubric:: Параметры:
  
  * **action** (*str*) - экшен из *[push, publish]*
  * **version** (*bool / str / int*) - версия, если *False* - то открывается последняя.
  * **launch** (*bool*) - *False* - возвращает только путь, иначе запуск редактором по расширению (для не скетч).
  * **return** (*True, path*) или (*False, comment*)

.. py:function:: open_file([look=False, current_artist=False, tasks=False, input_task=False, open_path=False, version=False, launch=True])

  откроет файл в приложении - согласно расширению.
  
  .. note:: заполнение: ``task.time``, ``task.full_time``, ``artist_log.full_time``
  
  .. rubric:: Параметры:

  * **look** (*bool*) - если *True* - то статусы меняться не будут, если *False* - то статусы меняться будут
  * **current_artist** (*artist*) - если не передавать, то в случае *look=False* - будет выполняться *get_user()* - лишнее обращение к БД
  * **tasks** (*dict*) - словарь задач данного артиста по именам (результат функции artist.get_working_tasks()). - нужен для случая когда *look=False*, при отсутствии будет считан - лишнее обращение к БД
  * **input_task** (*task*) - входящая задача - для *open_from_input* (если передавать - то имеется ввиду открытие из активити входящей задачи)
  * **open_path** (*unicode/str*) - путь к файлу - указывается для *open_from_file* (открытие из указанного файла)
  * **version** (*bool/str*) - версия рабочего файла активити - если указать то будет открытие рабочего файла этой версии
  * **launch** (*bool*) - если *True* - то будет произведён запуск приложением, которое установлено в соответствии с данным расширением файла (для универсальной юзерской панели и для менеджерской панели, при открытии на проверку), если *False* - то запуска не будет, но все смены статусов произойдут и будет возвращён путь к файлу - для запуска из плагина
  * **return** (*True, file_path - куда открывается файл*) или (*False, coment*)

.. py:function:: push(description[, version=False, current_artist=False])

	создание новой *push* версии на сервере студии, или выгрузка архива в облако для создания *push* версии на сервере студии (для аутсорса)
  
  .. Attention:: Для аутсорса пока не сделано, только для работников студии.
  
  .. rubric:: Параметры:
  
  * **version** (*str/int*) - *work* версия из которой делается *push*, не имеет смысла для мультипуша (*sketch*) там только из последней версии.
  * **return* (*True, message*) или (*False, message*)
  
.. py:function:: push_file(description, current_file[, current_artist=False])

  .. danger:: Устарело!

  запись новой рабочей версии файла, сохранение версии + запись *push* лога.
  
  .. rubric:: Параметры:

  * **description** (*str*) - комментарий к версии
  * **current_file** (*unicode/str*) - текущее местоположение рабочего файла (как правило в темп)
  * **current_artist** (*artist*) - если не передавать, то будет выполняться *get_user()* - лишнее обращение к БД
  * **return** (*True, new_file_path*) или (*False, comment*)
  
.. py:function:: publish_task([description=False, republish=False, source_version=False, source_log=False, current_artist=False])

  перекладывание паблиш версии файлов (в том числе top версии), запись лога.
  
  .. rubric:: Параметры:
  
  * **description** (*str*) - не обязательный параметр, при отсутствии составляется автоматически - техническое описание: что, откуда, куда.
  * **source_version** (*int, str*) - версия *push* или *publish* (при репаблише), если *False* при паблише - то паблиш из последней пуш версии.
  * **source_log** (*bool / dict*) - лог версии источника, при его наличии *source_version* не имеет смысла.
  * **current_artist** (*artist*) - если не передавать, то будет выполняться *get_user()* - лишнее обращение к БД.
  * **return** (*True, comment*) или (*False, comment*)
  
Кеш
~~~

.. py:function:: get_versions_list_of_cache_by_object(ob_name[, activity = 'cache', extension = '.pc2', task_data=False])

  список версий кеша для меш объекта.

  .. rubric:: Параметры:

  * **ob_name** (*str*) - имя 3d объекта
  * **activity** (*str*) - по умолчанию *"cache"* (для *blender*) - для других программ может быть другим, например *"maya_cache"*
  * **extension** (*str*) - расширение файла кеша
  * **task_data** (*dict*) - читаемая задача(словарь), если *False* - значит предполагается, что *task* инициализирован. ``лучше не использовать``
  * **return**:
      * (*True, cache_versions_list*)  где *cache_versions_list* список кортежей - [*(num (str), ob_name,  path), ...*]
      * (*False, коммент*)

.. py:function:: get_final_cache_file_path(cache_dir_name[, activity = 'cache', extension = '.pc2', task_data=False])

  путь к последней версии кеша для меш объекта.

  .. rubric:: Параметры:

  * **cache_dir_name** (*str*) - "*asset_name*" + "_" + "*ob_name*"
  * **activity** (*str*) - по умолчанию *"cache"* (для *blender*) - для других программ может быть другим, например "*maya_cache*"
  * **extension** (*str*) - расширение файла кеша
  * **task_data** (*dict*) - читаемая задача, если *False* - значит предполагается, что *task* инициализирован. ``лучше не использовать``
  * **return**  - (*True, path*) или (*False, коммент*)

.. py:function:: get_new_cache_file_path(cache_dir_name[, activity = 'cache', extension = '.pc2', task_data=False])

  путь к новой версии кеша для меш объекта.

  .. rubric:: Параметры:

  * **cache_dir_name** (*str*) - "*asset_name*" + "_" + "*ob_name*"
  * **activity** (*str*) - по умолчанию "*cache*" (для *blender*) - для других программ может быть другим, например "*maya_cache*"
  * **extension** (*str*) - расширение файла кеша
  * **task_data** (*dict*) - читаемая задача, если *False* - значит предполагается, что *task* инициализирован. ``лучше не использовать``
  * **return** - (*True, (new_dir_path, new_file_path)*) или (*False, коммент*)

.. py:function:: get_version_cache_file_path(version, cache_dir_name[, activity = 'cache', extension = '.pc2', task_data=False])

  путь к определённой версии файла кеша меш объекта.

  .. rubric:: Параметры:

  * **version** (*str*) - *hex* 4 символа
  * **cache_dir_name** (*str*) - "*asset_name*" + "_" + "*ob_name*"
  * **activity** (*str*) - по умолчанию *"cache"* (для *blender*) - для других программ может быть другим, например *"maya_cache"*
  * **extension** (*str*) - расширение файла кеша
  * **task_data** (*dict*) - читаемая задача, , если *False* - значит предполагается, что *task* инициализирован. ``лучше не использовать``
  * **return_data** - (*True, path*) или (*False, коммент*)
  
Создание задач
~~~~~~~~~~~~~~

.. py:function:: create_tasks_from_list(list_of_tasks)

  создание задач ассета по списку.
  
  .. note:: *task.asset* - должен быть инициализирован

  .. rubric:: Параметры:

  * **list_of_tasks** (*list*) - список задач (словари по *tasks_keys*, обязательные параметры: *task_name*)
  * **return** - (*True, 'ok'*) или (*False, коммент*)

.. py:function:: add_single_task(task_data)

  создание одной задачи.
  
  .. note:: *task.asset* - должен быть инициализирован.
  
  .. note:: обязательные поля в *task_data*: *activity*, *task_name*, *task_type*, *extension*, если передать поля *input*, *output* - то будут установлены соединения и призведены проверки, и смены статусов

  .. rubric:: Параметры:

  * **return** - (*True, 'ok'*) или (*False, коммент*)
  
Редактирование
~~~~~~~~~~~~~~

.. py:function:: change_activity(new_activity)

  замена активити текущей задачи

  .. note:: *task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **new_activity** (*str*)
  * **return_data** -  (*True, task_data*) или (*False, коммент*)

.. py:function:: change_price(new_price)

  замена стоимости текущей задачи

  .. note:: *task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **new_price** (*float*)
  * **return** -  (*True, task_data*) или (*False, коммент*)

.. py:function:: changes_without_a_change_of_status(key, new_data, task_data=False)

  замена параметров задачи, которые не приводят к смене статуса.

  .. rubric:: Параметры:

  * **key** (*str*) - ключ для которого идёт замена
      * допустимые ключи для замены:
          *  *activity*
          *  *task_type*
          *  *season*
          *  *price*
          *  *specification*
          *  *extension*
          *  *start*
          *  *end*
          *  *time*
          *  *full_time*
          *  *deadline*
          *  *planned_time*
          *  *level*
  * **new_data** (по типу ключа) - данные на замену
  * **task_data** (*bool/dict*) - изменяемая задача, если *False* - значит предполагается, что *task* инициализирован. ``лучше не использовать``
  * **return** - (*True, 'ok'*) или (*False, коммент*)

.. py:function:: add_readers(add_readers_list)

  добавление проверяющих для текущей задачи.

  .. note:: *task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **add_readers_list** (*list*) - список никнеймов проверяющих
  * **return** - (*True, readers(dict - в формате записи как в задаче), change_status(bool)*) или (*False, коммент*)

.. py:function:: make_first_reader(nik_name)

  обозначение превого проверяющего, только после его проверки есть смысл проверять остальным проверяющим, и только после его приёма данная задача появится в списке на проверку у остальных читателей. Предполагается что это технический проверяющий от отдела, где идёт работа.

  .. note:: *task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **nik_name** (*str*) - никнейм артиста
  * **return** - (*True, readers(dict - в формате записи как в задаче)*) или (*False, коммент*)

.. py:function:: remove_readers(remove_readers_list)

  удаляет проверяющего из списка проверяющих, а также удалит его как первого проверяющего, если он таковой.

  .. note:: *task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **remove_readers_list** (*list*) - список никнеймов удаляемых из списка читателей
  * **return** - (*True, readers(dict - в формате записи как в задаче), change_status(bool)*) или (*False, коммент*)

.. py:function:: change_artist(new_artist)

  замена артиста и возможная замена при этом статуса.

  .. note:: *task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **new_artist** (*str/artist*) - *nik_name* или *artist* (экземпляр), лучше передавать экземпляр для экономии запросов
  * **return_data** - (*True, (new_status, int(artist_outsource))*) или (*False, коммент*)

.. py:function:: change_input(new_input)

  изменение входа не сервисной задачи, с вытикающими изменениями статусов.

  .. note:: *task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **new_input** (*str*) - имя новой входящей задачи
  * **return** - (*True, (new_status, old_input_task_data, new_input_task_data)*) или (*False, коммент*)

.. py:function:: accept_task()

  приём задачи, статус на *done* (со всеми вытикающими сменами статусов), создание паблиш версии, заполнение *artist_tasks_log (finish, price)*, выполнение хуков.

  .. note:: *task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **return** - (*True, 'ok'*) или (*False, коммент*)

.. py:function:: readers_accept_task(current_artist)

  приём задачи текущим проверяющим, изменение статуса в *task.readers*, если он последний то смена статуса задачи на *done* (со всеми вытикающими сменами статусов).

  .. note:: *task* - должен быть инициализирован.

  .. rubric:: Параметры:

  * **current_artist** (*artist*) - экземпляр класса артист, должен быть инициализирован - *artist.get_user()*
  * **return** - (*True, 'ok'*) или (*False, коммент*)

.. py:function:: close_task()

  закрытие задачи, смена статуса на *close* (со всеми вытикающими сменами статусов)

  .. note:: *task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **return** - (*True, 'ok'*) или (*False, коммент*)

.. py:function:: rework_task(current_user)

  отправка задачи на переработку из статуса на проверке, при этом проверяется наличие свежего (последние 30 минут) коментария от проверяющего.
  
  .. note:: *task* должен быть инициализирован

  .. rubric:: Параметры:

  * **current_user** (*artist*) - экземпляр класса артист, должен быть инициализирован - *artist.get_user()* - если *False* - то задача отправится на переделку без проверки чата (для тех нужд)
  * **return** - (*True, 'ok'*) или (*False, коммент*)

.. py:function:: return_a_job_task([task_data=False])

  возврат в работу задачи из завершённых статусов (*done*, *close*).

  .. rubric:: Параметры:

  * **task_data** (*dict*) - изменяемая задача, если *False* - значит предполагается, что *task* инициализирован
  * **return** - (*True, new_status*) или (*False, коммент*)

.. py:function:: change_work_statuses(change_statuses)

  тупо смена статусов в пределах рабочих, что не приводит к смене статусов исходящих задач.
  
  .. note:: *task* - должен быть инициализирован

  .. rubric:: Параметры:

  * **change_statuses** (*list*) - [*(task_ob, new_status), ...*]
  * **return_data** - (*True, {task_name: new_status, ... } *) или (*False, коммент*)
  
.. py:function:: to_checking()

  отправка текущей задачи на проверку

  .. note:: *task* должен быть инициализирован, обёртка на task.change_work_statuses()
  
  .. rubric:: Параметры:
  
  * **return** - (*True, 'ok'*) или (*False, коммент*)
  
Служебные
~~~~~~~~~

Хуки
~~~~

.. py:function:: _pre_commit(work_path, save_path)

  вызов одноимённого хука. Вызывается из ``commit``
  
  .. rubric:: Параметры:
  
  * **work_path** (*unicode*) - путь текущего рабочего файла
  * **save_path** (*unicode*) - путь сохранения файла
  * **return** - (*True, 'Ok!'*) или (*False, coment*)
  
.. py:function:: _post_commit(work_path, save_path)

  вызов одноимённого хука. Вызывается из ``commit``
  
  .. rubric:: Параметры:
  
  * **work_path** (*unicode*) - путь текущего рабочего файла
  * **save_path** (*unicode*) - путь сохранения файла
  * **return** - (*True, 'Ok!'*) или (*False, coment*)

Чтение
""""""

.. py:function:: _read_task(task_name)

  возврат словаря задачи (по ключам из *tasks_keys*, чтение БД) по имени задачи. если нужен объект используем *task.init(name)*.

  .. rubric:: Параметры:

  * **task_name** (*str*) - имя задачи
  * **return** - (*True, task_data(словарь)*) или (*False, коммент*)

Смены статусов
""""""""""""""

.. py:function:: _service_input_to_end(assets)

  изменение статуса текущей сервис задачи (задача инициализирована), по проверке статусов входящих задач. и далее задач по цепочке.
  
  .. note:: данный экземпляр *task* инициализирован.
  
  .. rubric:: Параметры:
  
  * **assets** (*dict*) - словарь всех ассетов по всем типам (ключи - имена, данные - ассеты экземпляры) - результат функции *asset.get_dict_by_name_by_all_types()*
  * **return** - (*True, new_status*) или (*False, коммент*)

.. py:function:: _from_input_status(input_task[, this_task=False])

  возвращает новый статус задачи (текущей - если *this_task=False*), на основе входящей задачи, ``?? не меняя статуса данной задачи``.
  
  .. rubric:: Параметры:
  
  * **input_task** (*task / False*) входящая задача ``?? зачем вообще передавать, если есть есть атрибут input``
  * **this_task** (*task / False*) - если *False* - то предполагается текущая задача
  * **return** - *new_status*

.. py:function:: _this_change_from_end([this_task=False, assets = False])

  замена статусов исходящих задач при изменении статуса текущей задачи с *done* или с *close*.
  
  .. rubric:: Параметры:
  
  * **this_task** (*task / False*) - если *False* то текущая задача
  * **assets** (*dict*) - словарь всех ассетов по всем типам (ключи - имена, данные - ассеты (объекты)) - результат функции *asset.get_dict_by_name_by_all_types()*
  * **return** - (*True, 'Ok!'*) / или (*False, comment*)

.. py:function:: _this_change_to_end(self[, assets = False])

  замена статусов исходящих задач при изменении статуса текущей задачи на *done* или *close*.
  
  .. note:: данный экземпляр *task* инициализирован
  
  .. rubric:: Параметры:
  
  * **assets** (*dict*) - словарь всех ассетов по всем типам (ключи - имена, данные - ассеты (объекты)) - результат функции *asset.get_dict_by_name_by_all_types()*
  * **return** - (*True, 'Ok!'*) / или (*False, comment*)
  
.. py:function:: _service_add_list_to_input(input_task_list)

  добавление списка задач во входящие сервисной задаче, со всеми вытикающими изменениями статусов.

  .. note:: данный экземпляр *task* инициализирован
  
  .. rubric:: Параметры:

  * **input_task_list** (*list*) - список задач (экземпляры)
  * **return** - (*True, (new_ststus, append_task_name_list))* или (*False, коммент*)

.. py:function:: _service_add_list_to_input_from_asset_list(asset_list[, task_data=False])

  добавление задач во входящие сервисной задаче из списка ассетов. Какую именно добавлять задачу из ассета, определяет алгоритм.

  .. rubric:: Параметры:

  * **asset_list** (*list*) - подсоединяемые ассеты (словари, или экземпляры)
  * **task_data** (*dict*) - изменяемая задача, если *False* - значит предполагается, что *task* инициализирован ``лучше не использовать``
  * **return** - (*True, (this_task_data, append_task_name_list)*) ``?? пересмотреть``  или (*False, коммент*)

.. py:function:: _service_remove_task_from_input(removed_tasks_list[, task_data=False, change_status = True])

  удаление списка задач из входящих сервисной задачи.

  .. rubric:: Параметры:

  * **removed_tasks_list** (*list*) - содержит словари удаляемых из инпута задач ``?? переработать - заменить на объекты``
  * **task_data** (*dict*) - изменяемая задача, если *False* - значит предполагается, что *task* инициализирован ``лучше не использовать``
  * **return** - (*True, (new_status, input_list)*) или (*False, коммент*)
      * **new_status** (*str*)- новый статтус данной задачи
      * **input_list** (*list*) - фактически *task.input*

.. py:function:: _service_change_task_in_input(removed_task_data, added_task_data[, task_data=False])

  замена входящей задачи одной на другую для сервисной задачи.

  .. rubric:: Параметры:

  * **removed_task_data** (*dict*) - удаляемая задача ``?? или экземпляр - возможно переработать - заменить на объекты``
  * **added_task_data** (*dict*) - добавляемая задача ``?? или экземпляр - возможно переработать - заменить на объекты``
  * **task_data** (*dict*) - изменяемая задача, если *False* - значит предполагается, что *task* инициализирован. ``лучше не использовать``
  * **return** - (*True, (this_task_data, append_task_name_list)*)  или (*False, коммент*)
  
Прочее
""""""

.. py:function:: _set_branches(branches)

  заполнение ``атрибута класса`` **branches**
  
  .. rubric:: Параметры:
  
  * **branches** (*list*) - список веток получаемый при выполнении ``log.read_log()``
  * **return** - *None*