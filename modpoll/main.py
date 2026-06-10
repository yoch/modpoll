import json
import logging
import re
import signal
import sys

from .arg_parser import get_parser
from .mqtt_task import MqttHandler
from .modbus_task import setup_modbus_handlers, modbus_connect, modbus_close

from . import __version__
from .utils import set_threading_event, delay_thread, on_threading_event, get_utc_time


LOG_SIMPLE = "%(asctime)s | %(levelname).1s | %(name)s | %(message)s"
logger = None


def _signal_handler(signal, frame):
    logger.info(f"Exiting {sys.argv[0]}")
    set_threading_event()


def extract_device_from_mqtt_topic(pattern: str, topic: str):
    """Return device name from the first '+' wildcard segment, or None if no match."""
    parts = pattern.split("+")
    if len(parts) < 2:
        raise ValueError("MQTT subscribe pattern must contain '+' wildcard")
    topic_regex = "([^/\n]*)".join(re.escape(p) for p in parts)
    match = re.fullmatch(topic_regex, topic)
    return match.group(1) if match else None


def setup_logging(level, format):
    logging.basicConfig(level=level, format=format)


def app(name="modpoll"):
    mqtt_handler = None
    modbus_client = None
    modbus_handlers = []

    print(
        f"\nModpoll v{__version__} - A New Command-line Tool for Modbus and MQTT\n",
        flush=True,
    )

    # parse args
    args = get_parser().parse_args()

    # get logger
    setup_logging(args.loglevel, LOG_SIMPLE)
    global logger
    logger = logging.getLogger(__name__)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # setup mqtt
    if not args.mqtt_host:
        logger.info("No MQTT host specified, skip MQTT setup.")
    else:
        logger.info(f"Setup MQTT connection to {args.mqtt_host}:{args.mqtt_port}")
        try:
            if "+" not in args.mqtt_subscribe_topic_pattern:
                logger.error(
                    "MQTT subscribe pattern must contain '+' wildcard, not "
                    "'{{device_name}}': "
                    f"{args.mqtt_subscribe_topic_pattern}"
                )
                exit(1)
            if args.mqtt_rx_queue_size < 1:
                logger.error(
                    f"MQTT rx queue size must be at least 1: {args.mqtt_rx_queue_size}"
                )
                exit(1)
            mqtt_handler = MqttHandler(
                "MqttHandler",
                args.mqtt_host,
                args.mqtt_port,
                args.mqtt_user,
                args.mqtt_pass,
                args.mqtt_clientid,
                args.mqtt_qos,
                subscribe_topics=[args.mqtt_subscribe_topic_pattern],
                use_tls=args.mqtt_use_tls,
                tls_version=args.mqtt_tls_version,
                cacerts=args.mqtt_cacerts,
                insecure=args.mqtt_insecure,
                mqtt_version=args.mqtt_version,
                log_level=args.loglevel,
                rx_queue_size=args.mqtt_rx_queue_size,
            )
            if mqtt_handler.setup() and mqtt_handler.connect():
                logger.info("Connected to MQTT broker.")
            else:
                logger.error("Failed to connect with MQTT broker, exiting...")
                try:
                    mqtt_handler.close()
                except Exception as close_err:
                    logger.debug(
                        f"Ignoring MQTT close error after failed connect: {close_err}"
                    )
                exit(1)
        except Exception as e:
            logger.error(f"Error setting up MQTT input: {e}, exiting...")
            if mqtt_handler:
                try:
                    mqtt_handler.close()
                except Exception as close_err:
                    logger.debug(
                        f"Ignoring MQTT close error after setup exception: {close_err}"
                    )
            exit(1)

    # setup modbus tasks
    modbus_client, modbus_handlers = setup_modbus_handlers(args, mqtt_handler)
    if modbus_handlers:
        logger.info(f"Loaded {len(modbus_handlers)} Modbus config(s).")
        delay_thread(args.delay)
    else:
        logger.error("No Modbus config(s) defined. Exiting...")
        if mqtt_handler:
            mqtt_handler.close()
        exit(1)

    # main loop
    last_check = 0
    last_diag = 0
    while not on_threading_event():
        now = get_utc_time()
        # routine check
        if now > last_check + args.rate:
            if last_check == 0:
                elapsed = args.rate
            else:
                elapsed = round(now - last_check, 6)
            logger.info(
                f" === Modpoll is polling at rate:{args.rate}s, actual:{elapsed}s ==="
            )
            if not modbus_connect(modbus_client):
                for modbus_handler in modbus_handlers:
                    modbus_handler.on_connect_failure()
            else:
                try:
                    for modbus_handler in modbus_handlers:
                        modbus_handler.poll()
                        if on_threading_event():
                            break
                finally:
                    modbus_close(modbus_client)
            for modbus_handler in modbus_handlers:
                if on_threading_event():
                    break
                if args.mqtt_host:
                    if args.timestamp:
                        modbus_handler.publish_data(timestamp=now)
                    else:
                        modbus_handler.publish_data()
                if args.export:
                    if args.timestamp:
                        modbus_handler.export(args.export, timestamp=now)
                    else:
                        modbus_handler.export(args.export)
            last_check = get_utc_time()
        if args.diagnostics_rate > 0 and now > last_diag + args.diagnostics_rate:
            last_diag = now
            for modbus_handler in modbus_handlers:
                modbus_handler.publish_diagnostics()
        if on_threading_event():
            break
        # Check if receive mqtt request
        if mqtt_handler:
            topic, payload = mqtt_handler.receive()
            if topic and payload:
                try:
                    device_name = extract_device_from_mqtt_topic(
                        args.mqtt_subscribe_topic_pattern, topic
                    )
                except ValueError:
                    logger.error(
                        "MQTT subscribe pattern must contain '+' wildcard: "
                        f"{args.mqtt_subscribe_topic_pattern}"
                    )
                    continue
                if device_name:
                    logger.info(
                        f"Received request to write data for device {device_name}"
                    )
                    try:
                        reg = json.loads(payload)
                        object_type = reg["object_type"]
                        address = reg["address"]
                        value = reg["value"]

                        device_found = False
                        for modbus_handler in modbus_handlers:
                            if device_name in [
                                dev.name for dev in modbus_handler.get_device_list()
                            ]:
                                device_found = True
                                write_success = False
                                if modbus_connect(modbus_client):
                                    try:
                                        if object_type == "coil":
                                            write_success = modbus_handler.write_coil(
                                                device_name, address, value
                                            )
                                        elif object_type == "holding_register":
                                            write_success = (
                                                modbus_handler.write_register(
                                                    device_name, address, value
                                                )
                                            )
                                    finally:
                                        modbus_close(modbus_client)

                                if write_success:
                                    logger.info(
                                        f"Successfully wrote {object_type}: device={device_name}, address={address}, value={value}"
                                    )
                                else:
                                    logger.warning(
                                        f"Failed to write {object_type}: device={device_name}, address={address}, value={value}"
                                    )
                                break

                        if not device_found:
                            logger.error(f"No device found with name: {device_name}")

                    except KeyError as e:
                        logger.error(f"Missing required key in payload: {e}")
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON message: {payload}")
                else:
                    logger.error(f"Failed to extract device name from topic: {topic}")
        if args.once:
            set_threading_event()
            break

        remaining = last_check + args.rate - get_utc_time()
        delay_thread(min(max(remaining, 0.01), 0.5))

    modbus_close(modbus_client)
    if mqtt_handler:
        mqtt_handler.close()


if __name__ == "__main__":
    app()
