import os
import socket
import uuid

import pytest

INTEGRATION_MQTT_HOST = os.environ.get("MQTT_TEST_HOST", "broker.emqx.io")
INTEGRATION_MQTT_PORT = int(os.environ.get("MQTT_TEST_PORT", "1883"))


def _mqtt_broker_reachable(host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@pytest.fixture(scope="session")
def mqtt_broker():
    """Public broker used by MQTT integration tests (override via MQTT_TEST_HOST/PORT)."""
    if not _mqtt_broker_reachable(INTEGRATION_MQTT_HOST, INTEGRATION_MQTT_PORT):
        pytest.skip(
            f"MQTT broker unavailable at {INTEGRATION_MQTT_HOST}:{INTEGRATION_MQTT_PORT}"
        )
    return INTEGRATION_MQTT_HOST, INTEGRATION_MQTT_PORT


@pytest.fixture
def unique_mqtt_client_id():
    return f"modpoll-test-{uuid.uuid4().hex[:16]}"


@pytest.fixture
def unique_mqtt_topic():
    return f"modpoll/integration/{uuid.uuid4().hex}"
