.. _class-database-page:

Class Database
==============

**database(studio)**

Методы
------

.. py:function:: get(level, read_ob, table_name, com[, table_root=False])

  чтение БД.

  **Параметры:**

  * **level** (*str*) - 'studio' or 'project'
  * **read_ob** (*studio/project*) - экземпляр класса студии или проекта
  * **com** (*str*) - команда для базы данных mysql
  * **table_root** (*str*) - для тех случаев когда имя файла ДБ(sqlite3) не соответствует имени таблицы, если есть table_root - имя файла ДБ будет определяться по нему table_root - * может быть как именем таблицы - например: 'assets', так и именем файла - .assets.db
  * **return** - (*True, [строки таблицы базы данных - словари]*) или (*False, comment*)

.. py:function:: set_db(level, read_ob, table_name, com[, data_com=False, table_root=False])

  внесение изменений в таблицу базы данных.

  **Параметры:**

  * **level** (*str*)- 'studio' or 'project'
  * **read_ob** (*studio/project*) - экземпляр класса студии или проекта
  * **com** (*str*)- команда для базы данных mysql
  * **data_com** (*tuple*)- кортеж значений для com
  * **table_root** (*str*)- для тех случаев когда имя файла ДБ(sqlite3) не соответствует имени таблицы, если есть table_root - имя файла ДБ будет определяться по нему. table_root - может быть как именем таблицы - например: 'assets', так и именем файла - .assets.db
  * **return** - (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: create_table(level, read_ob, table_name, keys[, table_root = False])
    
  создание таблицы при её отсутствии.
  
  **Параметры:**

  * **level** (*str*)- 'studio' or 'project'
  * **read_ob** (*studio/project*) - экземпляр класса студии или проекта
  * **table_name** (*str*)- имя таблицы
  * **keys** (*dict*)- словарь ключей данного типа таблицы, например tasks_keys
  * **table_root** (*str*)- для тех случаев когда имя файла ДБ(sqlite3) не соответствует имени таблицы, если есть table_root - имя файла ДБ будет определяться по нему table_root - может быть как именем таблицы - например: 'assets', так и именем файла - .assets.db
  * **return** - (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: insert(level, read_ob, table_name, keys, write_data[, table_root=False])

  запись строк в таблицу, перед записью запускает процедуру создания таблицы - create_table.
  
  **Параметры:**

  * **level** (*str*)- 'studio' or 'project'
  * **read_ob** (*studio/project*) - экземпляр класса студии или проекта
  * **table_name** (*str*)- имя таблицы
  * **keys** (*dict*)- словарь ключей данного типа таблицы, например tasks_keys
  * **write_data** (*dict*)- словарь по ключам keys, также может быть списком словарей, для записи нескольких строк
  * **table_root** (*str*)- для тех случаев когда имя файла ДБ(sqlite3) не соответствует имени таблицы, если есть table_root - имя файла ДБ будет определяться по нему table_root - может быть как именем таблицы - например: 'assets', так и именем файла - .assets.db
  * **return** - (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: read(level, read_ob, table_name, keys[, columns = False, where=False, table_root=False])

  чтение таблицы бд.
  
  **Параметры:**

  * **level** (*str*)- 'studio' or 'project'
  * **read_ob** (*studio/project*) - экземпляр класса студии или проекта
  * **table_name** (*str*)- имя таблицы
  * **keys** (*dict*)- словарь ключей данного типа таблицы, например tasks_keys
  * **columns** (*dict*)- False - означает все столбцы если не False - то список столбцов
  * **where** (*dict*)- 1) строка условия, 2) словарь по *keys*, может иметь ключ условия - *'condition'* значения из *[or, end]* 3) *False* - значит выделяется всё
  * **table_root** (*str*)- для тех случаев когда имя файла ДБ(sqlite3) не соответствует имени таблицы, если есть table_root - имя файла ДБ будет определяться по нему. table_root - может быть как именем таблицы - например: 'assets', так и именем файла - .assets.db
  * **return** - (*True, [строки таблицы базы данных - словари]*) или (*False, comment*)
  
  .. note:: при остутсвии таблицы вернёт - (True, [])

.. py:function:: update(level, read_ob, table_name, keys, update_data, where[, table_root=False])

  внесение изменений в таблицу бд.
  
  **Параметры:**

  * **level** (*str*)- 'studio' or 'project'
  * **read_ob** (*studio/project*) - экземпляр класса студии или проекта
  * **table_name** (*str*)- имя таблицы
  * **keys** (*dict*)- словарь ключей данного типа таблицы, например tasks_keys
  * **update_data** (*dict*)- словарь по ключам из keys
  * **where** (*dict*)- словарь по ключам, так как значения маскируются под "?" не может быть None или False
  * **table_root** (*str*)- для тех случаев когда имя файла ДБ(sqlite3) не соответствует имени таблицы, если есть table_root - имя файла ДБ будет определяться по нему. table_root - может быть как именем таблицы - например: 'assets', так и именем файла - .assets.db
  * **return** - (*True, 'Ok!'*) или (*False, comment*)

.. py:function:: delete(level, read_ob, table_name, where[, table_root=False])

  удаление строкит из таблицы БД.
  
  **Параметры:**

  * **level** (*str*)- 'studio' or 'project'
  * **read_ob** (*studio/project*) - экземпляр класса студии или проекта
  * **table_name** (*str*)- имя таблицы
  * **where** (*dict*)- словарь по ключам, так как значения маскируются под "?" не может быть None или False
  * **table_root** (*str*)- для тех случаев когда имя файла ДБ(sqlite3) не соответствует имени таблицы, если есть table_root - имя файла ДБ будет определяться по нему. table_root - может быть как именем таблицы - например: 'assets', так и именем файла - .assets.db
  * **return** - (*True, 'Ok!'*) или (*False, comment*)
