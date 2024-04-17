import numpy as np
from threading import Lock
from PIL import Image

class Sensor:
    class State:
        def __init__(self) -> None:
            self.data = np.zeros(6, dtype=np.int16)
            self.timestamp = 0

    class Depth:
        def __init__(self) -> None:
            self.data = np.zeros((8, 8), dtype=np.int16)
            self.timestamp = 0

    def __init__(self) -> None:
        self._depth = Sensor.Depth()
        self.lock_depth = Lock()
        self._frame = np.array(Image.new('RGB', (320, 240)))
        self.lock_frame = Lock()
        self._state = Sensor.State()
        self.lock_state = Lock()

    @property
    def depth(self):
        with self.lock_depth:
            return self._depth
        
    @depth.setter
    def depth(self, value):
        with self.lock_depth:
            self._depth.timestamp = value[0]
            self._depth.data = np.array(value[1:], dtype=np.int16).reshape((8, 8))

    @property
    def frame(self):
        with self.lock_frame:
            return self._frame
        
    @frame.setter
    def frame(self, value):
        with self.lock_frame:
            self._frame = value

    @property
    def state(self):
        with self.lock_state:
            return self._state
    
    @state.setter
    def state(self, value):
        with self.lock_state:
            self._state.timestamp = value[0]
            self._state.data = np.array(value[1:], dtype=np.int16)