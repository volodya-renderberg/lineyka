.. _class-set-of-tasks-page:

Class Set_of_tasks
==================

**set_of_tasks(studio)**

**level** = 'studio'

Редактирование наборов задач.

Данные хранимые в БД (имя столбца : тип данных):

.. code-block:: python

  set_of_tasks_keys = {
  'name':'text',
  'asset_type': 'text',
  'loading_type': 'text',
  'sets':'json',
  'edit_time': 'timestamp',
  }
  
Структура словарей атрибута *sets*:
  
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
  
Атрибуты
--------

:name: (*str*) - имя сета (уникально)

:asset_type: (*str*) - тип ассета из *studio.asset_types*

:loading_type: (*str*) - # способ загрузки ассета для типа ***object***, значения из *studio.loading_types*

:sets: (*list*) - сами задачи, список словарей с ключами по *sets_keys* (ключи соответсвую атрибутам класса Task).

:edit_time: (*timestamp*) - дата и время последних изменений.
  
Методы
------
  
.. py:function:: init_by_keys(keys[, new=True])

  инициализация по словарю.
  
  **Параметры:**
  
  * **keys** (*dict*) - словарь по *set_of_tasks_keys*
  * **new** (*bool*) - если *True* - то возврат нового объекта, если *False* - то инициализация текущего
  * **return** - new_ob или (*True, 'Ok!'*)

.. py:function:: create(name, asset_type[, loading_type=False, keys = False, force=False])

  создание набора задач.
  
  **Параметры:**
  
  * **name** (*str*) - имя набора
  * **asset_type** (*str*) - должен быть из *studio.asset_types*
  * **loading_type** (*str*) - тип загрузки для *object* ассета, из *studio.loading_types*
  * **keys** (*list/ bool*) - список задач(словари по *sets_keys*), если *False* - будет создан пустой набор
  * **force** (*bool*) - если *False* - то будет давать ошибку при совпадении имени, если *True* - то будет принудительно перименовывать с подбором номера
  * **return** - (*True, new_ob*) или (*False, comment*)

.. py:function:: get_list([f = False, path = False])

  чтение всех наборов (объекты).
  
  **Параметры:**
  
  * **f** (*dict*) - фильтр ро ключам *set_of_tasks_keys*, используется только для чтения из базы данных при path= *False*
  * **path** (*bool / str*) - если указан - то чтение из файла *.json*, если - *False* - то чтение из базы данных
  * **return** - (*True, [список объектов]*) или (*False, comment*)

.. py:function:: get_list_by_type(asset_type)

  чтение наборов (объекты) определённого типа.
  
  .. note:: обёртка на *get_list(f)*
  
  **Параметры:**
  
  * **asset_type** (*str*) - должен быть из *studio.asset_types*
  * **return** - (*True, [список объектов]*) или (*False, comment*)

.. py:function:: get_dict_by_all_types()

  чтение всех наборов (объекты) в словарь с ключами по типам ассетов.
  
  **Параметры:**
  
  * **return** - (*True, {тип ассета : {имя сета: объект, ...}, ...}*) или (*False, comment*)

.. py:function:: get(name)

  чтение набора по имени.
  
  .. note:: обёртка на get_list(f)
  
  **Параметры:**
  
  * **name** (*str*) - имя набора
  * **return** - (*True, объект*) или (*False, comment*)

.. py:function:: remove([name=False])

  удаление набора.
  
  **Параметры:**
  
  * *name** (*str*) - если *False* - то удаляется текущий инициализированный объект: удаляется строка из БД - поля объекта переписываются на *False*
  * **return** - (*True, 'ok'*) или (*False, comment*)

.. py:function:: rename(new_name[, name=False])

  переименование набора.

  **Параметры:**
  
  * **new_name** (*str*) - новое имя сета
  * **name** (*str*) - имя переименоваваемого сета, если *False* - переименовывается текущий объект
  * **return** - (*True, 'ok'*) или (*False, comment*)

.. py:function:: edit_asset_type(asset_type[, name=False])

  смена типа набора.

  **Параметры:**
  
  * **asset_type** (*str*) - новый тип, должен быть из *studio.asset_types*
  * **name** (*str/bool*) - имя изменяемого сета, если *False* - то редактируется текущий объект
  * **return** - (*True, 'ok'*) или (*False, comment*)
  
.. py:function:: edit_loading_type(loading_type)

  редактирование параметра ``loading_type``.
  
  .. note:: только для ассетов типа ``"object"``

  **Параметры:**
  
  * **loading_type** (*str*) - значение из *studio.loading_types*
  * **return** - (*True, 'ok'*) или (*False, comment*)

.. py:function:: edit_sets(data[, name=False])

  редактирование значения ``sets``

  **Параметры:**
  
  * **data** (*list*) - список словарей по *sets_keys*
  * **name** (*bool/str*) - имя изменяемого сета, если *False* - то редактируется текущий объект
  * **return** - (*True, 'ok'*) или (*False, comment*)

.. py:function:: copy(new_name[, old_name=False])

  создание копии сета.

  **Параметры:**
  
  * **new_name** (*str*) - имя создаваемого сета
  * **old_name** (*bool / str*) - имя копируемого сета, если *False* - то копируется текущий
  * **return** - (*True, объект*) или (*False, comment*)

.. py:function:: save_to_library(path[, save_objects=False])

  запись библиотеки наборов задач в *.json* файл.

  **Параметры:**
  
  * **path** (*str*) - путь сохранения
  * **save_objects** (*bool / list*) - список объектов (*set_of_tasks*) - если *False* - то сохраняет всю библиотеку
  * **return** - (*True, 'ok'*) или (*False, comment*)

.. py:function:: load_from_library(data)

  запись наборов задач в студийный набор из внешнего файла.
  
  .. note:: возможно больше не нужно / это сочетание *get_list(path) + create()*

  **Параметры:**
  
  * **data** - словарь из внешнего файла, по структуре аналогичен словарю *set_of_tasks* в системе происходит запись данных в *set_of_tasks*, при этом данные по совпадающим ключам перезаписываются на новые.
  * **return** - (*True, 'ok'*) или (*False, comment*)
