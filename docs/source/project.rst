.. _class-project-page:

Class Project
=============

**project(studio)**

**level** = 'studio'

Данные хранимые в БД (имя столбца : тип данных):

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
  
Создание экземпляра класса:
---------------------------

.. code-block:: python
  
  import edit_db as db
  
  project = db.project()

Атрибуты
--------

:name: (*str*) - имя проекта (уникально).

:path: (*str*) - путь до директории проекта.

:status: (*str*) - ``['active', 'none']``

:project_database: (*list*) - параметры используемой базы данных, по умолчанию: ``['sqlite3', False]``

:chat_img_path: (*str*) - путь до директории с картинками чата.

:list_of_assets_path: (*str*) - путь до файла с временными данными создаваемых ассетов.

:preview_img_path: (*str*) - путь до директории с превью картинок чата.

:fps: (*float*) - **fps** проекта (по умолчанию 24).

:units: (*str*) - юниты 3d сцен ``['m', 'cm', 'mm']`` по умолчанию ``'m'``

:list_active_projects: (*list*) - ``атрибут класса`` список активных проектов, только имена. . Заполняется при выполнеии метода `get_list`_, значение по умолчанию - *[]*.

:list_projects:  (*list*) - ``атрибут класса`` список всех проектов (экземпляры). Заполняется при выполнеии метода `get_list`_, значение по умолчанию - *[]*.

:dict_projects: (*dict*) - ``атрибут класса`` словарь содержащий все проекты (экземпляры) с ключами по именам. . Заполняется при выполнеии метода `get_list`_, значение по умолчанию - *{}*.

Методы
------
  
.. py:function:: add_project(project_name, project_path)

  создаёт проект.
  
  .. note:: при создании проекта новый экземпляр не возвращается, заполняются поля текущего экземпляра.
  
  **Параметры:**
  
  * **project_name** (*str*) - имя проекта, если имя не указано, но указана директория, проект будет назван именем директории
  * **project_path** (*str - path*) - путь к директории проекта, если путь не указан, директория проекта будет создана в директории студии
  * **return** - (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: init(name[, new=True])

  инициализирует экземпляр по имени (заполняет поля экземпляра), чтение БД.
  
  **Параметры:**
  
  * **name** (*str*) - имя проекта
  * **new** (*bool*) - если new= *True* - возвращает новый инициализированный экземпляр, если *False* то инициализирует текущий экземпляр
  * **return** - новый экземпляр (*project*) / (*True,  'Ok!'*) или (*False, comment*)

.. py:function:: init_by_keys(keys[, new=True])

  инициализирует экземпляр по словарю (заполняет поля экземпляра), без чтения БД
  
  **Параметры:**
  
  * **keys** (*dict*) - словарь по *projects_keys*
  * **new** (*bool*) - если new= *True* - возвращает новый инициализированный экземпляр, если *False* то инициализирует текущий экземпляр
  * **return**  - новый экземпляр (*project*) / (*True,  'Ok!'*) или (*False, comment*)

.. py:function:: get_list()

  чтение существующих проектов.
  
  .. note:: не возвращает экземпляры, только заполняет ``поля класса``: **list_active_projects**, **list_projects**, **dict_projects**. (см. `Атрибуты`_ )
  
  * **return** - (*True,  'Ok!'*) или (*False, comment*)

.. py:function:: rename_project(new_name)
  
  переименование проекта (данного экземпляра), заполняются поля экземпляра, ``перезагружает studio.list_projects. ????``
  
  **Параметры:**
  
  * **new_name** (*str*) - новое имя отдела
  * **return** - (*True, 'Ok!'*) или (*False, comment*).

.. py:function:: remove_project()

  удаляет проект из БД (не удаляя файловую структуру), ``перезагружает studio.list_projects ???``, приводит экземпляр к сосотоянию *empty* (все поля по *projects_keys* = *False*).
  
  **Параметры:**
  
  * **return** - (*True, 'Ok!'*) или (*False, comment*).

.. py:function:: edit_status(status)

  изменение статуса проекта.
  
  **Параметры:**
  
  * **status** (*str*) - присваиваемый статус
  * **return** - (*True, 'Ok!'*) или (*False, comment*)
  
.. py:function:: change_fps(fps)

  изменение fps проекта, предполагается автоматическое назначение этого параметра в сценах.
  
  .. rubric:: Параметры:
  
  * **fps** (*float*) - fps
  * **return** - (*True, 'Ok!'*) или (*False, comment*)
  
.. py:function:: change_units(fps)

  изменение юнитов проекта, параметр для 3d сцен. Предполагается автоматическое назначение этого параметра в сценах.
  
  .. rubric:: Параметры:
  
  * **units** (*str*) - юниты для 3d сцен, значение из *studio.projects_units*
  * **return** - (*True, 'Ok!'*) или (*False, comment*)
  
Служебные
~~~~~~~~~

.. py:function:: __make_folders(root)

  создаёт файловую структуру проекта, при отсутствии.
  
  **Параметры:**
  
  * **root** (*str - path*) - корневой каталог проекта
  * **return** - *None*.

.. py:function:: _write_settings()

  запись настроек проекта в файл *project_path/studio.PROJECT_SETTING*
  
  .. note:: Выполнять в каждой процедуре по редактированию параметров проекта.
  
  .. rubric:: Параметры:
  
  * **return** - (*True, 'Ok!'*) или (*False, comment*)
  
.. py:function:: _read_settings()

  чтение словаря параметров проекта из файла *project_path/studio.PROJECT_SETTING*
  
  .. rubric:: Параметры:
  
  * **return**:
      * *data* - словарь по ключам *studio.projects_keys*
      * *None* в случае остутствия файла.