"""
Minimal DJI protocol codec helpers (prototype).

This is a simplified, pure-Python implementation used by the prototype backend.
It does NOT implement the full DJI onboard SDK protocol; it's a placeholder
that structures messages so transports can send/receive them.
"""
from typing import Tuple
import binascii
import zlib
def build_command(cmd_name: str, payload: bytes = b"") -> bytes:
    """
    Build a simple framed command.
    Format: b'DJI|' + cmd_name.encode() + b'|' + payload + b'|H:<crc16>|T:<crc32>'
    """
    if isinstance(cmd_name, str):
        name = cmd_name.encode("ascii", errors="ignore")
    else:
        name = bytes(cmd_name)
    body = b"DJI|" + name + b"|" + (payload or b"")
    # compute CRCs
    head_crc = _crc16(body)
    tail_crc = _crc32(payload or b"")
    return body + b"|H:" + head_crc.to_bytes(2, "big") + b"|T:" + tail_crc.to_bytes(4, "big")


def parse_frame(frame: bytes) -> Tuple[str, bytes]:
    """
    Parse a simple framed message built by build_command.
    Returns (cmd_name, payload).
    """
    try:
        if not frame.startswith(b"DJI|"):
            return ("", frame)
        # split into header, name, rest
        parts = frame.split(b"|", 2)
        if len(parts) < 2:
            return ("", frame)
        name = parts[1].decode("ascii", errors="ignore")
        rest = parts[2] if len(parts) > 2 else b""
        # strip CRC suffixes if present
        # look for b'|H:' before tail
        hidx = rest.find(b"|H:")
        if hidx != -1:
            payload = rest[:hidx]
        else:
            payload = rest
        return (name, payload)
    except Exception:
        pass
    return ("", frame)


import binascii
import zlib
def _crc16(data: bytes) -> int:
    # CRC-16-CCITT (0xFFFF initial)
    try:
        return binascii.crc_hqx(data, 0xFFFF) & 0xFFFF
    except Exception:
        # fallback simple sum
        return sum(data) & 0xFFFF


def _crc32(data: bytes) -> int:
    try:
        return zlib.crc32(data) & 0xFFFFFFFF
    except Exception:
        return 0


