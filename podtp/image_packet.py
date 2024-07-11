from PIL import Image
import io

IMAGE_PACKET_SIZE = 1024
IMAGE_HEADER_SIZE = 8
IMAGE_PAYLOAD_SIZE = IMAGE_PACKET_SIZE - IMAGE_HEADER_SIZE

class ImagePacket:
    class Header:
        def __init__(self, buffer: bytearray) -> None:
            self.buffer = buffer

        @property
        def seq(self):
            return self.buffer[0] | (self.buffer[1] << 8)
        
        @seq.setter
        def seq(self, val: int):
            self.buffer[0] = val & 0xFF
            self.buffer[1] = (val >> 8) & 0xFF
        
        @property
        def index(self):
            return self.buffer[2] | (self.buffer[3] << 8)
        
        @index.setter
        def index(self, val: int):
            self.buffer[2] = val & 0xFF
            self.buffer[3] = (val >> 8) & 0xFF

        @property
        def total(self):
            return self.buffer[4] | (self.buffer[5] << 8)
        
        @total.setter
        def total(self, val: int):
            self.buffer[4] = val & 0xFF
            self.buffer[5] = (val >> 8) & 0xFF

        @property
        def size(self):
            return self.buffer[6] | (self.buffer[7] << 8)
        
        @size.setter
        def size(self, val: int):
            self.buffer[6] = val & 0xFF
            self.buffer[7] = (val >> 8) & 0xFF

    class Data:
        def __init__(self, buffer: bytearray) -> None:
            self.buffer = buffer

        def __getitem__(self, key):
            if isinstance(key, slice):
                start = key.start + IMAGE_HEADER_SIZE if key.start is not None else IMAGE_HEADER_SIZE
                stop = key.stop + IMAGE_HEADER_SIZE if key.stop is not None else len(self.buffer)
                return self.buffer[start:stop]
            else:
                return self.buffer[key + IMAGE_HEADER_SIZE]
        
        def __setitem__(self, key, value):
            if isinstance(key, slice):
                start = key.start + IMAGE_HEADER_SIZE if key.start is not None else IMAGE_HEADER_SIZE
                stop = key.stop + IMAGE_HEADER_SIZE if key.stop is not None else len(self.buffer)
                self.buffer[start:stop] = value
            else:
                self.buffer[key + IMAGE_HEADER_SIZE] = value

        def bytes(self, start: int, stop: int):
            return self.buffer[start + IMAGE_HEADER_SIZE:stop + IMAGE_HEADER_SIZE]
    
    def __init__(self, buffer: bytes):
        self.buffer = bytearray(buffer)
        self.header = ImagePacket.Header(self.buffer)
        self.data = ImagePacket.Data(self.buffer)

    def __repr__(self):
        return f"ImagePacket(seq={self.header.seq}, index={self.header.index}, total={self.header.total}, size={self.header.size})"
    
class ImageParser:
    def __init__(self):
        self.image_packets = {}
        self.image = None

    def process(self, packet: ImagePacket) -> tuple[int, Image.Image | None]:
        seq = packet.header.seq
        index = packet.header.index
        total = packet.header.total
        size = packet.header.size
        data = packet.data

        if seq not in self.image_packets:
            self.image_packets[seq] = [None] * total
        
        self.image_packets[seq][index] = data.bytes(0, size)

        if None not in self.image_packets[seq]:
            self.image = b''.join(self.image_packets[seq])
            del self.image_packets[seq]
            return seq, Image.open(io.BytesIO(self.image))

        return seq, None