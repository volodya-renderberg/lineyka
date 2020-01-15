.. time-zone-page:

Time Zone
=========

Запись в ``utc``. 
    * Во всех ``write`` функциях использовать ``datetime.datetime.utcnow()``
При чтении конвертировать в локальную таймзону. 
    * В ``database.read()`` - переводить ``utc`` в локальное время, в том же цикле, где форматируется ``json``. 
    
::
    
    import tzlocal
    import pytz
    
    utc=pytz.utc
    tz_local=tzlocal.get_localzone()
    
    # в цикле
    # локализация времени из базы данных к utc
    utc_datetime=utc.localize(datetime_from_database)
    # конвертирование ко времени локальной таймзоны
    local_datetime=utc_datetime.astimezone(tz_local)


