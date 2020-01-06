import pygame
# Initialize a pygame instace
pygame.init()
# Set screen size
screen = pygame.display.set_mode((400, 300))
# Parameter for this example
done = False
is_blue = True
x = 30
y = 30
# Initialize clock instance
clock = pygame.time.Clock()
# Main loop
while not done:
        # Acttions such as pressing a key or moving the mouse will generate events recorded by pygame
        for event in pygame.event.get():
                # If request to close pygame window
                if event.type == pygame.QUIT:
                        done = True
                # If event is of type KEYDOWN and the key pressed is space
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        is_blue = not is_blue
        # Move box from keyboard input
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]: y -= 3
        if pressed[pygame.K_DOWN]: y += 3
        if pressed[pygame.K_LEFT]: x -= 3
        if pressed[pygame.K_RIGHT]: x += 3
        # Make screen black
        screen.fill((0, 0, 0))
        if is_blue: color = (0, 128, 255)
        else: color = (255, 100, 0)
        # Draw rectangle on black screen
        pygame.draw.rect(screen, color, pygame.Rect(x, y, 60, 60))
        # Update game window
        pygame.display.flip()
        # Set game update frequency/fps
        clock.tick(60)