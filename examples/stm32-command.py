import json
from podtp import Podtp, print_t
import time

def takeoff(podtp: Podtp):
    print_t('Takeoff command...')
    podtp.takeoff()
    time.sleep(5)
    input('Press Enter to land...')
    podtp.land()

def hover_command(podtp: Podtp):
    print_t('Hovering command...')
    count = 0
    while count < 10:
        # print_t(f'Sending setpoint {count}')
        # podtp.send_command_hover(0, 0, 0, 0.5)
        # podtp.send_command_position(0, 0, 0.5, 0)
        podtp.send_command_setpoint(0, 0, 0, 12000)
        time.sleep(0.2)
        count += 1

def main():
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
    
    podtp = Podtp(config)
    if podtp.connect():
        if not podtp.send_ctrl_lock(False):
            print_t('Failed to unlock control')
            podtp.disconnect()
            return
        else:
            print_t('Drone unlocked')

        takeoff(podtp)
        # hover_command(podtp)

        podtp.disconnect()

if __name__ == '__main__':
    main()