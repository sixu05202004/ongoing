=====
缓存
=====

.. automodule:: werkzeug.contrib.cache


缓存系统 API
================

.. autoclass:: BaseCache
   :members:


缓存系统
=============

.. autoclass:: NullCache

.. autoclass:: SimpleCache

.. autoclass:: MemcachedCache

.. class:: GAEMemcachedCache

   This class is deprecated in favour of :class:`MemcachedCache` which
   now supports Google Appengine as well.

   .. versionchanged:: 0.8
      Deprecated in favour of :class:`MemcachedCache`.

.. autoclass:: RedisCache

.. autoclass:: FileSystemCache
