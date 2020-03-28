.. data-exchange-page:

Data Exchange
=============

.. image:: images/django_exchange.png

Обмен данными с линейкой через модуль :ref:`django_connect-page`.

Arist
-----

* Локальное хранение данных юзера в формате ``django`` в файле :attr:`edit_db.studio.USER_DATA_FILE_NAME`

* Конвертирование данных в формат линейки при инициализации экземпляра в процедуре :func:`edit_db.artist.init_by_keys`


Data to Lineyka
---------------

На стороне django
~~~~~~~~~~~~~~~~~

* :func:`edit_db.shortcuts.inst_to_json` 
	* объект джанго в словарь,
	* удаление лишних полей,
	* дату/время из *utc* в местное время пользователя. ``!!!! сделать``
	* преобразование словаря в строку.

На стороне Lineyka
~~~~~~~~~~~~~~~~~~

* :func:`django_connect._input_data_converter`
	* ццц

