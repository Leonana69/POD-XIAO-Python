import argparse
import json, time
from podtp import Podtp

def main():
    with open('config.json', 'r') as file:
        config = json.loads(file.read())

    parser = argparse.ArgumentParser(description='Upload firmware to STM32 via ESP32 over WiFi')
    parser.add_argument('-d', '--disable', help='Disable STM32', action='store_true')
    parser.add_argument('-r', '--reset', help='Reset STM32', action='store_true')
    args = parser.parse_args()
    
    podtp = Podtp(config)
    if podtp.connect():
        if args.reset:
            print('Resetting STM32')
            podtp.stm32_enable(False)
            time.sleep(0.5)
            podtp.stm32_enable(True)
        else:
            podtp.stm32_enable(not args.disable)
        podtp.disconnect()

if __name__ == '__main__':
    main()