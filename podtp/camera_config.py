from enum import Enum
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
    
    def __init__(self, on: int = 1, frame_size: FrameSize = FrameSize.FRAMESIZE_VGA, \
                quality: int = 12, brightness: int = 3, contrast: int = 3, \
                saturation: int = 0, sharpness: int = 2) -> None:
        self.on = on
        self.frame_size = frame_size
        self.quality = quality
        self.brightness = brightness
        self.contrast = contrast
        self.saturation = saturation
        self.sharpness = sharpness

    def pack(self) -> bytes:
        return struct.pack('<BBbbbbb', self.on, self.frame_size.value, self.quality, self.brightness, self.contrast, self.saturation, self.sharpness)