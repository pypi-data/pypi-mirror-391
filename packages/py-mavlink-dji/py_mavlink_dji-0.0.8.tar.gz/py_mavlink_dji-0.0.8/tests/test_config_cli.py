import os, sys, tempfile
here = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(here, "..", "src")))

from py_mavlink_dji.config import Config


def test_config_load_toml_and_overrides(tmp_path):
    cfg_file = tmp_path / "testcfg.toml"
    cfg_file.write_text('''uri = "udp:0.0.0.0:15000"
mock_backend = false
backend_transport = "udp"
udp_host = "1.2.3.4"
udp_port = 15010
app_id = 12345
app_key = "abc123"
api_level = 3
''')
    cfg = Config.load(str(cfg_file))
    assert cfg.uri == "udp:0.0.0.0:15000"
    assert cfg.mock_backend is False
    assert cfg.backend_transport == "udp"
    assert cfg.udp_host == "1.2.3.4"
    assert cfg.udp_port == 15010
    assert cfg.app_id == 12345
    assert cfg.app_key == "abc123"
    assert cfg.api_level == 3


