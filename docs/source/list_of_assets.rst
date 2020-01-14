.. _class-list_of_assets-page:

Class List_of_assets
====================

**list_of_assets(studio)**

**level** = 'project'

.. epigraph::

    Запись и редактирование временного списка ассетов {*имя, тип, set_of_tasks*} из редактора создания асетов. Запись в формат *json*, после создания ассетов, список очищается.

Данные хранимые в БД (имя столбца : тип данных):

.. code-block:: python

  list_of_assets_keys = [
    'asset_name', # text
    'asset_type', # text
    'set_of_tasks', # text
    ]
    
Создание экземпляра класса:
---------------------------

.. code-block:: python
  
  import edit_db as db
  
  project = db.project()
  group = db.group(project)
  
  list_of_assets = db.list_of_assets(group) # group - обязательный параметр при создании экземпляра list_of_assets
  # доступ ко всем параметрам и методам принимаемого экземпляра group - через list_of_assets.group
  
Атрибуты
--------

:asset_name: (*str*) - имя ассета

:asset_type: (*str*) - тип ассета

:set_of_tasks: (*str*) - название набора задач

:group: (*group*) - экземпляр :ref:`class-group-page` принимаемый при создании экземпляра класса, содержит все атрибуты и методы :ref:`class-group-page`.

Методы
------

.. py:function:: save_list(rows[, group_name = False])

  запись списка ассетов.

  .. rubric:: Параметры:

  * **rows** (*list*) - список ассетов (словари по *list_of_assets_keys*)
  * **group_name** (*str*) - имя группы, не требуется если группа инициализирована ``лучше не использовать``
  * **return** (*True, 'ok'*) или (*False, comment*)

.. py:function:: get_list()

  чтение всех данных в словарь по группам.

  .. rubric:: Параметры:

  * **return** (*True, {имя группы: [список ассетов(словари), ...], ...}*) или (*False, comment*)

.. py:function:: get([group_name = False])

  чтение списка ассетов данной группы.

  .. rubric:: Параметры:

  * **group_name** (*str*) - имя группы, не требуется если группа инициализирована ``лучше не использовать``
  * **return** (*True, [список ассетов (словари)]*) или (*False, comment*)

.. py:function:: remove([group_name = False])

  удаление списка ассетов данной группы.

  .. rubric:: Параметры:

  * **group_name** (*str*) - имя группы, не требуется если группа инициализирована ``лучше не использовать``
  * **return** (*True, 'ok'*) или (*False, comment*)