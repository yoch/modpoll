Changelog
=========

`2.0.0 <https://github.com/yoch/modpoll2mqtt/compare/v1.6.0...v2.0.0>`__ (2026-06-10)
-------------------------------------------------------------------------------------

Project
~~~~~~~

-  forked from `modpoll <https://github.com/gavinying/modpoll>`__; PyPI
   package renamed to ``modpoll2mqtt``, repository ``yoch/modpoll2mqtt``
-  CLI command and Python module remain ``modpoll``

Features
~~~~~~~~

-  semantic MQTT write by CSV reference on ``modpoll/<device>/set`` with
   payload ``ref`` and ``value`` (device from topic; scale, dtype, and
   endianness handled automatically)
-  subscribe pattern ``modpoll/+/set`` by default

BREAKING CHANGES
~~~~~~~~~~~~~~~~

-  removed low-level MQTT write format (``object_type``, ``address``,
   ``value``); use topic + ``ref`` and ``value`` instead
-  duplicate reference names on the same device now abort config loading
   (previously warned and overwrote)
