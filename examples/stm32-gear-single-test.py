import json
from podtp import Podtp, print_t
import time

def wait(podtp, t):
    count = 0
    while count < t:
        print_t(f'Setpoint {count}, state: {podtp.sensor_data.state.data}')
        time.sleep(0.1)
        count += 1

def main():
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
    
    podtp = Podtp(config)
    if podtp.connect():
        if not podtp.send_ctrl_lock(False):
            print_t('Failed to unlock control')
        else:
            print_t('Drone unlocked')
            podtp.reset_estimator()
            
            podtp.send_command_hover(0.4, 0, 0, 0)
            time.sleep(4)

            # for _ in range(40):
            #     podtp.send_command_hover(0.4, 0, 0, 0)
            #     time.sleep(0.1)
            

            # for _ in range(30):
            #     podtp.send_command_hover(0.3, 0.2, 0, 0)
            #     # podtp.send_command_setpoint(0, 0, 0, 1000)
            #     time.sleep(0.1)
            
            # for _ in range(30):
            #     podtp.send_command_hover(0.8, 0, 0, 0)
            #     # podtp.send_command_setpoint(0, 0, 0, 1000)
            #     time.sleep(0.1)
            

            for _ in range(15):
                # podtp.send_command_hover(0.3, 0, 0, 0)
                podtp.send_command_setpoint(0, 0, 0, 11000)
                time.sleep(0.1)
            
            # podtp.send_command_position(0, 0.1, 0, 0)
            # wait(podtp, 20)
            # podtp.send_command_position(-0.2, 0, 0, 0)
            # wait(podtp, 20)
            # podtp.send_command_position(-0, 0, 0, 0)
            # wait(podtp, 20)
            podtp.send_command_setpoint(0, 0, 0, 0)
            time.sleep(2)
            
        podtp.disconnect()

if __name__ == '__main__':
    main()