"""CLI runner for the bridge with configuration support."""
import argparse
import time
from .adapter import Bridge
from .backend import MockBackend, PureDJIBackend
from .transport import UDPTransport, SerialTransport
from .config import Config
from .backend import DJIOnboardBackend


def main():
    p = argparse.ArgumentParser(prog="py_mavlink_dji")
    p.add_argument("--config", help="Path to TOML config file", default=None)
    p.add_argument("--uri", help="MAVLink source URI (pymavlink style)", default=None)
    p.add_argument("--mock", help="Use mock backend", action="store_true")
    p.add_argument("--transport", choices=["udp", "serial"], default=None, help="DJI backend transport")
    p.add_argument("--udp-host", help="UDP backend host", default=None)
    p.add_argument("--udp-port", type=int, help="UDP backend port", default=None)
    p.add_argument("--serial-device", help="Serial device for backend", default=None)
    p.add_argument("--serial-baud", type=int, help="Serial baud", default=None)
    p.add_argument("--log-level", choices=["debug", "info", "warning", "error"], default=None)
    p.add_argument("--app-id", type=int, help="DJI app_id for activation", default=None)
    p.add_argument("--app-key", help="DJI app_key for activation", default=None)
    p.add_argument("--api-level", type=int, help="DJI api_level", default=None)
    args = p.parse_args()

    cfg = Config.load(args.config)
    # override from CLI args if provided
    if args.uri:
        cfg.uri = args.uri
    if args.mock:
        cfg.mock_backend = True
    if args.transport:
        cfg.backend_transport = args.transport
    if args.udp_host:
        cfg.udp_host = args.udp_host
    if args.udp_port:
        cfg.udp_port = args.udp_port
    if args.serial_device:
        cfg.serial_device = args.serial_device
    if args.serial_baud:
        cfg.serial_baud = args.serial_baud
    if args.log_level:
        cfg.log_level = args.log_level
    if args.app_id is not None:
        cfg.app_id = args.app_id
    if args.app_key is not None:
        cfg.app_key = args.app_key
    if args.api_level is not None:
        cfg.api_level = args.api_level

    # choose backend
    if cfg.mock_backend:
        backend = MockBackend()
    else:
        # Prefer a real DJIOnboardBackend implementation if available.
        try:
            # DJIOnboardBackend will raise if the native SDK/bindings are not present.
            backend = DJIOnboardBackend()
        except Exception:
            # Fallback to the prototype PureDJIBackend using transport+codec
            if cfg.backend_transport == "serial":
                tr = SerialTransport(cfg.serial_device, cfg.serial_baud)
            else:
                tr = UDPTransport(cfg.udp_host, cfg.udp_port)
            backend = PureDJIBackend(tr, __import__("py_mavlink_dji.codec", fromlist=["codec"]))

    bridge = Bridge(source_uri=cfg.uri, backend=backend)
    try:
        bridge.activate_backend(app_id=cfg.app_id, app_key=cfg.app_key, api_level=cfg.api_level)
    except Exception:
        pass
    print("Starting bridge, listening on", cfg.uri, "mock_backend=", cfg.mock_backend)
    bridge.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        bridge.stop()
        if hasattr(backend, "stop"):
            backend.stop()
        print("Stopped")


if __name__ == "__main__":
    main()

