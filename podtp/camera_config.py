from enum import Enum
import numpy as np
import struct

class CameraConfig:
    class FrameSize(Enum):
        FRAMESIZE_QVGA = 5     # 320x240
        FRAMESIZE_CIF = 6      # 400x296
        FRAMESIZE_HVGA = 7     # 480x320
        FRAMESIZE_VGA = 8      # 640x480
        FRAMESIZE_SVGA = 9     # 800x600
        FRAMESIZE_XGA = 10     # 1024x768
        FRAMESIZE_HD = 11      # 1280x720

    K = np.array([[454.19405878,   0.,         617.24234876],
                  [  0.,         452.65234296, 299.6066995 ],
                  [  0.,           0.,           1.        ]])
    
    D = np.array([[ 0.47264424],
                  [ 0.96219725],
                  [-2.22589356],
                  [ 1.31717773]])
    
    def __init__(self, on: int = 1, frame_size: FrameSize = FrameSize.FRAMESIZE_HD, \
                quality: int = 7, brightness: int = 0, contrast: int = 4, \
                saturation: int = 2, sharpness: int = 4) -> None:
        self.on = on
        self.frame_size = frame_size
        self.quality = quality
        self.brightness = brightness
        self.contrast = contrast
        self.saturation = saturation
        self.sharpness = sharpness

    def pack(self) -> bytes:
        return struct.pack('<BBbbbbb', self.on, self.frame_size.value, self.quality, self.brightness, self.contrast, self.saturation, self.sharpness)