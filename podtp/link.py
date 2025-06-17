import socket
import select
from enum import Enum
from typing import Optional
from .utils import print_t

LINK_MAX_WAIT_TIME = 5000

class WifiLink:
    def __init__(self, server_ip: str, server_port: int, use_udp = False):
        self.server_ip = server_ip
        self.server_port = server_port
        if server_ip == '255.255.255.255' or server_ip == '0.0.0.0':
            self.use_udp = True
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        elif use_udp:
            self.use_udp = True
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.use_udp = False
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.client_socket.settimeout(LINK_MAX_WAIT_TIME / 1000)
        self.client_connected = False

    def connect(self, timeout=5) -> bool:
        try:
            if self.use_udp:
                self.client_socket.bind(('', self.server_port))
            else:
                self.client_socket.settimeout(timeout)
                self.client_socket.connect((self.server_ip, self.server_port))
            self.client_connected = True
            print_t(f'Connected to {self.server_ip}:{self.server_port}')
            return True
        except:
            print_t(f'Failed to connect to {self.server_ip}:{self.server_port}')
            return False

    def disconnect(self):
        if not self.use_udp:
            self.client_socket.close()
        self.client_connected = False
        print_t(f'Disconnected from {self.server_ip}:{self.server_port}')

    def send(self, data: bytearray) -> bool:
        if not self.client_connected:
            print_t(f'Failed to send packet: Not connected to {self.server_ip}:{self.server_port}')
            return False
        self.client_socket.send(data)
        return True

    def receive(self, length=4096, timeout=0.001) -> Optional[bytes]:
        """
        Read from the TCP/UDP connection until data is received or a timeout occurs.
        :param length: The maximum number of bytes to read.
        :param timeout: The number of seconds to wait for data.
        :return: The received data as bytes, or None if no data is received.
        """
        if not self.client_connected:
            print_t(f'Failed to receive packet: Not connected to {self.server_ip}:{self.server_port}')
            return None

        try:
            readable, _, _ = select.select([self.client_socket], [], [], timeout)
            if not readable:
                return None

            if self.use_udp:
                data, addr = self.client_socket.recvfrom(length)
                # Optionally validate the source address
                # if addr[0] != self.server_ip or addr[1] != self.server_port:
                #     print_t(f"Received packet from unexpected source: {addr}")
                #     return None
            else:
                data = self.client_socket.recv(length)

            if not data:
                print_t("Connection closed by the server.")
                self.disconnect()  # Ensure the connection is marked as closed
                return None

            return data

        except (socket.timeout, ConnectionResetError, OSError) as e:
            print_t(f"Error receiving data: {e}")
            self.disconnect()  # Handle connection errors gracefully
            return None