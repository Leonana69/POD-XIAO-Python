import json
from podtp import Podtp
import argparse

def main(lock: bool):
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
    
    podtp = Podtp(config)
    if podtp.connect():
        if podtp.send_ctrl_lock(lock):
            print(('Lock' if lock else 'Unlock') + ' [OK]')
        podtp.disconnect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lock or unlock the drone control.')
    parser.add_argument('--unlock', action='store_false', help='Unlock the drone control')
    args = parser.parse_args()
    main(args.unlock)