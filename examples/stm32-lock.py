import json
from podtp import Podtp, print_t
import time

def main():
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
    
    podtp = Podtp(config)
    if podtp.connect():
        podtp.send_ctrl_lock(True)
        podtp.disconnect()


if __name__ == '__main__':
    main()