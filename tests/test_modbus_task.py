import os
import socket

import pytest  # type: ignore
from modpoll.arg_parser import get_parser
from modpoll.modbus_task import setup_modbus_handlers, modbus_connect, modbus_close

MODBUS_TEST_HOST = os.environ.get("MODBUS_TEST_HOST", "127.0.0.1")
MODBUS_TEST_PORT = int(os.environ.get("MODBUS_TEST_PORT", "502"))


def _modbus_reachable(host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@pytest.fixture(scope="module")
def modbus_test_host():
    if not _modbus_reachable(MODBUS_TEST_HOST, MODBUS_TEST_PORT):
        pytest.skip(
            f"Modbus TCP unavailable at {MODBUS_TEST_HOST}:{MODBUS_TEST_PORT} "
            "(set MODBUS_TEST_HOST / MODBUS_TEST_PORT)"
        )
    return MODBUS_TEST_HOST


@pytest.mark.integration
def test_modbus_task_modbus_setup(modbus_test_host):
    parser = get_parser()
    args = parser.parse_args(
        [
            "--config",
            "examples/modsim.csv",
            "examples/modsim2.csv",
            "--tcp",
            modbus_test_host,
        ]
    )
    _modbus_client, modbus_handlers = setup_modbus_handlers(args)
    assert len(modbus_handlers) == 2


@pytest.mark.integration
def test_modbus_task_poll_modsim(modbus_test_host):
    parser = get_parser()
    args = parser.parse_args(
        [
            "--config",
            "examples/modsim.csv",
            "--tcp",
            modbus_test_host,
        ]
    )
    modbus_client, modbus_handlers = setup_modbus_handlers(args)
    modbus_handler = modbus_handlers[0]

    assert modbus_connect(modbus_client)

    try:
        modbus_handler.poll()
    finally:
        modbus_close(modbus_client)

    assert len(modbus_handler.deviceList) > 0
    assert len(modbus_handler.deviceList[0].references) > 0
    assert any(
        ref.val is not None for ref in modbus_handler.deviceList[0].references.values()
    )
