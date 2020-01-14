.. _class-studio-page:

Class Studio
============

**studio()**

**level** = 'studio'

Атрибуты
--------

:task_status: (*tuple*) - все возможные статусы задач: ``('null','ready', 'ready_to_send', 'work', 'work_to_outsorce', 'pause', 'recast', 'checking', 'done', 'close')``

:working_statuses: (*list*) - рабочие статусы (задачи с этими статусами отображаются в списке задач исполнителя) ``['ready', 'ready_to_send', 'work', 'work_to_outsorce', 'pause', 'recast']``

:end_statuses: (*tuple*) - статусы завершения работы над задачами (задачи с этими статусами не отображаются в списке задач исполнителей) ``('done', 'close')``

:studio_database: (*list*) - параметры используемой базы данных, по умолчанию: ``['sqlite3', False]``

:studio_folder: (*str*) - ``атрибут класса`` путь к директории хранения мета данных студии.

:tmp_folder: (*str*) - ``атрибут класса`` путь к директории хранения временных рабочих файлов.

:convert_exe: (*str*) - ``атрибут класса`` путь к *exe* файлу *convert* приложения *Image Magick*.

Методы
------

.. py:function:: set_studio(path)
  
  определяет директорию для хранения мета данных студии. Заполняет ``атрибут класса`` *studio_folder*. (см. `Атрибуты`_ )
  
  .. note:: в редких случаях там же могут создаваться и директории проектов (временные студии для аутсорса).
  
  .. rubric:: Параметры:
  
  * **path** (*str*) - путь к директории студии
  * **return** - (*True, 'Ok!'*) или (*False, Comment*)
  
.. py:function:: set_tmp_dir(path)

  определяет директорию для расположения временных рабочих файлов, по умолчанию системная темп директория. Заполняет ``атрибут класса`` *tmp_folder*. (см. `Атрибуты`_ )
  
  .. rubric:: Параметры:
  
  * **path** (*str*) - путь к директории
  * **return** - (*True, 'Ok!'*) или (*False, Comment*)
  
.. py:function:: set_convert_exe_path(path)

  определяет путь к *exe* файлу *convert* приложения *Image Magick*. Заполняет ``атрибут класса`` *convert_exe*. (см. `Атрибуты`_ )
  
  .. note:: Приложение *Image Magick* используется для редактирования картинок: конвертирование в *.png* при паблише и создания превью.
  
  .. rubric:: Параметры:
  
  * **path** (*str*) - путь к файлу *convert.exe*
  * **return** - (*True, 'Ok!'*) или (*False, Comment*)
  
.. py:function:: set_share_dir(path)

  пока не используется

.. py:function:: get_share_dir()

  пока не используется
  
.. py:function:: get_extension_dict()

  возвращает словарь соответствия расширений файлов и соответствующих им приложений. *extension_dict* - это словарь: **ключи** - расширения файлов, **значения** - экзешники для открытия этих типов файлов.

  .. rubric:: Параметры:
  
  * **return** - (*True, extension_dict*)  или (*False, Comment*)

.. py:function:: edit_extension_dict(key, path)

  редактирование словаря соответствия расширений файлов и соответствующих им приложений *extension_dict*.
  
  .. rubric:: Параметры:
  
  * **key** (*str*) - расширение файла с точкой, например: *'.blend'*
  * **path** (*str*) - путь к исполняемому файлу приложения, или имя исполняемого файла (если позволяют настройки переменной *PATH* системы)
  * **return** - (*True, 'Ok!'*) или (*False, Comment*)

.. py:function:: edit_extension(extension, action[, new_extension = False])

  редактирование ключей словаря соответствия расширений файлов и соответствующих им приложений, добавляет новые расширения, удаляет расширения, меняет расширения на другие, оставляя содержание.
  
  .. rubric:: Параметры:
  
  * **extension** (*str*) - расширение файлов (запись с точкой, например *'.blend'*)
  * **action** (*str*) - действие из списка *['ADD', 'REMOVE', 'EDIT']*
      * *ADD* - будет добавлен новое расширение по значению *extension*
      * *REMOVE* - будет удалено расширение по значению *extension*
      * *EDIT* - расширение по значению *extension* будет заменено на расширение по значению *new_extension* - при этом приложение для открытия файлов удаляемого расширения будет перезаписано на новое расширение
  * **new_extension** (*str*) - новое расширение на замену старому. Имет смысл только когда *action = EDIT*
  * **return** - (*True, 'Ok!'*) или (*False, Comment*)
  
.. py:function:: set_work_folder(path)

  определение пути до рабочей директории пользователя, заполнение поля ``studio.work_folder``. Пользовательская настройка запись в ``.init.py``
  
  .. rubric:: Параметры:
  
  * **path** (*str*) - путь до директории.
  * **return** - (*True, ok*) или (False, comment)
  
.. py:function:: _template_version_num(version)

  преобразование номера версии к правильному строковому формату
  
  .. rubric:: Параметры:
  
  * **version** (*int / str*) - номер версии число или строка, преобразуемая в строку
  * **return** (*True, version_str*) или (*False*, comment) - если переданная строка не преобразуется в число.
  
.. py:function:: _template_get_work_path(c_task[, version=False])

  получение шаблоного пути до *commit* или *pull* версии рабочего файла или пути к его активити (в локальной *work* директории).
  
  .. rubric:: Параметры:
  
  * **c_task**  (*task*) - задача, для которой ищется файл.
  * **version** (False / int / str) - номер версии или *False* - в этом случае возврат только пути до активити.
  * **return** - (*True, path*) или (*False, Comment*)
  
.. py:function:: _template_get_push_path(c_task[, version=False, branches=False, look=False])

  получение шаблоного пути до *push* версии файла или пути к его активити на сервере студии.
  
  .. rubric:: Параметры:
  
  * **c_task**  (*task*) - задача, для которой ищется файл.
  * **version** (*False / int / str*) - номер версии или *False* - в этом случае возврат только пути до активити.
  * **branches** (*bool / list*) - список веток из которых делался *push* - для *task_type* = *sketch*
  * **look** (*bool*) - рассматривается только при *task_type* = *sketch*, если *False* - то используется *c_task.extension*, если *True* - то используется *studio.look_extension* (список путей для просмотра)
  * **return** - (*True, path или path_dict - ключи имена веток*) или (*False, Comment*)

.. py:function:: _template_get_publish_path(c_task[, version=False, branches=False, look=False])

  получение шаблонных путей для *publish* версий на сервере студии.
  
  .. note:: Если не передавать ``version`` - то будет получен путь к файлам, которые располагаются сверху директорий версий - это файлы последней версии.
  
  * **c_task**  (*task*) - задача, для которой ищется файл.
  * **version** (*False / int / str*) - номер версии или *False* - в этом случае путь до финальной версии (файлы сверху директорий версий).
  * **branches** (*bool / list*) - список веток из которых делался *push* или *publish* (в случае репаблиша) - для мультипаблиша (например *task_type* = *sketch*)
  * **look** (*bool*) - рассматривается только при *task_type* = *sketch*, если *False* - то используется *c_task.extension*, если *True* - то используется *studio.look_extension* (список путей для просмотра)
  * **return** - (*True, (path или path_dict - ключи имена веток)*) или (*False, Comment*)
