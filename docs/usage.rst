Basic Usage
===========

.. argparse::
    :ref: modpoll.arg_parser.get_parser
    :prog: modpoll

The `config` option is required.


Commandline Usage
------------------

- Connect to Modbus TCP device

  .. code-block:: shell

    modpoll --tcp 192.168.1.10 --config examples/modsim.csv

- Connect to Modbus serial device

  .. code-block:: shell

    modpoll --serial /dev/ttyUSB0 --serial-baud 9600 --config contrib/eniwise/scpms6.csv

- Connect to Modbus TCP device and publish data to remote MQTT broker

  .. code-block:: shell

    modpoll --tcp 192.168.1.10 --config examples/modsim.csv --mqtt-host broker.emqx.io

- Connect to Modbus TCP device and export data to local csv file

  .. code-block:: shell

    modpoll --tcp modsim.topmaker.net --config https://raw.githubusercontent.com/gavinying/modpoll/main/examples/modsim.csv --export data.csv

Configuration File
------------------

The configuration file (`--config`) is a CSV file that defines the devices, pollers, and references to be read.

Coil and discrete input references
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On ``coil`` or ``discrete_input`` pollers:

- ``5,bool`` reads a **single coil/discrete input** at Modbus address 5 and publishes one boolean value.
- ``0,bool8`` / ``0,bool16`` read a **legacy bit group** (8 or 16 booleans). With ``poll,coil,0,16``, group address ``1`` returns Modbus coil addresses 8–15 (often labeled coils 9–16 in vendor tables). If the poll ends before the full group is read, missing bits are padded with ``false``.
- ``address:bit`` syntax is **not** supported on coil/discrete_input pollers.

Register bit references
^^^^^^^^^^^^^^^^^^^^^^^

For register references (i.e., Holding or Input registers) with a ``dtype`` of ``bool``, you can specify a single bit to be extracted from the 16-bit register. This is done by appending ``:bit`` to the address, where ``bit`` is an integer from 0 to 15.

- ``40110``: Reads the entire 16-bit register at address 40110.
- ``40110:15``: Reads the 16-bit register at address 40110, extracts bit 15, and returns a boolean value.

The bit is extracted from the final 16-bit value after byte/word swapping based on the poller's endianness configuration.

Framers and transports
----------------------

- Serial (`--serial`, alias `--rtu`) supports framers `rtu` and `ascii` (e.g., `--serial ... --framer ascii`). Binary framer was removed in pymodbus 3.9+. If `--framer default` is used, pymodbus defaults to RTU framer.
- TCP/UDP (`--tcp`/`--udp`) use the `socket` framer; other framers are rejected. If `--framer default` is used, pymodbus defaults to socket framer.
