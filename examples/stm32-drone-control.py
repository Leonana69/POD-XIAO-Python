import json
from podtp import Podtp, print_t
import pygame
import sys, time

def control(podtp: Podtp):
    podtp.start_stream()
    # podtp.reset_estimator()
    # Initialize Pygame
    pygame.init()
    clock = pygame.time.Clock()

    # save depth and state data
    depth_data = open('cache/depth.txt', 'w')
    state_data = open('cache/state.txt', 'w')

    # Set up the display
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption('Drone Control')
    running = True
    SPEED = 0.8
    vx = 0
    vy = 0
    vr = 0
    vz = 0
    height = 0.5
    last_command_time = 0

    counter = 0
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_w:
                    vx = SPEED
                elif event.key == pygame.K_s:
                    vx = -SPEED
                elif event.key == pygame.K_a:
                    vy = SPEED
                elif event.key == pygame.K_d:
                    vy = -SPEED
                elif event.key == pygame.K_q:
                    vr = 30
                elif event.key == pygame.K_e:
                    vr = -30
                elif event.key == pygame.K_SPACE:
                    vz = 0.2
                elif event.key == pygame.K_LSHIFT:
                    vz = -0.2
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    vx = 0
                elif event.key == pygame.K_s:
                    vx = 0
                elif event.key == pygame.K_a:
                    vy = 0
                elif event.key == pygame.K_d:
                    vy = 0
                elif event.key == pygame.K_q:
                    vr = 0
                elif event.key == pygame.K_e:
                    vr = 0
                elif event.key == pygame.K_SPACE:
                    vz = 0
                elif event.key == pygame.K_LSHIFT:
                    vz = 0
        # if vx == 0 and vy == 0 and vr == 0:
        #     pass
        # else:
        #     print_t(f'vx: {vx} vy: {vy} vr: {vr}')

        
        dt = pygame.time.get_ticks() - last_command_time
        if dt > 200:
            if vz != 0:
                height += vz * dt / 1000
            podtp.send_command_hover(height, vx, vy, vr)
            # podtp.send_command_setpoint(0, 0, 0, 0)
            last_command_time = pygame.time.get_ticks()
        print(podtp.sensor_data.state.timestamp, podtp.sensor_data.state.data)
        print(podtp.sensor_data.depth.timestamp, podtp.sensor_data.depth.data)
        depth_data.write(f'{podtp.sensor_data.depth.timestamp}: {podtp.sensor_data.depth.data}\n\n')
        state_data.write(f'{podtp.sensor_data.state.timestamp}: {podtp.sensor_data.state.data}\n\n')
        # You can update your game logic and draw here
        # For this example, we'll just fill the screen with black
        # screen.fill((0, 0, 0))
        image_surface = pygame.surfarray.make_surface(podtp.sensor_data.frame.transpose(1, 0, 2))
        # save the image
        pygame.image.save(image_surface, f'cache/image/{podtp.sensor_data.state.timestamp}.png')
        counter += 1

        screen.blit(image_surface, (0, 0))
        pygame.display.flip()
        clock.tick(10)

    count = 0
    while count < 10:
        # print_t(f'Sending setpoint {count}')
        # podtp.send_command_velocity(0, 0, -0.3, 0)
        podtp.send_command_setpoint(0, 0, 0, 11000)
        time.sleep(0.2)
        count += 1
    # Quit Pygame
    pygame.quit()
    sys.exit()

def main():
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
    
    podtp = Podtp(config)
    if podtp.connect():
        if not podtp.send_ctrl_lock(False):
            print_t('Failed to unlock control')
        else:
            print_t('Drone unlocked')
            control(podtp)
            
        podtp.disconnect()

if __name__ == '__main__':
    main()