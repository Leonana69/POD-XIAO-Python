import queue
import struct
import time
from typing import Optional
from threading import Thread, Lock
import numpy as np
from numpy.typing import NDArray
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
    filename="app.log",  # Log to a file
    filemode="w",  # Overwrite the file each time
)

from .podtp_packet import PODTP_MAX_DATA_LEN, PodtpPacket, PodtpType, PodtpPort
from .link import WifiLink
from .utils import print_t
from .podtp_parser import PodtpParser
from .camera_config import CameraConfig
from .sensor import Sensor
from .image_packet import ImagePacket, ImageParser

COMMAND_TIMEOUT_MS = 450

class Podtp:
    def __init__(self, config: dict):
        if 'ip_index' in config:
            config["ip"] = config["ip_list"][config["ip_index"]]
        self.data_link = WifiLink(config["ip"], config.get("port", 80))
        self.packet_parser = PodtpParser()
        self.packet_queue = {}
        self.last_packet_time_lock = Lock()
        self.last_packet_time = time.time()
        self.keep_alive = True
        for type in PodtpType:
            self.packet_queue[type.value] = queue.Queue()

        self.stream_link = WifiLink(config["ip"], config.get("stream_port", 81), True)
        self.image_parser = ImageParser()
        self.stream_on = False
        self.sensor_data = Sensor()

    def connect(self, timeout=5) -> bool:
        """
        Connect to the ESP32.
        """
        self.connected = self.data_link.connect(timeout)
        if self.connected:
            self.packet_thread = Thread(target=self._receive_packets_func)
            self.packet_thread.start()
            self.keep_alive_thread = Thread(target=self._keep_alive_func)
            self.keep_alive_thread.start()
        return self.connected

    def disconnect(self):
        print_t('Disconnecting...')
        self.stop_stream()
        self.connected = False
        self.keep_alive = False
        self.packet_thread.join()
        self.keep_alive_thread.join()
        self.data_link.disconnect()

    def start_stream(self):
        self._config_camera(CameraConfig())
        time.sleep(0.5) # wait for the esp32 to configure the camera and close the previous TCP link
        self._enable_stream()
        self.stream_on = self.stream_link.connect()
        if self.stream_on:
            self.stream_thread = Thread(target=self._stream_func)
            self.stream_thread.start()

    def _enable_stream(self, enable = True):
        packet = PodtpPacket().set_header(PodtpType.ESP32, PodtpPort.ESP32_ENABLE_STREAM)
        packet.length = 2
        packet.data[0] = 1 if enable else 0
        self._send_packet(packet)

    def _config_camera(self, config: CameraConfig):
        packet = PodtpPacket().set_header(PodtpType.ESP32, PodtpPort.ESP32_CONFIG_CAMERA)
        config_bytes = config.pack()
        packet.length = 1 + len(config_bytes)
        packet.data[:len(config_bytes)] = config_bytes
        self._send_packet(packet)

    def stop_stream(self):
        if not self.stream_on:
            return
        self.stream_on = False
        self.stream_thread.join()
        self._enable_stream(False)

    def _keep_alive_func(self):
        while self.connected:
            if self.keep_alive:
                send_packet = False
                with self.last_packet_time_lock:
                    if time.time() - self.last_packet_time > COMMAND_TIMEOUT_MS / 1000:
                        self.last_packet_time = time.time()
                        send_packet = True
                if send_packet:
                    packet = PodtpPacket().set_header(PodtpType.CTRL, PodtpPort.CTRL_KEEP_ALIVE)
                    self._send_packet(packet)
            time.sleep(0.05)

    def _receive_packets_func(self):
        while self.connected:
            self.packet_parser.process(self.data_link.receive(PODTP_MAX_DATA_LEN + 1))
            packet = self.packet_parser.get_packet()
            if packet is None:
                continue

            if packet.header.type == PodtpType.LOG:
                if packet.header.port == PodtpPort.LOG_STRING:
                    logging.debug(f'Log: {packet.data[:packet.length - 1].decode()}'.strip('\n'))
                    print_t(f'Log: {packet.data[:packet.length - 1].decode()}', end='')
                elif packet.header.port == PodtpPort.LOG_DISTANCE:
                    self.sensor_data.depth = struct.unpack('<I64h', packet.data.bytes(0, 132))
                elif packet.header.port == PodtpPort.LOG_STATE:
                    self.sensor_data.state = struct.unpack('<I6h', packet.data.bytes(0, 16))
                    # print_t(f'State: {self.sensor_data.state.timestamp}: {self.sensor_data.state.data}')
            else:
                self.packet_queue[packet.header.type].put(packet)

    def _stream_func(self):
        while self.stream_on:
            data = self.stream_link.receive(65535, 0.5)
            if data is None:
                continue
            _, image = self.image_parser.process(ImagePacket(data))
            if image is not None:
                self.sensor_data.frame = np.array(image)

    def _get_packet(self, type: PodtpType, timeout = 1) -> Optional[PodtpPacket]:
        try:
            return self.packet_queue[type.value].get(timeout = timeout)
        except queue.Empty:
            return None
    
    def _send_packet(self, packet: PodtpPacket, timeout = 2) -> bool:
        with self.last_packet_time_lock:
            self.last_packet_time = time.time()
        self.data_link.send(packet.pack())
        if packet.header.ack:
            packet = self._get_packet(PodtpType.ACK, timeout)
            if not packet or packet.header.port != PodtpPort.ACK_OK:
                return False
        return True
        
    def stm32_enable(self, enable: bool):
        packet = PodtpPacket().set_header(PodtpType.ESP32, PodtpPort.ESP32_ENABLE_STM32)
        packet.length = 2
        packet.data[0] = 1 if enable else 0
        self._send_packet(packet)

    def esp32_echo(self, message: str = 'Hello, ESP32!'):
        """
        Send a message to the ESP32 and wait for a response.
        """
        packet = PodtpPacket().set_header(PodtpType.ESP32, PodtpPort.ESP32_ECHO)
        packet.length = len(message) + 1
        packet.data[:len(message)] = message.encode()
        self._send_packet(packet)
        packet = self._get_packet(PodtpType.ESP32)
        if packet:
            print_t(f'Echo: {packet.data[:packet.length - 1].decode()}')
        else:
            print_t('No response')

    def command_takeoff(self) -> bool:
        """
        Send a takeoff command to the drone.
        """
        packet = PodtpPacket().set_header(PodtpType.COMMAND, PodtpPort.COMMAND_TAKEOFF)
        return self._send_packet(packet)
    
    def command_land(self) -> bool:
        """
        Send a land command to the drone.
        """
        packet = PodtpPacket().set_header(PodtpType.COMMAND, PodtpPort.COMMAND_LAND)
        return self._send_packet(packet)

    def ctrl_lock(self, lock: bool) -> bool:
        """
        Lock or unlock the drone.
        """
        packet = PodtpPacket().set_header(PodtpType.CTRL,
                                          PodtpPort.CTRL_LOCK,
                                          ack=True)
        packet.length = 2
        packet.data[0] = 1 if lock else 0
        return self._send_packet(packet)
    
    def ctrl_obstacle_avoidance(self, mode: int) -> bool:
        """
        Enable or disable obstacle avoidance.
        mode = 0: disable, 1: stop, 2: avoid
        """
        packet = PodtpPacket().set_header(PodtpType.CTRL,
                                          PodtpPort.CTRL_OBSTACLE_AVOIDANCE,
                                          ack=True)
        packet.length = 2
        packet.data[0] = mode
        return self._send_packet(packet)

    def command_setpoint(self, roll: float, pitch: float, yaw: float, thrust: float) -> bool:
        """
        Send a setpoint command to the drone. roll, pitch, yaw, thrust are in radians.
        """
        packet = PodtpPacket().set_header(PodtpType.COMMAND, PodtpPort.COMMAND_RPYT)
        size = struct.calcsize('<ffff')
        packet.data[:size] = struct.pack('<ffff', roll, pitch, yaw, thrust)
        packet.length = 1 + size
        return self._send_packet(packet)

    def command_hover(self, vx: float, vy: float, vyaw: float, height: float) -> bool:
        """
        Send a hover command to the drone. vx, vy are in m/s,  vyaw is in rad/s, height is in m.
        """
        packet = PodtpPacket().set_header(PodtpType.COMMAND, PodtpPort.COMMAND_HOVER)
        size = struct.calcsize('<ffff')
        packet.data[:size] = struct.pack('<ffff', vx, vy, vyaw, height)
        packet.length = 1 + size
        return self._send_packet(packet)
    
    def command_velocity(self, vx: float, vy: float, vyaw: float, vz: float) -> bool:
        """
        Send a velocity command to the drone. vx, vy are in m/s,  vyaw is in rad/s, vz is in m/s.
        """
        packet = PodtpPacket().set_header(PodtpType.COMMAND, PodtpPort.COMMAND_VELOCITY)
        size = struct.calcsize('<ffff')
        packet.data[:size] = struct.pack('<ffff', vx, vy, vyaw, vz)
        packet.length = 1 + size
        return self._send_packet(packet)
    
    def command_position(self, x: float, y: float, z: float, yaw: float) -> bool:
        """
        Send a delta position command to the drone. x, y, z are in m, yaw is in degrees.
        """
        packet = PodtpPacket().set_header(PodtpType.COMMAND, PodtpPort.COMMAND_POSITION)
        size = struct.calcsize('<ffff')
        packet.data[:size] = struct.pack('<ffff', x, y, z, yaw)
        packet.length = 1 + size
        return self._send_packet(packet)
    
    def reset_estimator(self, starting_height=0) -> bool:
        """
        Reset the estimator with the given starting height (cm).
        """
        packet = PodtpPacket().set_header(PodtpType.CTRL, PodtpPort.CTRL_RESET_ESTIMATOR, ack=True)
        packet.length = 2
        assert starting_height < 100 and starting_height >= 0, "Height must be between 0 and 100 (cm)"
        packet.data[0] = starting_height
        return self._send_packet(packet)