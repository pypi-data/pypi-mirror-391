"""
Transport implementations for the backend.
Provides SerialTransport (pyserial) and UDPTransport (socket).
"""
import threading
import socket
import time
from typing import Optional, Callable


class UDPTransport:
    def __init__(self, remote_host: str, remote_port: int, bind_host: str = "0.0.0.0", bind_port: int = 0):
        self.remote = (remote_host, int(remote_port))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((bind_host, int(bind_port)))
        self._recv_thread: Optional[threading.Thread] = None
        self._running = False
        self.on_recv: Optional[Callable[[bytes], None]] = None

    def send(self, data: bytes):
        self.sock.sendto(data, self.remote)

    def start_recv(self):
        if self._running:
            return
        self._running = True
        self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def stop_recv(self):
        self._running = False
        if self._recv_thread:
            self._recv_thread.join(timeout=1.0)

    def _recv_loop(self):
        while self._running:
            try:
                data, addr = self.sock.recvfrom(4096)
                if self.on_recv:
                    self.on_recv(data)
            except Exception:
                time.sleep(0.01)


class SerialTransport:
    def __init__(self, device: str, baudrate: int = 230400, timeout: float = 0.1):
        try:
            import serial
        except Exception:
            serial = None

        if serial is None:
            raise RuntimeError("pyserial is required for SerialTransport")
        self._ser = serial.Serial(device, baudrate, timeout=timeout)
        self._recv_thread: Optional[threading.Thread] = None
        self._running = False
        self.on_recv: Optional[Callable[[bytes], None]] = None

    def send(self, data: bytes):
        self._ser.write(data)

    def start_recv(self):
        if self._running:
            return
        self._running = True
        self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def stop_recv(self):
        self._running = False
        if self._recv_thread:
            self._recv_thread.join(timeout=1.0)

    def _recv_loop(self):
        while self._running:
            try:
                data = self._ser.read(4096)
                if data and self.on_recv:
                    self.on_recv(data)
            except Exception:
                time.sleep(0.01)


