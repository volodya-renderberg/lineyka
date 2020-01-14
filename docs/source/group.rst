.. _class-group-page:

Class Group
===========

**group(studio)**

**level** = 'project'

Данные хранимые в БД (имя столбца : тип данных):

.. code-block:: python
  
  group_keys = {
  'name': 'text',
  'type': 'text',
  'season': 'text',
  'description': 'text',
  'id': 'text',
  }
  
Создание экземпляра класса:
---------------------------

.. code-block:: python
  
  import edit_db as db
  
  project = db.project()
  group = db.group(project) # project - обязательный параметр при создании экземпляра group
  # доступ ко всем параметрам и методам принимаемого экземпляра project через group.project
  
Атрибуты
--------

:name: (*str*) - имя группы (уникально). 

:type: (*str*) - тип ассетов данной группы, из *studio.asset_types* 

:season: (*str*) - *id* сезона ``?`` 

:description: (*str*) -  

:id: (*str*) - *hex*

:project: - экземпляр :ref:`class-project-page`, принимаемый при создании экземпляра класса, содержит все атрибуты и методы :ref:`class-project-page`.

:list_group: - ``атрибут класса`` список групп (экземпляры) даного проекта. Заполняется привыполнеии метода `get_list`_, значение по умолчанию - *False*.

:dict_by_name: - ``атрибут класса`` словарь групп (экземпляры) с ключами по именам. Заполняется привыполнеии метода `get_list`_, значение по умолчанию - *False*.

:dict_by_id: - ``атрибут класса`` словарь групп (экземпляры) с ключами по *id*. Заполняется привыполнеии метода `get_list`_, значение по умолчанию - *False*.

:dict_by_type: - ``атрибут класса`` словарь групп: ключи - *type*, значения - списки групп (экземпляры). Заполняется привыполнеии метода `get_list`_, значение по умолчанию - *False*.

  
Методы
------
  
.. py:function:: init(group_name[, new = True])

  заполнение полей экземпляра по *group_keys*.

  **Параметры:**
  
  * **group_name** (*str*) - имя группы. данные группы будут считаны из базы данных
  * **new** (*bool*) - если *True* - то возвращается новый инициализированный экземпляр класса group, если *False* - то инициализируется текущий экземпляр
  * **return:** 
      :если new= *True*: - инициализированный экземпляр, 
      :если new= *False*: - (*True, 'Ok!'*) / или (*False, comment*)

.. py:function:: init_by_keys(keys[, new=True])

  заполнение полей экземпляра по *group_keys*.

  **Параметры:**
  
  * **keys** (*dict*) - словарь данных группы по *group_keys*
  * **new** (*bool*) - если *True* - то возвращается новый инициализированный экземпляр класса *group*, если *False* - то инициализируется текущий экземпляр
  * **return:**
      :если new= *True*: - инициализированный экземпляр
      :если new= *False*: - (*True, 'Ok!'*)

.. py:function:: create(keys[, new=True])

  создание группы

  **Параметры:**
  
  * **keys** (*dict*) - словарь по *group_keys* (*name* и *type* (тип ассетов) - обязательные ключи)
  
  .. note:: если *type* подразумевает привязку к сезону(*type* из *studio.asset_types_with_season*), то *season* - так же обязательный параметр.
  
  * **new** (*bool*) - возвращать новый экземпляр или инициализировать текущий
  * **return:**
      :если *new* = *True*: - (*True, new_group (group)*)
      :если *new* = *False*: - (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: create_recycle_bin()

  создание группы - корзина, для удалённых ассетов. Процедура выполняется при создании проекта.

  **Параметры:**

  * **return** - (*True, 'Ok!'*) или (*False, comment*).

.. py:function:: get_list([f = False])

  возвращает список групп (экземпляры) согласно фильтру f.
  
  .. note:: заполняет ``атрибуты класса``: **list_group**, **dict_by_name**, **dict_by_id**, **dict_by_type** (см. `Атрибуты`_ )

  **Параметры:**
  
  * **f** (*list / bool*) - *False* или список типов(типы ассета)
  * **return** (*True, [список групп - экземпляры]*)  или (*False, comment*).

.. py:function:: get_by_keys(keys)

  возвращает список групп(экземпляры) удовлетворяющих *keys*.

  **Параметры:**
  
  * **keys** (*dict*) - словарь по *group_keys*
  * **return** (*True, [список групп - экземпляры]*)  или (*False, comment*)

.. py:function:: get_by_name(name)

  возвращает группу(экземпляр) по имени.
  
  .. note:: Обёртка на *get_by_keys()*

  **Параметры:**
  
  * **name** (*str*) - имя группы
  * **return** (*True, группа - экземпляр*)  или (*False, comment*)

.. py:function:: get_by_id(id)

  возвращает группу(экземпляр) по *id*.
  
  .. note:: Обёртка на *get_by_keys()*

  **Параметры:**
  
  * **id** (*str*) - *id* группы
  * **return** (*True, группа - экземпляр*)  или (*False, comment*)

.. py:function:: get_by_season(season)

  возвращает список групп(экземпляры) данного сезона.
  
  .. note:: Обёртка на *get_by_keys()*

  **Параметры:**
  
  * **season** (*str*) - сезон
  * **return** (*True, [список групп - экземпляры]*)  или (*False, comment*)

.. py:function:: get_by_type_list(type_list)

  возвращает список групп(словари) по списку типов.
  
  .. note:: Обёртка на *get_list()*

  **Параметры:**
  
  * **type_list** (*list*) - список типов ассетов из *asset_types*
  * **return** (*True, [список групп - экземпляры]*)  или (*False, comment*)

.. py:function:: rename(new_name)

  переименование текущего объекта группы.

  **Параметры:**
  
  * **new_name** (*str*) - новое имя группы
  * **return** - (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: edit_comment(comment)

  редактирование комментария текущего объекта группы.

  **Параметры:**
  
  * **comment** (*str*) - текст коментария
  * **return** - (*True, 'Ok!'*) или (*False, comment*)
