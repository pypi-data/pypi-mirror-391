import os, sys
# ensure src package path
here = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(here, "..", "src")))
from py_mavlink_dji import codec


def test_crc_and_parse_roundtrip():
    frame = codec.build_command("TESTCMD", b"PAYLOAD")
    name, payload = codec.parse_frame(frame)
    assert name == "TESTCMD"
    assert payload == b"PAYLOAD"
    # ensure CRC fields present as suffix
    assert b"|H:" in frame and b"|T:" in frame


