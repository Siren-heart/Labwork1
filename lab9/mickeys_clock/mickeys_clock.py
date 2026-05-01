from datetime import datetime
from math import cos, radians, sin
from pathlib import Path

import pygame


WIDTH = 800
HEIGHT = 800
CENTER = (WIDTH // 2, HEIGHT // 2)


def load_background():
    image_path = Path(__file__).resolve().parent / "mickeys_clock" / "images" / "mickeyclock.jpeg"
    image = pygame.image.load(str(image_path)).convert()
    return pygame.transform.smoothscale(image, (WIDTH, HEIGHT))


def angle_to_point(angle_degrees, length):
    adjusted = radians(angle_degrees - 90)
    x = CENTER[0] + cos(adjusted) * length
    y = CENTER[1] + sin(adjusted) * length
    return int(x), int(y)


def draw_hand(screen, angle, length, thickness, glove_radius):
    end_point = angle_to_point(angle, length)
    pygame.draw.line(screen, (10, 10, 10), CENTER, end_point, thickness)
    pygame.draw.circle(screen, (255, 255, 255), end_point, glove_radius)
    pygame.draw.circle(screen, (30, 30, 30), end_point, glove_radius, 2)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mickey's Clock")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 28, bold=True)
    background = load_background()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        now = datetime.now()
        minute_angle = now.minute * 6
        second_angle = now.second * 6

        screen.blit(background, (0, 0))
        pygame.draw.circle(screen, (20, 20, 20), CENTER, 16)

        # Left hand = seconds, right hand = minutes.
        draw_hand(screen, second_angle, 215, 10, 20)
        draw_hand(screen, minute_angle, 185, 12, 22)

        time_text = font.render(now.strftime("%M:%S"), True, (20, 20, 20))
        text_rect = time_text.get_rect(center=(CENTER[0], HEIGHT - 40))
        screen.blit(time_text, text_rect)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
