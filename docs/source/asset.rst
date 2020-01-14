.. _class-asset-page:

Class Asset
===========

**asset(studio)**

**level** = 'project'

Данные хранимые в БД (имя столбца : тип данных):

.. code-block:: python

  asset_keys = {
  'name': 'text',
  'group': 'text',
  'type': 'text',
  'loading_type': 'text', # способ загрузки ассета object в анимационную сцену, значения из studio.loading_types
  'season': 'text', # ``?``
  'priority': 'integer',
  'description': 'text',
  'content': 'text',
  'id': 'text',
  'status': 'text',
  'parent': 'json' # {'name':asset_name, 'id': asset_id} - возможно не нужно
  }
  
Создание экземпляра класса:
---------------------------

.. code-block:: python
  
  import edit_db as db
  
  project = db.project()
  
  asset = db.asset(project) # project - обязательный параметр при создании экземпляра asset
  # доступ ко всем параметрам и методам принимаемого экземпляра project через asset.project
  
Атрибуты
--------

:name: (*str*) - имя ассета (уникально)

:group: (*str*) - *id* группы

:type: (*str*) - тип ассета из *studio.asset_types*

:loading_type: (*str*) - тип загрузки в анимационную сцену, варианты: **mesh** - загрузка меша из активити ``model``, **group** - загрузка группы из активити ``model``, **rig** - загрузка группы рига из активити ``rig``

:season: (*str*) - *id* сезона ``?``

:priority: (*int*) - [0 - inf]

:description: (*str*) - 

:content: (*str*) - ``?``

:id: (*str*) - *hex*

:status: (*str*) - *['active', 'none']*

:parent': (*dict*) - ``?``

:project: (*project*) - экземпляр :ref:`class-project-page` принимаемый при создании экземпляра класса, содержит все атрибуты и методы :ref:`class-project-page`.

:path: (*str*) - путь к директории ассета на сервере (заполняется при инициализации объекта).

Методы
------

.. py:function:: init(asset_name, new = True)

  заполнение полей экземпляра по studio.asset_keys

  .. rubric:: Параметры:

  * **asset_name** (*str*) - имя ассета. данные ассета будут считаны из базы данных
  * **new** (*bool*) - если *True* - то возвращается новый инициализированный экземпляр класса asset, если *False* - то инициализируется текущий экземпляр
  * **return**:
      * если *new=True* - инициализированный экземпляр
      * если *new=False* - (*True, 'Ok!'*) / или (*False, comment*)

.. py:function:: init_by_keys(keys, new=True)

  заполнение полей экземпляра по studio.asset_keys.

  .. rubric:: Параметры:

  * **keys** (*dict*) - словарь данных ассета, получаемый в из БД
  * **new** (*bool*) - если *True* - то возвращается новый инициализированный экземпляр класса *asset*, если *False* - то инициализируется текущий экземпляр.
  * **return**: 
      * если *new=True* - инициализированный экземпляр, 
      * если *new=False* - (*True, 'Ok!'*)

.. py:function:: create(asset_type, list_keys)

  создание ассетов по списку.

  .. rubric:: Параметры:

  * **asset_type** (*str*) - тип для всех ассетов из *studio.asset_types*
  * **list_keys** (*list*) - список словарей по ключам *asset_keys* обязательные параметры в *keys* (*list_keys*): *name*, *group(id)*.  важный параметр *set_of_tasks* - имя набора задач
  * **return** - (*True, assets_data*) или (*False, comment*)
      * **assets_data** (*dict*) - словарь создаваемых асетов(экземпляры) по именам.

.. py:function:: remove()

  Перемещение текущего ассета в корзину, снятие задач с исполниетлей, изменение статуса и приоритета, разрыв исходящих связей ассета. Физически файлы ассета не удаляются.

  .. rubric:: Параметры:

  * **return** -  (*True, 'Ok!'*) или (*False, comment*).

.. py:function:: copy_of_asset(new_group_name, new_asset_name, new_asset_type, set_of_tasks)

  копирование текущего ассета.

  .. rubric:: Параметры:

  * **new_group_name** (*str*) - имя группы для создаваемого ассета
  * **new_asset_name** (*str*) - имя создаваемого ассета
  * **new_asset_type** (*str*) из *studio.asset_types* - тип создаваемого ассета
  * **set_of_tasks** (*str*) - имя набора задач
  * **return** -  (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: get_list_by_type(asset_type= False)

  возвращает ассеты (экземпляры) по типу. Если не указывать тип ассета, вернёт ассеты по всем типам.

  .. rubric:: Параметры:

  * **asset_type** (*str*) - тип ассета. Если не указывать тип ассета, вернёт ассеты по всем типам
  * **return** (*True, [instances]*) или (*False, comment*)

.. py:function:: get_list_by_all_types()

  возвращает ассеты (экземпляры) по всем типам.
  
  .. note:: Обёртка на *get_list_by_type()*

  .. rubric:: Параметры:

  * **return** - (*True, [instances]*) или (*False, comment*)

.. py:function:: get_list_by_group(group)

  возвращает список ассетов (экземпляры) данной группы.

  .. rubric:: Параметры:

  * **group** (group) - экземпляр группы
  * **return** - (*True, [instances]*) или (*False, comment*)

.. py:function:: get_dict_by_name_by_all_types()

  возвращает словарь ассетов (экземпляры) по именам, по всем типам.

  .. rubric:: Параметры:

  * **return** (*True, {asset_name: экземпляр}*) или (*False, comment*)

.. py:function:: change_group(new_group_id)

  изменение группы текущего ассета (ассет должен быть инициализирован).

  .. rubric:: Параметры:

  * **new_group_id** (*str*) - *id* новой группы
  * **return** -  (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: change_priority(priority)

  изменение приоритета текущего ассета (ассет должен быть инициализирован).

  .. rubric:: Параметры:

  * **priority** (*int*) - новый приоритет
  * **return_data** -  (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: change_description(description)

  изменение описания текущего ассета (ассет должен быть инициализирован).

  .. rubric:: Параметры:

  * **description** (*str*) - новое описание
  * **return** -  (*True, 'Ok!'*) или (*False, comment*)
  
.. py:function:: change_loading_type(loading_type)

  Смена типа загрузки ассета, для типа **object** (ассет должен быть инициализирован).

  .. rubric:: Параметры:

  * **loading_type** (*str*) - тип загрузки, значение из *studio.loading_types*
  * **return** -  (*True, 'Ok!'*) или (*False, comment*)
