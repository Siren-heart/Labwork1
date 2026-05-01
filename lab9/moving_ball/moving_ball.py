import pygame


WIDTH = 800
HEIGHT = 600
RADIUS = 25
STEP = 20


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Moving Ball")
    clock = pygame.time.Clock()

    x = WIDTH // 2
    y = HEIGHT // 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x - STEP >= RADIUS:
                    x -= STEP
                elif event.key == pygame.K_RIGHT and x + STEP <= WIDTH - RADIUS:
                    x += STEP
                elif event.key == pygame.K_UP and y - STEP >= RADIUS:
                    y -= STEP
                elif event.key == pygame.K_DOWN and y + STEP <= HEIGHT - RADIUS:
                    y += STEP

        screen.fill((255, 255, 255))
        pygame.draw.circle(screen, (220, 20, 60), (x, y), RADIUS)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
