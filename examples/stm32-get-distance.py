import json
from time import sleep
from podtp import Podtp
from podtp import PodtpType
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import logging

logging.getLogger('matplotlib.font_manager').disabled = True
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
    # print(data)
    im.set_data(data)
    return [im]

def data_gen(podtp: Podtp):
    """Generator function to yield data packets."""
    while True:
        data = podtp.sensor_data.depth.data
        for i in range(0, len(data)):
            for j in range(0, len(data[i])):
                if data[i][j] & 0x8000:
                    data[i][j] = 0

        yield data
        sleep(0.1)

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