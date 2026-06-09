from unittest.mock import MagicMock

from modpoll.modbus_task import (
    Device,
    ModbusHandler,
    Poller,
    modbus_connect,
    modbus_close,
)


def _handler_with_empty_poll(client):
    handler = ModbusHandler(client, "dummy.csv", daemon=True)
    device = Device("dev", 1)
    device.pollerList = []
    handler.deviceList = [device]
    return handler


def test_shared_client_single_connect_and_close_per_cycle():
    client = MagicMock()
    client.connect.return_value = True

    h1 = _handler_with_empty_poll(client)
    h2 = _handler_with_empty_poll(client)

    assert modbus_connect(client)
    try:
        h1.poll()
        h2.poll()
    finally:
        modbus_close(client)

    assert client.connect.call_count == 1
    assert client.close.call_count == 1


def test_on_connect_failure_clears_poll_success():
    client = MagicMock()
    handler = _handler_with_empty_poll(client)
    handler.deviceList[0].pollSuccess = True

    handler.on_connect_failure()

    assert handler.deviceList[0].pollSuccess is False


def test_on_connect_failure_autoremove_after_three_cycles():
    client = MagicMock()
    device = Device("dev", 1)
    poller = Poller(device, 3, 0, 1, "BE_BE")
    device.pollerList = [poller]

    handler = ModbusHandler(client, "dummy.csv", autoremove=True, daemon=True)
    handler.deviceList = [device]

    for _ in range(3):
        handler.on_connect_failure()

    assert poller.disabled is True
