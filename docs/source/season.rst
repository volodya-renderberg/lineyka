.. _class-season-page:

Class Season
============

**season(studio)**

**level** = 'project'

.. epigraph::

    Сезон это группа серий, для сериала. Не создаёт файловую структуру.

Данные хранимые в БД (имя столбца : тип данных):

.. code-block:: python

  season_keys = {
  'name': 'text',
  'status':'text',
  'id': 'text',
  }
  
Создание экземпляра класса:
---------------------------

.. code-block:: python
  
  import edit_db as db
  
  project = db.project()
  
  season = db.season(project) # project - обязательный параметр при создании экземпляра season
  # доступ ко всем параметрам и методам принимаемого экземпляра project через season.project
  
Атрибуты
--------

:name: (*str*) - имя сезона (уникально).

:status: (*str*) - *['active', 'none']*

:id: (*str*) - *hex*

:project: (*project*) - экземпляр :ref:`class-project-page`, принимаемый при создании экземпляра класса, содержит все атрибуты и методы :ref:`class-project-page`.

:seasons_list: (*list*) - ``атрибут класса`` список сезонов (экземпляры) даного проекта. Заполняется при выполнеии метода `get_list`_, значение по умолчанию - *[]*.

:dict_by_name: (*dict*) - ``атрибут класса`` словарь сезонов (экземпляры) с ключами по именам. Заполняется при выполнеии метода `get_list`_, значение по умолчанию - *{}*.

:dict_by_id: (*dict*) - ``атрибут класса`` словарь сезонов (экземпляры) с ключами по *id*. Заполняется при выполнеии метода `get_list`_, значение по умолчанию - *{}*.

Методы
------

.. py:function:: init(name[, new=True])

  инициализация (заполнение полей по *season_keys*) по имени.

  **Параметры:**

  * **name** (*str*) - имя серии
  * **new** (*bool*) - если *True* - вернёт новый экземпляр, если *False* - инициализирует текущий
  * **return:**
      :если new = *True*: - season (экземпляр), *None* (при отсутствии данного сезона) 
      :если new = *False*: - (*True, 'Ok!'*) или (*False, коммент*)

.. py:function:: init_by_keys(keys[, new=True])

  инициализация (заполнение полей по *season_keys*) по словарю.

  **Параметры:**

  * **keys** (*dict*) словарь по *season_keys*
  * **new** (*bool*) - если *True* - вернёт новый экземпляр, если *False* - инициализирует текущий
  * **return**
      :если new = *True*: - season (экземпляр)
      :если new = *False*: - (*True, 'Ok!'*) или (*False, коммент*)

.. py:function:: create(name)

  создаёт сезон.

  **Параметры:**

  * **name** (*str*) - имя сезона, должно быть уникально, иначе будет ошибка
  * **return** - (*True, season (экземпляр)*) или (*False, comment*)

.. py:function:: get_list([status='all'])

  возвращает список сезонов (экземпляры). заполняет ``атрибуты класса``: **seasons_list**, **dict_by_name**, **dict_by_id**. (см. `Атрибуты`_ )

  **Параметры:**

  * **status** (*str*) - значения из *['all', 'active', 'none']*
  * **return** - (*True, [список сезонов - экземпляры]*) или (*False, comment*)

.. py:function:: rename(new_name)

  переименовывает текущий сезон.

  **Параметры:**

  * **new_name** (*str*) - новое имя сезона
  * **return** - (*True, 'ok'*) или (*False, comment*)

.. py:function:: stop()

  деактивация текущего сезона. Замена статуса на *'none'*.

  **Параметры:**

  * **name** (*str*) - имя сезона
  * **return** - (*True, 'ok'*) или (*False, comment*)

.. py:function:: start()

  активация текущего сезона. Замена статуса на *'active'*.

  **Параметры:**

  * **name** (*str*) - имя сезона
  * **return** - (*True, 'ok'*) или (*False, comment*)

