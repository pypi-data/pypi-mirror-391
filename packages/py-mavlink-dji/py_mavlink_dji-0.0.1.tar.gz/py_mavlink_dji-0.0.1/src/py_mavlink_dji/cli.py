"""Minimal CLI runner for the bridge."""
import argparse
from .adapter import Bridge
from .backend import MockBackend

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--uri", default="udp:0.0.0.0:14550", help="MAVLink source URI (pymavlink style)")
    args = p.parse_args()

    backend = MockBackend()
    bridge = Bridge(source_uri=args.uri, backend=backend)
    print("Starting bridge, listening on", args.uri)
    bridge.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        bridge.stop()
        print("Stopped")

if __name__ == "__main__":
    main()


