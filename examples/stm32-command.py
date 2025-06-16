import json
from podtp import Podtp, print_t
import time

def takeoff(podtp: Podtp):
    print_t('Takeoff command...')
    podtp.command_takeoff()
    input('Press Enter to land...')
    podtp.command_land()

def hover_command(podtp: Podtp):
    print_t('Hovering command...')
    podtp.reset_estimator(0)
    podtp.ctrl_obstacle_avoidance(1)
    count = 0
    while count < 12:
        # print_t(f'Sending setpoint {count}')
        podtp.command_hover(0, 0, 0, 0.5)
        # podtp.command_position(0, 0, 0.5, 0)
        # podtp.command_setpoint(0, 0, 0, 17000)
        time.sleep(0.2)
        count += 1
    # podtp.command_position(0.4, 0, 0, 0)
    input('Press Enter to rotate')
    # podtp.command_position(0, 0, 0, 90)
    count = 0
    while count < 10:
        podtp.command_hover(0.3, 0, 0, 0.5)
        time.sleep(0.2)
        count += 1
    podtp.command_hover(0, 0, 0, 0.5)
    # input('Press Enter to rotate')
    # podtp.command_position(1.5, 0, 0, 0)


    # time.sleep(0.2)
    # podtp.command_position(-0.4, 0, 0, 0)
    
    input('Press Enter to land...')
    podtp.command_land()

def main():
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
    
    podtp = Podtp(config)
    if podtp.connect():
        if not podtp.ctrl_lock(False):
            print_t('Failed to unlock control')
            podtp.disconnect()
            return
        else:
            print_t('Drone unlocked')
        
        # takeoff(podtp)
        hover_command(podtp)

        podtp.disconnect()

if __name__ == '__main__':
    main()