import json
from time import sleep
from podtp import Podtp
from podtp import PodtpType
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LogNorm
import numpy as np
import logging

logging.getLogger('matplotlib.font_manager').disabled = True
# Configuration for animation
fig, ax = plt.subplots(figsize=(8, 8))
cmap = plt.get_cmap('viridis')  # Get the colormap
data = np.zeros((8, 8))  # Initial data array
# im = ax.imshow(data, cmap=cmap, interpolation='nearest', vmin=0, vmax=3000)
im = ax.imshow(data, cmap=cmap, interpolation='nearest', norm=LogNorm(vmin=1, vmax=3000))
fig.colorbar(im)
ax.set_title("8x8 Grid Representation of Sensor Data")
ax.set_xlabel("Column Index")
ax.set_ylabel("Row Index")
ax.grid(False)  # Optionally enable grid

# Add text annotations for each cell
text_annotations = [[ax.text(j, i, f'{int(data[i, j])}', ha='center', va='center', color='white')
                     for j in range(data.shape[1])] for i in range(data.shape[0])]


def update_plot(data):
    """Update the plot with new data."""
    im.set_data(data)
    # Update text annotations with the new data
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            text_annotations[i][j].set_text(f'{int(data[i, j])}')
    return [im] + [text for row in text_annotations for text in row]


def data_gen(podtp: Podtp):
    """Generator function to yield data packets."""
    while True:
        data = podtp.sensor_data.depth.data
        for i in range(0, len(data)):
            for j in range(0, len(data[i])):
                if data[i][j] & 0x8000:
                    data[i][j] = 1

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