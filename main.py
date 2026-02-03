import pygame, sys, ghosts


def main():
    # 1. Initialize Pygame
    pygame.init()

    # 2. Setup the Window
    screen_width, screen_height = 600, 400
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pac-Man Ghost Test")
    clock = pygame.time.Clock()

    # 3. Create Ghost Instance (Blinky!)
    blinky = ghosts.Ghost(285, 185, (255, 0, 0), 'test')  # Red ghost in the center

    # 4. The Game Loop
    running = True
    while running:
        # Check for exit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill background with black (classic Pac-Man style)
        screen.fill((0, 0, 0))

        # 5. Draw the Ghost
        blinky.draw(screen)

        # Update the display
        pygame.display.flip()

        # Limit to 60 frames per second
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
