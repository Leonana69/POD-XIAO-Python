import json
from time import sleep
from podtp import Podtp
from podtp import PodtpType
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import struct
import numpy as np

# Configuration for animation
fig, ax = plt.subplots(figsize=(8, 8))
cmap = plt.get_cmap('viridis')  # Get the colormap
data = np.zeros((8, 8))  # Initial data array
im = ax.imshow(data, cmap=cmap, interpolation='nearest', vmin=0, vmax=3000)
fig.colorbar(im)
ax.set_title("8x8 Grid Representation of Sensor Data")
ax.set_xlabel("Column Index")
ax.set_ylabel("Row Index")
ax.grid(False)  # Optionally enable grid

def update_plot(data):
    """Update the plot with new data."""
    grid_data = data.reshape(8, 8)
    print(grid_data)
    im.set_data(grid_data)
    return [im]

def data_gen(podtp):
    """Generator function to yield data packets."""
    while True:
        packet = podtp.get_packet(PodtpType.LOG)
        if packet:
            data = np.array(struct.unpack('<64h', packet.data.bytes(0, 128)))
            for i in range(0, len(data)):
                if data[i] & 0x8000:
                    data[i] = 0
            yield data
        else:
            break  # Stop the generator if no packet is received

def main():
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
    
    podtp = Podtp(config)
    if podtp.connect():
        ani = FuncAnimation(fig, update_plot, frames=lambda: data_gen(podtp), repeat=False)
        plt.show()
        podtp.disconnect()

if __name__ == '__main__':
    main()