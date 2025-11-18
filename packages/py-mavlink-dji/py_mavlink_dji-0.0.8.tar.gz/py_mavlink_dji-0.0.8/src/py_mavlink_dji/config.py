"""Configuration loader for py_mavlink_dji.
Supports TOML config files (if tomllib available) and command-line overrides.
"""
from dataclasses import dataclass
from typing import Optional
import os

try:
    import tomllib  # Python 3.11+
except Exception:
    tomllib = None


@dataclass
class Config:
    # MAVLink source
    uri: str = "udp:0.0.0.0:14550"
    # Transport for DJI backend: "udp" or "serial"
    backend_transport: str = "udp"
    udp_host: str = "127.0.0.1"
    udp_port: int = 14551
    serial_device: str = "/dev/ttyACM0"
    serial_baud: int = 230400
    # DJI activation / app settings (optional)
    app_id: Optional[int] = None
    app_key: Optional[str] = None
    api_level: Optional[int] = None
    # runtime flags
    mock_backend: bool = False
    log_level: str = "info"

    @classmethod
    def load(cls, path: Optional[str] = None):
        cfg = cls()
        data = {}
        if path and os.path.exists(path):
            if tomllib is not None:
                try:
                    with open(path, "rb") as fh:
                        data = tomllib.load(fh)
                except Exception:
                    data = {}
            else:
                data = cls._load_simple_toml(path)
        for k, v in data.items():
            if hasattr(cfg, k):
                try:
                    setattr(cfg, k, v)
                except Exception:
                    pass
        return cfg

    @staticmethod
    def _load_simple_toml(path: str):
        """Fallback parser for environments without tomllib."""
        data = {}
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if v.startswith('"') and v.endswith('"'):
                        v = v[1:-1]
                    elif v.lower() in ("true", "false"):
                        v = v.lower() == "true"
                    else:
                        try:
                            if "." in v:
                                v = float(v)
                            else:
                                v = int(v)
                        except Exception:
                            pass
                    data[k] = v
        except Exception:
            return {}
        return data


